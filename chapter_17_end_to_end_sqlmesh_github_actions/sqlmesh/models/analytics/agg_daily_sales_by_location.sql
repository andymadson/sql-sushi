MODEL (
  name analytics.agg_daily_sales_by_location,
  kind FULL,
  grain (location_id, sales_date),
);

SELECT
  f.location_id,
  CAST(f.transaction_ts AS DATE) AS sales_date,
  COUNT(*) AS line_items,
  COUNT(DISTINCT f.transaction_ts) AS approx_orders,
  SUM(f.quantity) AS units_sold,
  CAST(SUM(f.amount) AS DECIMAL(12, 2)) AS revenue
FROM analytics.fact_sales AS f
GROUP BY
  f.location_id,
  CAST(f.transaction_ts AS DATE)
ORDER BY sales_date, location_id
