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
    CAST(f.transaction_ts AS DATE)       AS sales_date,
    COUNT(*)                            AS line_items,
    COUNT(DISTINCT f.transaction_ts)    AS approx_orders,
    SUM(f.quantity)                     AS units_sold,
    CAST(SUM(f.amount) AS DECIMAL(12,2)) AS revenue
FROM analytics.fact_sales AS f
GROUP BY
    f.location_id,
    CAST(f.transaction_ts AS DATE)
ORDER BY sales_date, location_id;

CREATE UNIQUE INDEX ux_agg_daily_sales_by_location_key
    ON analytics.agg_daily_sales_by_location (location_id, sales_date);
