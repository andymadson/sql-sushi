MODEL (
  name staging.stg_pos_transactions,
  kind FULL,
  grain transaction_id,
);

WITH clover AS (
  SELECT
    c.transaction_id,
    CAST('clover' AS TEXT) AS source_pos,
    c.location_id,
    c.item_name AS source_item_name,
    mi.master_item_id,
    c.quantity,
    CAST(CAST(c.amount_cents AS DECIMAL(10, 2)) / 100 AS DECIMAL(10, 2)) AS amount,
    CAST(CAST(c.txn_date AS VARCHAR) || ' ' || CAST(c.txn_time AS VARCHAR) AS TIMESTAMP) AS transaction_ts,
    c.payment_method
  FROM raw.clover_transactions AS c
  LEFT JOIN raw.master_items AS mi
    ON mi.clover_name = c.item_name
), square AS (
  SELECT
    s.transaction_id,
    CAST('square' AS TEXT) AS source_pos,
    s.location_id,
    s.item_name AS source_item_name,
    mi.master_item_id,
    s.quantity,
    s.amount,
    s.transaction_at AS transaction_ts,
    s.payment_method
  FROM raw.square_transactions AS s
  LEFT JOIN raw.master_items AS mi
    ON mi.square_name = s.item_name
), toast AS (
  SELECT
    t.transaction_id,
    CAST('toast' AS TEXT) AS source_pos,
    t.location_id,
    t.item_name AS source_item_name,
    mi.master_item_id,
    t.quantity,
    t.amount,
    t.transaction_ts,
    t.payment_method
  FROM raw.toast_transactions AS t
  LEFT JOIN raw.master_items AS mi
    ON mi.toast_name = t.item_name
)
SELECT
  transaction_id,
  source_pos,
  location_id,
  source_item_name,
  master_item_id,
  quantity,
  amount,
  transaction_ts,
  NULLIF(TRIM(payment_method), '') AS payment_method
FROM (
  SELECT * FROM clover
  UNION ALL
  SELECT * FROM square
  UNION ALL
  SELECT * FROM toast
) AS u
ORDER BY transaction_ts, transaction_id
