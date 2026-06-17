# Chapter 14: SQL-Based Transformation Frameworks

Chapter 12 built the SQL-Sushi transformations with ordered SQL files and a small Python runner. Chapter 14 rebuilds the same transformed tables with dbt Core and SQLMesh so readers can compare framework behavior without changing the data or the business question.

Both frameworks read the same DuckDB database created by Chapter 12 data-loading code:

- `raw.master_items`
- `raw.locations`
- `raw.clover_transactions`
- `raw.square_transactions`
- `raw.toast_transactions`

Both frameworks produce the same Chapter 12 targets:

- `staging.stg_pos_transactions`
- `analytics.fact_sales`
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
|   `-- models/
|       |-- sources.yml
|       |-- staging/
|       |   `-- stg_pos_transactions.sql
|       `-- analytics/
|           |-- fact_sales.sql
|           |-- agg_daily_sales_by_location.sql
|           `-- agg_top_items_30d.sql
|-- sqlmesh/
|   |-- config.yaml
|   `-- models/
|       |-- staging/
|       |   `-- stg_pos_transactions.sql
|       `-- analytics/
|           |-- fact_sales.sql
|           |-- agg_daily_sales_by_location.sql
|           `-- agg_top_items_30d.sql
`-- scripts/
    |-- prepare_raw_data.py
    `-- verify_framework_counts.py
```

## Quick Start

Run these commands from the repo root.

Mac/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt -r chapter_12_scheduling_sql_pipelines_python/requirements.txt -r chapter_14_sql_transformation_frameworks/requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -r chapter_12_scheduling_sql_pipelines_python\requirements.txt -r chapter_14_sql_transformation_frameworks\requirements.txt
```

## Run the dbt Version

Mac/Linux:

```bash
.venv/bin/python chapter_14_sql_transformation_frameworks/scripts/prepare_raw_data.py
.venv/bin/dbt run --project-dir chapter_14_sql_transformation_frameworks/dbt --profiles-dir chapter_14_sql_transformation_frameworks/dbt
.venv/bin/dbt test --project-dir chapter_14_sql_transformation_frameworks/dbt --profiles-dir chapter_14_sql_transformation_frameworks/dbt
.venv/bin/python chapter_14_sql_transformation_frameworks/scripts/verify_framework_counts.py --label dbt
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe chapter_14_sql_transformation_frameworks\scripts\prepare_raw_data.py
.\.venv\Scripts\dbt.exe run --project-dir chapter_14_sql_transformation_frameworks\dbt --profiles-dir chapter_14_sql_transformation_frameworks\dbt
.\.venv\Scripts\dbt.exe test --project-dir chapter_14_sql_transformation_frameworks\dbt --profiles-dir chapter_14_sql_transformation_frameworks\dbt
.\.venv\Scripts\python.exe chapter_14_sql_transformation_frameworks\scripts\verify_framework_counts.py --label dbt
```

## Run the SQLMesh Version

Prepare raw data again so SQLMesh starts from the same baseline.

Mac/Linux:

```bash
.venv/bin/python chapter_14_sql_transformation_frameworks/scripts/prepare_raw_data.py
.venv/bin/sqlmesh -p chapter_14_sql_transformation_frameworks/sqlmesh plan --auto-apply --no-prompts
.venv/bin/python chapter_14_sql_transformation_frameworks/scripts/verify_framework_counts.py --label sqlmesh
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe chapter_14_sql_transformation_frameworks\scripts\prepare_raw_data.py
.\.venv\Scripts\sqlmesh.exe -p chapter_14_sql_transformation_frameworks\sqlmesh plan --auto-apply --no-prompts
.\.venv\Scripts\python.exe chapter_14_sql_transformation_frameworks\scripts\verify_framework_counts.py --label sqlmesh
```

## What to Compare

The point is not that one framework writes better SQL. The SQL is intentionally close in both versions.

The useful comparison is the operating surface:

- dbt Core makes the project shape familiar: sources, refs, model folders, and `dbt run`.
- SQLMesh makes model state and environments the center of the workflow.
- Both can build the same DuckDB tables.
- Neither changes the data contract by itself. The verifier still decides whether the output is acceptable.

Chapter 17 uses SQLMesh as the main path because the final case study needs stronger state and environment semantics. Chapter 14 shows that choice as a tradeoff, not a slogan.
