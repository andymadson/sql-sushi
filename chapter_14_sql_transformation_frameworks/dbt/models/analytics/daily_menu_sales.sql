WITH daily AS (
    SELECT
        CAST(f.transaction_ts AS DATE) AS sales_date,
        f.location_id,
        f.master_item_id,
        COUNT(*) AS line_items,
        COUNT(DISTINCT f.transaction_ts) AS approx_orders,
        SUM(f.quantity) AS units_sold,
        CAST(SUM(f.amount) AS DECIMAL(12, 2)) AS gross_sales,
        CAST(0.00 AS DECIMAL(12, 2)) AS discount_amount,
        CAST(SUM(f.amount) AS DECIMAL(12, 2)) AS net_sales,
        COUNT(DISTINCT f.source_pos) AS source_system_count
    FROM {{ ref('fact_sales') }} AS f
    GROUP BY
        CAST(f.transaction_ts AS DATE),
        f.location_id,
        f.master_item_id
)
SELECT
    d.sales_date,
    d.location_id,
    l.location_name,
    l.metro,
    d.master_item_id,
    mi.category AS menu_category,
    mi.base_price_usd,
    d.line_items,
    d.approx_orders,
    d.units_sold,
    d.gross_sales,
    d.discount_amount,
    d.net_sales,
    d.source_system_count
FROM daily AS d
INNER JOIN {{ source('raw', 'locations') }} AS l
    ON l.location_id = d.location_id
INNER JOIN {{ source('raw', 'master_items') }} AS mi
    ON mi.master_item_id = d.master_item_id
ORDER BY d.sales_date, d.location_id, d.master_item_id
