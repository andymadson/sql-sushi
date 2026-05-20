# sqlsushi-pipeline-v1

The companion code for Chapter 12 of *Data Transformation: The Definitive Guide*.

A small SQL pipeline that loads three POS systems into a unified `fact_sales`
table, runs two aggregate models on top, and records what happened in a
`pipeline` metadata schema. Everything runs in Postgres 17 against synthetic
data on your laptop.

## What's in the box

```
sqlsushi-pipeline-v1/
├── docker-compose.yml         # Postgres 17.10 in a container
├── requirements.txt           # psycopg[binary]==3.3.4
├── .env.example               # copy to .env, fill in
├── data/                      # synthetic CSVs land here
├── scripts/
│   ├── build_seed_data.py     # 30 menu items, 6 locations
│   ├── generate_data.py       # one month of transactions, seed=42
│   ├── db.py                  # connection helper
│   ├── load_raw.py            # CSV -> raw.* via COPY
│   ├── steps.py               # ordered list of pipeline steps
│   └── runner.py              # the main entry point
└── sql/
    ├── 00_create_schemas.sql
    ├── 10_raw_ddl.sql
    ├── 30_pipeline_metadata.sql
    ├── staging/
    │   └── stg_pos_transactions.sql
    └── analytics/
        ├── fact_sales.sql
        ├── agg_daily_sales_by_location.sql
        └── agg_top_items_30d.sql
```

## Quick start

```bash
cp .env.example .env

docker compose up -d
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/build_seed_data.py
python scripts/generate_data.py
python scripts/runner.py
```

Expected outputs from a clean seeded run:

- `data/clover_transactions.csv`: 18,904 rows
- `data/square_transactions.csv`: 18,211 rows
- `data/toast_transactions.csv`:  18,541 rows
- `staging.stg_pos_transactions`: 55,656 rows
- `analytics.fact_sales`:         55,656 rows (zero unmapped items
                                  with the canonical generator)
- `analytics.agg_daily_sales_by_location`: 180 rows (6 locations x 30 days)
- `analytics.agg_top_items_30d`:  30 rows (one per master_item_id)

## How to verify

```sql
SELECT master_item_id, units_sold, revenue, rank_by_revenue
FROM analytics.agg_top_items_30d
ORDER BY rank_by_revenue
LIMIT 5;

SELECT step_name, status, rows_affected,
       EXTRACT(EPOCH FROM (completed_at - started_at)) AS seconds
FROM pipeline.step_runs
WHERE run_id = (SELECT run_id FROM pipeline.pipeline_runs
                ORDER BY started_at DESC LIMIT 1)
ORDER BY step_order;
```
