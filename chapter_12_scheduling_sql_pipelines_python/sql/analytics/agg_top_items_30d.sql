-- analytics.agg_top_items_30d
--
-- Top menu items over the trailing 30 days of fact_sales, ranked by
-- revenue and by units sold.
--
-- "Trailing 30 days" is measured from the latest transaction_ts in
-- fact_sales, not from the wall-clock now(). That's deliberate. If a
-- developer reruns this against a frozen snapshot of the data three
-- months later, they should get the same answer.

DROP TABLE IF EXISTS analytics.agg_top_items_30d;

CREATE TABLE analytics.agg_top_items_30d AS
WITH window_bounds AS (
    SELECT
        MAX(transaction_ts)                          AS window_end,
        MAX(transaction_ts) - INTERVAL '30 days'     AS window_start
    FROM analytics.fact_sales
),
in_window AS (
    SELECT f.*
    FROM analytics.fact_sales AS f
    CROSS JOIN window_bounds AS w
    WHERE f.transaction_ts >  w.window_start
      AND f.transaction_ts <= w.window_end
)
SELECT
    master_item_id,
    SUM(quantity)              AS units_sold,
    CAST(SUM(amount) AS DECIMAL(12,2)) AS revenue,
    RANK() OVER (ORDER BY SUM(amount)    DESC) AS rank_by_revenue,
    RANK() OVER (ORDER BY SUM(quantity)  DESC) AS rank_by_units
FROM in_window
GROUP BY master_item_id
ORDER BY rank_by_revenue;

CREATE UNIQUE INDEX ux_agg_top_items_30d_master_item
    ON analytics.agg_top_items_30d (master_item_id);
