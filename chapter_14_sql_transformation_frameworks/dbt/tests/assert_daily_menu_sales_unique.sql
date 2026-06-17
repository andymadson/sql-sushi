SELECT
    sales_date,
    location_id,
    master_item_id,
    COUNT(*) AS row_count
FROM {{ ref('daily_menu_sales') }}
GROUP BY sales_date, location_id, master_item_id
HAVING COUNT(*) > 1
