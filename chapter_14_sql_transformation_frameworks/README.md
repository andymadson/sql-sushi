# Chapter 14: SQL-Based Transformation Frameworks

Chapter 12 built the SQL-Sushi transformations with ordered SQL files and a small Python runner. Chapter 14 rebuilds the same transformed tables with dbt Core and SQLMesh so readers can compare framework behavior without changing the data or the business question.

dbt Core and SQLMesh are either/or framework choices. Do not run both in the same production transformation project. This chapter keeps both local projects side by side only for comparison.

Both frameworks read the same DuckDB database created by Chapter 12 data-loading code:

- `raw.master_items`
- `raw.locations`
- `raw.clover_transactions`
- `raw.square_transactions`
- `raw.toast_transactions`

Both frameworks produce the same Chapter 12 targets:

- `staging.stg_pos_transactions`
- `analytics.fact_sales`
- `analytics.daily_menu_sales`
- `analytics.agg_daily_sales_by_location`
- `analytics.agg_top_items_30d`

## What's Here

```text
chapter_14_sql_transformation_frameworks/
|-- README.md
|-- requirements.txt
|-- dbt/
|   |-- dbt_project.yml
|   |-- profiles.yml
|   |-- macros/
|   |   `-- generate_schema_name.sql
|   |-- models/
|       |-- sources.yml
|       |-- staging/
|       |   `-- stg_pos_transactions.sql
|       `-- analytics/
|           |-- fact_sales.sql
|           |-- daily_menu_sales.sql
|           |-- agg_daily_sales_by_location.sql
|           `-- agg_top_items_30d.sql
|   `-- tests/
|       `-- assert_daily_menu_sales_unique.sql
|-- sqlmesh/
|   |-- config.yaml
|   `-- models/
|       |-- staging/
|       |   `-- stg_pos_transactions.sql
|       `-- analytics/
|           |-- fact_sales.sql
|           |-- daily_menu_sales.sql
|           |-- agg_daily_sales_by_location.sql
|           `-- agg_top_items_30d.sql
|-- orchestration/
|   |-- README.md
|   |-- airflow_dbt/
|   |-- dagster_sqlmesh/
|   |-- sqlmesh_cron/
|   `-- sqlmesh_github_actions/
`-- scripts/
    |-- prepare_raw_data.py
    |-- run_dbt_path.py
    |-- run_sqlmesh_path.py
    |-- validate_orchestration_examples.py
    `-- verify_framework_counts.py
```

## Quick Start

Run these commands from the repo root.

Mac/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_14_sql_transformation_frameworks/requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install `
  -r requirements-dev.txt `
  -r chapter_12_scheduling_sql_pipelines_python\requirements.txt `
  -r chapter_14_sql_transformation_frameworks\requirements.txt
```

## Run the dbt Version

This path demonstrates dbt Core as the operating framework.

Mac/Linux:

```bash
.venv/bin/python \
  chapter_14_sql_transformation_frameworks/scripts/run_dbt_path.py
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe `
  chapter_14_sql_transformation_frameworks\scripts\run_dbt_path.py
```

## Run the SQLMesh Version

This path demonstrates SQLMesh as the operating framework. Prepare raw data again so SQLMesh starts from the same baseline, separate from the dbt demonstration.

Mac/Linux:

```bash
.venv/bin/python \
  chapter_14_sql_transformation_frameworks/scripts/run_sqlmesh_path.py
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe `
  chapter_14_sql_transformation_frameworks\scripts\run_sqlmesh_path.py
```

## Orchestration Pairings

The `orchestration/` folder shows four ways teams commonly operate these framework choices:

| Pairing | Use when | Tradeoff |
|---|---|---|
| Airflow plus dbt Core | The team chooses dbt and already operates Airflow or needs DAG scheduling and task history. | Strong orchestration surface, more services to operate. |
| SQLMesh plus Dagster | The team chooses SQLMesh and wants Python-native jobs, schedules, and a local UI. | Richer orchestration than cron, more project structure. |
| SQLMesh plus cron | The team chooses SQLMesh and wants the smallest reliable scheduler. | Simple and robust, but limited run UI and backfill ergonomics. |
| SQLMesh plus GitHub Actions | The team chooses SQLMesh and wants repo-native validation or scheduled automation. | Easy for repository workflows, not a full data orchestrator. |

These are alternatives. Do not run dbt and SQLMesh together as a single production transformation layer.

## What to Compare

The point is not that one framework writes better SQL. The SQL is intentionally close in both versions.

The useful comparison is the operating surface:

- dbt Core makes the project shape familiar: sources, refs, model folders, model tests, and `dbt run`.
- SQLMesh makes model state and environments the center of the workflow.
- Both can build the same DuckDB tables.
- Both rebuild `analytics.daily_menu_sales`, the Chapter 2 daily location-and-menu-item contract, before building the downstream summaries.
- Neither changes the data contract by itself. The verifier still decides whether the output is acceptable.

Chapter 17 uses SQLMesh as the main path because the final case study needs stronger state and environment semantics. Chapter 14 shows that choice as a tradeoff, not a slogan.
