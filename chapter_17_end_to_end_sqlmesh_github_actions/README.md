# Chapter 17: End-to-End SQLMesh plus GitHub Actions

Chapter 17 pulls the SQL-Sushi project into one operating loop:

1. Generate deterministic source data.
2. Load raw POS tables into DuckDB.
3. Apply the SQLMesh plan.
4. Verify the transformed outputs.
5. Show how the same command can run from GitHub Actions or cron.

The scheduled GitHub Actions workflow in this folder is a copyable example. It is not active in `.github/workflows/`. The repository's main CI job runs the Chapter 17 pipeline directly so the chapter stays validated without adding a new scheduled workflow to the public repo.

## What's Here

```text
chapter_17_end_to_end_sqlmesh_github_actions/
|-- README.md
|-- requirements.txt
|-- cron/
|   `-- sql_sushi_chapter17.cron.example
|-- github_actions/
|   `-- sqlmesh_chapter17.yml
|-- scripts/
|   |-- run_pipeline.py
|   |-- validate_operating_examples.py
|   `-- verify_outputs.py
`-- sqlmesh/
    |-- config.yaml
    `-- models/
        |-- staging/
        |   `-- stg_pos_transactions.sql
        `-- analytics/
            |-- fact_sales.sql
            |-- daily_menu_sales.sql
            |-- agg_daily_sales_by_location.sql
            `-- agg_top_items_30d.sql
```

The SQLMesh project builds the same five transformed targets introduced earlier:

- `staging.stg_pos_transactions`
- `analytics.fact_sales`
- `analytics.daily_menu_sales`
- `analytics.agg_daily_sales_by_location`
- `analytics.agg_top_items_30d`

Chapter 17 writes its DuckDB database to:

```text
chapter_17_end_to_end_sqlmesh_github_actions/data/sqlsushi_end_to_end.duckdb
```

That keeps the final case study independent from the Chapter 14 dbt and SQLMesh comparison.

## Quick Start

Run these commands from the repo root.

Mac/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_17_end_to_end_sqlmesh_github_actions/requirements.txt
.venv/bin/python chapter_17_end_to_end_sqlmesh_github_actions/scripts/run_pipeline.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install `
  -r requirements-dev.txt `
  -r chapter_12_scheduling_sql_pipelines_python\requirements.txt `
  -r chapter_17_end_to_end_sqlmesh_github_actions\requirements.txt
.\.venv\Scripts\python.exe chapter_17_end_to_end_sqlmesh_github_actions\scripts\run_pipeline.py
```

The runner prepares raw data, applies the SQLMesh plan, and runs the verifier. It exits nonzero if any step fails.

## Expected Output

The verifier checks the Chapter 12 row-count contract:

| Relation | Rows |
|---|---:|
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

It also checks that `analytics.fact_sales` has no duplicate `transaction_id` groups, that `analytics.daily_menu_sales` is unique at `(sales_date, location_id, master_item_id)`, and that the daily menu sales key and label fields are populated.

## GitHub Actions Example

The copyable workflow lives at:

```text
chapter_17_end_to_end_sqlmesh_github_actions/github_actions/sqlmesh_chapter17.yml
```

Copy it into `.github/workflows/` only if you want a real scheduled workflow in your own repository. The example supports manual dispatch and a daily UTC schedule.

## cron Fallback

The cron example lives at:

```text
chapter_17_end_to_end_sqlmesh_github_actions/cron/sql_sushi_chapter17.cron.example
```

Use cron when a small server checkout is enough and you don't need repository-hosted run history. cron wakes up the command. SQLMesh still owns the model plan, and the verifier still decides whether the output is acceptable.

## Validate the Operating Examples

Run this check after editing the GitHub Actions or cron examples:

Mac/Linux:

```bash
.venv/bin/python chapter_17_end_to_end_sqlmesh_github_actions/scripts/validate_operating_examples.py
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe chapter_17_end_to_end_sqlmesh_github_actions\scripts\validate_operating_examples.py
```

The check confirms the workflow and cron files still call the Chapter 17 pipeline and that no active `.github/workflows/sqlmesh_chapter17.yml` file has been added by accident.
