# Chapter 12: Scheduling SQL Pipelines with Python

This directory holds the runnable companion code for Chapter 12. It is the canonical DuckDB-first baseline used by later chapters.

The pipeline loads deterministic SQL-Sushi CSV data into a local DuckDB database, builds one unified staging model, builds analytics tables, and records each run in a small `pipeline` metadata schema. No Docker or external database is required.

## What's Here

```text
chapter_12_scheduling_sql_pipelines_python/
|-- README.md
|-- expected_counts.json
|-- requirements.txt
|-- scripts/
|   |-- build_seed_data.py
|   |-- generate_data.py
|   |-- db.py
|   |-- load_raw.py
|   |-- steps.py
|   |-- runner.py
|   `-- verify_counts.py
`-- sql/
    |-- 00_create_schemas.sql
    |-- 10_raw_ddl.sql
    |-- 30_pipeline_metadata.sql
    |-- staging/
    |   `-- stg_pos_transactions.sql
    `-- analytics/
        |-- fact_sales.sql
        |-- daily_menu_sales.sql
        |-- agg_daily_sales_by_location.sql
        `-- agg_top_items_30d.sql
```

Generated CSV files and the DuckDB database are written to `data/` at runtime.

## Quick Start

Run these commands from the repo root.

```bash
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

```bash
. .venv/bin/activate
```

Install dependencies and run the pipeline:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt -r chapter_12_scheduling_sql_pipelines_python/requirements.txt
python chapter_12_scheduling_sql_pipelines_python/scripts/build_seed_data.py
python chapter_12_scheduling_sql_pipelines_python/scripts/generate_data.py
python chapter_12_scheduling_sql_pipelines_python/scripts/runner.py
python chapter_12_scheduling_sql_pipelines_python/scripts/verify_counts.py
```

## Expected Outputs

A clean seeded run with `seed=42` produces:

| Output | Rows |
|---|---:|
| `data/master_items.csv` | 30 |
| `data/locations.csv` | 6 |
| `data/clover_transactions.csv` | 18,904 |
| `data/square_transactions.csv` | 18,211 |
| `data/toast_transactions.csv` | 18,541 |
| `raw.master_items` | 30 |
| `raw.locations` | 6 |
| `raw.clover_transactions` | 18,904 |
| `raw.square_transactions` | 18,211 |
| `raw.toast_transactions` | 18,541 |
| `staging.stg_pos_transactions` | 55,656 |
| `analytics.fact_sales` | 55,656 |
| `analytics.daily_menu_sales` | 5,397 |
| `analytics.agg_daily_sales_by_location` | 180 |
| `analytics.agg_top_items_30d` | 30 |

`analytics.daily_menu_sales` is the Chapter 2 design-doc grain: one row per sales date, location, and standardized menu item, with location and menu metadata from the reference tables. The verifier reads `expected_counts.json` and fails non-zero if any CSV count, DuckDB relation count, or latest pipeline run status diverges.

## Validated Runtime

- Python 3.12 in CI
- DuckDB from `requirements.txt`
- SQL parsed as DuckDB through `sqlglot`
