-- Raw landing tables. Shapes follow each POS as the upstream system
-- delivers it, not the shape we wish it had. Cleanup happens in staging.
--
-- Each transactional table has a server-side loaded_at default so we can
-- tell when a row arrived without trusting the upstream timestamp.

CREATE TABLE IF NOT EXISTS raw.master_items (
    master_item_id   TEXT          PRIMARY KEY,
    category         TEXT          NOT NULL,
    base_price_usd   NUMERIC(10,2) NOT NULL,
    clover_name      TEXT          NOT NULL,
    square_name      TEXT          NOT NULL,
    toast_name       TEXT          NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.locations (
    location_id      INTEGER PRIMARY KEY,
    metro            TEXT    NOT NULL,
    location_name    TEXT    NOT NULL,
    pos_system       TEXT    NOT NULL
);

-- Clover keeps amounts in cents as INTEGER, and splits the timestamp
-- into a DATE and a TIME column. We preserve that here and convert
-- in staging.
CREATE TABLE IF NOT EXISTS raw.clover_transactions (
    transaction_id   TEXT        PRIMARY KEY,
    location_id      INTEGER     NOT NULL,
    item_name        TEXT        NOT NULL,
    amount_cents     INTEGER     NOT NULL,
    quantity         INTEGER     NOT NULL,
    payment_method   TEXT        NOT NULL,
    txn_date         DATE        NOT NULL,
    txn_time         TIME        NOT NULL,
    loaded_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Square uses NUMERIC dollars and a single naive TIMESTAMP. We assume
-- the timestamp is UTC and tag it on the way through staging.
CREATE TABLE IF NOT EXISTS raw.square_transactions (
    transaction_id   TEXT          PRIMARY KEY,
    location_id      INTEGER       NOT NULL,
    item_name        TEXT          NOT NULL,
    amount           NUMERIC(10,2) NOT NULL,
    quantity         INTEGER       NOT NULL,
    payment_method   TEXT          NOT NULL,
    transaction_at   TIMESTAMP     NOT NULL,
    loaded_at        TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- Toast already gives us TIMESTAMPTZ. Easiest of the three.
CREATE TABLE IF NOT EXISTS raw.toast_transactions (
    transaction_id   TEXT          PRIMARY KEY,
    location_id      INTEGER       NOT NULL,
    item_name        TEXT          NOT NULL,
    amount           NUMERIC(10,2) NOT NULL,
    quantity         INTEGER       NOT NULL,
    payment_method   TEXT          NOT NULL,
    transaction_ts   TIMESTAMPTZ   NOT NULL,
    loaded_at        TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_clover_loc_date
    ON raw.clover_transactions (location_id, txn_date);
CREATE INDEX IF NOT EXISTS ix_square_loc_ts
    ON raw.square_transactions (location_id, transaction_at);
CREATE INDEX IF NOT EXISTS ix_toast_loc_ts
    ON raw.toast_transactions (location_id, transaction_ts);
