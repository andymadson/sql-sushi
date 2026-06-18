# sql-sushi

Companion code repository for **_Data Transformation: The Definitive Guide_** by Andrew Madson (O'Reilly, 2026).

SQL-Sushi Co. is the fictional restaurant chain that runs through the book. The company operates multiple restaurant locations across several metros and receives POS exports from Clover, Square, and Toast. The runnable chapters progressively transform those raw exports into analytics-ready tables.

## How the Repo Is Organized

Each runnable chapter has one top-level directory. The folder names below are the contract names for Chapters 12 through 17:

```text
sql-sushi/
|-- chapter_12_scheduling_sql_pipelines_python/
|-- chapter_13_workflow_orchestration/
|-- chapter_14_sql_transformation_frameworks/
|-- chapter_15_beyond_sql_spark/
|-- chapter_16_real_time_data_transformation/
`-- chapter_17_end_to_end_sqlmesh_github_actions/
```

Each chapter directory is self-contained: it has its own README, pinned runtime dependencies, source code or SQL, data generation steps or documented data dependencies, verification commands, and expected outputs.

## Chapters

| # | Title | Code |
|---|-------|------|
| 1 | Business Challenges and the State of Data Today | _conceptual, no repo code_ |
| 2 | Drafting Design Documents | _conceptual, no repo code_ |
| 3 | Reproducibility | _conceptual, no repo code_ |
| 4 | Backfilling and Reprocessing | _conceptual, no repo code_ |
| 5 | Incremental Models | _conceptual, no repo code_ |
| 6 | Streaming Data Transformation | _conceptual, no repo code_ |
| 7 | Testing and Data Quality | _conceptual, no repo code_ |
| 8 | Version Control for Data Transformation | _conceptual, no repo code_ |
| 9 | CI/CD for Data Transformation Pipelines | _conceptual, no repo code_ |
| 10 | Observability and Monitoring | _conceptual, no repo code_ |
| 11 | Scalability and Performance | _conceptual, no repo code_ |
| 12 | Scheduling SQL Pipelines with Python | [`chapter_12_scheduling_sql_pipelines_python/`](chapter_12_scheduling_sql_pipelines_python/) |
| 13 | Workflow Orchestration | [`chapter_13_workflow_orchestration/`](chapter_13_workflow_orchestration/) |
| 14 | SQL-Based Transformation Frameworks | [`chapter_14_sql_transformation_frameworks/`](chapter_14_sql_transformation_frameworks/) |
| 15 | Beyond SQL | [`chapter_15_beyond_sql_spark/`](chapter_15_beyond_sql_spark/) |
| 16 | Real-Time Data Transformation | [`chapter_16_real_time_data_transformation/`](chapter_16_real_time_data_transformation/) |
| 17 | End-to-End Case Study | [`chapter_17_end_to_end_sqlmesh_github_actions/`](chapter_17_end_to_end_sqlmesh_github_actions/) |

## Quick Start: Chapter 12

From a clean checkout:

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

Chapter 12 writes generated CSV files and `data/sqlsushi.duckdb` under `chapter_12_scheduling_sql_pipelines_python/data/`. No Docker or external database is required.

## Chapter 12 Expected Counts

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

`chapter_12_scheduling_sql_pipelines_python/expected_counts.json` is the machine-checkable source for these counts.

## Quick Start: Chapter 14

Chapter 14 uses the same Chapter 12 raw DuckDB data to demonstrate two alternative transformation frameworks: dbt Core and SQLMesh. Treat them as either/or framework choices. The repo includes both only so readers can compare how each framework rebuilds the same SQL-Sushi contract, including the Chapter 2 daily menu sales grain.

```bash
python -m pip install -r requirements-dev.txt -r chapter_12_scheduling_sql_pipelines_python/requirements.txt -r chapter_14_sql_transformation_frameworks/requirements.txt
python chapter_14_sql_transformation_frameworks/scripts/prepare_raw_data.py
dbt run --project-dir chapter_14_sql_transformation_frameworks/dbt --profiles-dir chapter_14_sql_transformation_frameworks/dbt
dbt test --project-dir chapter_14_sql_transformation_frameworks/dbt --profiles-dir chapter_14_sql_transformation_frameworks/dbt
python chapter_14_sql_transformation_frameworks/scripts/verify_framework_counts.py --label dbt
python chapter_14_sql_transformation_frameworks/scripts/prepare_raw_data.py
sqlmesh -p chapter_14_sql_transformation_frameworks/sqlmesh plan --auto-apply --no-prompts
python chapter_14_sql_transformation_frameworks/scripts/verify_framework_counts.py --label sqlmesh
```

The second `prepare_raw_data.py` call resets the local DuckDB state before the SQLMesh path. Do not run dbt and SQLMesh together against the same production target. Choose one operating framework for a real project. Chapter 14 also includes real orchestration examples for Airflow plus dbt, SQLMesh plus Dagster, SQLMesh plus cron, and SQLMesh plus GitHub Actions.

Optional dbt state note: Orchestra Labs' [`orchestra-hq/sao-paolo`](https://github.com/orchestra-hq/sao-paolo) project publishes `dbt-orchestra`, a wrapper that runs dbt Core commands through `orc dbt ...` and uses saved run state to reduce unnecessary dbt work. It is relevant to the dbt tradeoff discussion, but it is not required for this repo. The SQL-Sushi dbt exercise stays DuckDB-first for local reproducibility, and Chapter 17 uses SQLMesh because state and environments are native to SQLMesh.

## Quick Start: Chapter 15

Chapter 15 uses Spark for one focused transformation that is awkward to express as plain SQL: reconstructing baskets from POS line items and counting co-purchased item pairs.

Spark requires a local JDK. The CI workflow uses Java 17.

```bash
python -m pip install -r requirements-dev.txt -r chapter_12_scheduling_sql_pipelines_python/requirements.txt -r chapter_15_beyond_sql_spark/requirements.txt
python chapter_15_beyond_sql_spark/scripts/prepare_spark_inputs.py
python chapter_15_beyond_sql_spark/scripts/build_basket_pairs.py
python chapter_15_beyond_sql_spark/scripts/verify_basket_pairs.py
```

## Quick Start: Chapter 16

Chapter 16 uses deterministic event batch files and DuckDB to show event-time watermarks, late-event capture, idempotent file processing, and 15-minute sales aggregates without requiring a streaming service.

Mac/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_16_real_time_data_transformation/requirements.txt
.venv/bin/python chapter_16_real_time_data_transformation/scripts/prepare_event_batches.py
.venv/bin/python chapter_16_real_time_data_transformation/scripts/run_micro_batches.py --reset
.venv/bin/python chapter_16_real_time_data_transformation/scripts/run_micro_batches.py
.venv/bin/python chapter_16_real_time_data_transformation/scripts/verify_real_time_outputs.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install `
  -r requirements-dev.txt `
  -r chapter_12_scheduling_sql_pipelines_python\requirements.txt `
  -r chapter_16_real_time_data_transformation\requirements.txt
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\prepare_event_batches.py
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\run_micro_batches.py --reset
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\run_micro_batches.py
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\verify_real_time_outputs.py
```

The second micro-batch run should skip the already processed batch files. That is the idempotency check.

## Quick Start: Chapter 17

Chapter 17 runs the final SQLMesh case study from one command. It prepares the deterministic raw data, applies the SQLMesh plan, and verifies the transformed outputs. The GitHub Actions workflow in the chapter folder is a copyable example, not an active repository workflow.

Mac/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_17_end_to_end_sqlmesh_github_actions/requirements.txt
.venv/bin/python chapter_17_end_to_end_sqlmesh_github_actions/scripts/run_pipeline.py
.venv/bin/python chapter_17_end_to_end_sqlmesh_github_actions/scripts/validate_operating_examples.py
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
.\.venv\Scripts\python.exe chapter_17_end_to_end_sqlmesh_github_actions\scripts\validate_operating_examples.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to suggest improvements. Pull requests that make the code more correct, more reproducible, or more aligned with current best practices are welcome.

## License

The code in this repository is MIT licensed. See [LICENSE](LICENSE). The text of *Data Transformation: The Definitive Guide* is copyright O'Reilly Media and is not distributed here.
