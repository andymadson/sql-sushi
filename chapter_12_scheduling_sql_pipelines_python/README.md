# Chapter 12: Scheduling SQL Pipelines with Python

This directory holds the companion code for Chapter 12.

## What's here

- [`sqlsushi-pipeline-v1/`](sqlsushi-pipeline-v1/) — the full pipeline the chapter walks through. A four-schema Postgres warehouse, three POS sources (Clover, Square, Toast) unified into one staging model, two analytics aggregates, and a Python runner that records what happened in a `pipeline` metadata schema.

## Running it

See [`sqlsushi-pipeline-v1/README.md`](sqlsushi-pipeline-v1/README.md) for the full setup. The short version:

```bash
cd sqlsushi-pipeline-v1
cp .env.example .env
docker compose up -d

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/build_seed_data.py
python scripts/generate_data.py
python scripts/runner.py
```

## Expected outputs

A clean seeded run with `seed=42` produces:

- `data/clover_transactions.csv`: 18,904 rows
- `data/square_transactions.csv`: 18,211 rows
- `data/toast_transactions.csv`: 18,541 rows
- `staging.stg_pos_transactions`: 55,656 rows
- `analytics.fact_sales`: 55,656 rows
- `analytics.agg_daily_sales_by_location`: 180 rows (6 locations × 30 days)
- `analytics.agg_top_items_30d`: 30 rows

If you see different numbers, something diverged. The most likely culprits are the seed or the date range; the chapter explains why those two pin every downstream count.

## Versions this code was validated against

- Postgres `17.10`
- Python `3.12`
- `psycopg[binary]==3.3.4`

If you bump any of these, run the pipeline end to end and confirm the row counts above before trusting the result.
