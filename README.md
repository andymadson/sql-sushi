# sql-sushi

Companion code repository for **_Data Transformation: The Definitive Guide_** by Andrew Madson (O'Reilly, 2026).

SQL-Sushi Co. is the fictional restaurant chain that runs through the book. The company operates multiple restaurant locations across several metros and receives POS exports from Clover, Square, and Toast. The runnable chapters progressively transform those raw exports into analytics-ready tables.

## How the Repo Is Organized

Each runnable chapter has one top-level directory. The folder names below are the contract names for Chapters 12 through 17:

```text
sql-sushi/
|-- chapter_12_scheduling_sql_pipelines_python/
|-- chapter_13_workflow_orchestration/          (coming)
|-- chapter_14_sql_transformation_frameworks/   (coming)
|-- chapter_15_beyond_sql_spark/                (coming)
|-- chapter_16_real_time_data_transformation/   (coming)
`-- chapter_17_end_to_end_sqlmesh_cron/         (coming)
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
| 13 | Workflow Orchestration | _coming_ |
| 14 | SQL-Based Transformation Frameworks | _coming_ |
| 15 | Beyond SQL | _coming_ |
| 16 | Real-Time Data Transformation | _coming_ |
| 17 | End-to-End Case Study | _coming_ |

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
| `analytics.agg_daily_sales_by_location` | 180 |
| `analytics.agg_top_items_30d` | 30 |

`chapter_12_scheduling_sql_pipelines_python/expected_counts.json` is the machine-checkable source for these counts.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to suggest improvements. Pull requests that make the code more correct, more reproducible, or more aligned with current best practices are welcome.

## License

The code in this repository is MIT licensed. See [LICENSE](LICENSE). The text of *Data Transformation: The Definitive Guide* is copyright O'Reilly Media and is not distributed here.
