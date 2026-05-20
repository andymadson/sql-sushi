-- analytics.agg_daily_sales_by_location
--
-- Daily revenue, order count, and line-item count per location. Used by
-- the operations team's morning report.
--
-- "Order count" approximates orders by counting distinct transaction_ts
-- per location per day; the fact table's grain is the line item, and the
-- POS exports we have don't carry a real order_id. Chapter 16 adds a
-- proper order grain once the delivery-platform data lands.

DROP TABLE IF EXISTS analytics.agg_daily_sales_by_location;

CREATE TABLE analytics.agg_daily_sales_by_location AS
SELECT
    f.location_id,
    (f.transaction_ts AT TIME ZONE 'UTC')::DATE AS sales_date,
    COUNT(*)                            AS line_items,
    COUNT(DISTINCT f.transaction_ts)    AS approx_orders,
    SUM(f.quantity)                     AS units_sold,
    SUM(f.amount)::NUMERIC(12,2)        AS revenue
FROM analytics.fact_sales AS f
GROUP BY
    f.location_id,
    (f.transaction_ts AT TIME ZONE 'UTC')::DATE
ORDER BY sales_date, location_id;

ALTER TABLE analytics.agg_daily_sales_by_location
    ADD PRIMARY KEY (location_id, sales_date);
