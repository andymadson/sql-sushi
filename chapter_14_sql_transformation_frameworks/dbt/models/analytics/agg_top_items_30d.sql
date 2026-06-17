WITH window_bounds AS (
    SELECT
        MAX(transaction_ts) AS window_end,
        MAX(transaction_ts) - INTERVAL '30 days' AS window_start
    FROM {{ ref('fact_sales') }}
),
in_window AS (
    SELECT f.*
    FROM {{ ref('fact_sales') }} AS f
    CROSS JOIN window_bounds AS w
    WHERE f.transaction_ts > w.window_start
      AND f.transaction_ts <= w.window_end
)
SELECT
    master_item_id,
    SUM(quantity) AS units_sold,
    CAST(SUM(amount) AS DECIMAL(12, 2)) AS revenue,
    RANK() OVER (ORDER BY SUM(amount) DESC) AS rank_by_revenue,
    RANK() OVER (ORDER BY SUM(quantity) DESC) AS rank_by_units
FROM in_window
GROUP BY master_item_id
ORDER BY rank_by_revenue
