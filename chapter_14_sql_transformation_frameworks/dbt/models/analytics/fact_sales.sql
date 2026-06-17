SELECT
    s.transaction_id,
    s.source_pos,
    s.location_id,
    s.master_item_id,
    s.quantity,
    s.amount,
    s.transaction_ts,
    s.payment_method
FROM {{ ref('stg_pos_transactions') }} AS s
WHERE s.master_item_id IS NOT NULL
ORDER BY s.transaction_ts, s.transaction_id
