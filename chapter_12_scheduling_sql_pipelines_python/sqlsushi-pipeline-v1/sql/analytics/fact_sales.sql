-- analytics.fact_sales
--
-- One row per real transaction line item, canonical column names and
-- types. The grain is the same as Chapter 7: keyed by transaction_id.
--
-- Rows with a NULL master_item_id are dropped here. They mean the item
-- didn't match the master_items catalog and need to be triaged before
-- they reach the analysts. The runner logs how many were dropped so the
-- team can see drift early.

DROP TABLE IF EXISTS analytics.fact_sales;

CREATE TABLE analytics.fact_sales AS
SELECT
    s.transaction_id,
    s.source_pos,
    s.location_id,
    s.master_item_id,
    s.quantity,
    s.amount,
    s.transaction_ts,
    s.payment_method
FROM staging.stg_pos_transactions AS s
WHERE s.master_item_id IS NOT NULL
ORDER BY s.transaction_ts, s.transaction_id;

ALTER TABLE analytics.fact_sales ADD PRIMARY KEY (transaction_id);

CREATE INDEX ix_fact_sales_loc_ts
    ON analytics.fact_sales (location_id, transaction_ts);
CREATE INDEX ix_fact_sales_master_item
    ON analytics.fact_sales (master_item_id);
