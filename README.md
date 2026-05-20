# sql-sushi

Companion code repository for **_Data Transformation: The Definitive Guide_** by Andrew Madson (O'Reilly, 2026).

SQL-Sushi Co. is the fictional restaurant chain that runs through every chapter of the book. The company operates 35 locations across 5 metros on three POS systems (Clover, Square, Toast), plus a delivery-platform mix. The chapters progressively build, replace, and extend a single data pipeline that transforms raw POS exports into analytics-ready tables. This repo holds the runnable code for every chapter that has it.

## How the repo is organized

Each chapter that includes runnable code has its own directory at the top level. The directory name matches the chapter number and title, lowercase with underscores:

```text
sql-sushi/
├── chapter_12_scheduling_sql_pipelines_python/
│   └── sqlsushi-pipeline-v1/        # the Python-runner pipeline
├── chapter_13_workflow_orchestration_airflow/   (coming)
│   └── sqlsushi-pipeline-v2/        # Airflow replaces the runner
├── chapter_14_sql_frameworks_dbt/   (coming)
│   └── sqlsushi-pipeline-v3/        # dbt replaces the SQL files
├── chapter_15_beyond_sql_spark/     (coming)
│   └── sqlsushi-pipeline-v4/        # Spark replaces Postgres
└── ...
```

Each chapter directory is self-contained. You can `cd` into one and run that chapter's code without thinking about anything else. The pipeline-version directories (`sqlsushi-pipeline-vN/`) let you compare the same logical pipeline across the four progressively more sophisticated implementations the book walks through.

## Chapters

| # | Title | Code |
|---|-------|------|
| 1 | Business Challenges and the State of Data Today | _no code_ |
| 2 | Specification Writing | _no code_ |
| 3 | Reproducibility | _coming_ |
| 4 | Backfilling and Reprocessing | _coming_ |
| 5 | Incremental Models | _coming_ |
| 6 | Streaming Data Transformation | _coming_ |
| 7 | Testing and Data Quality | _coming_ |
| 8 | Version Control | _no code_ |
| 9 | CI/CD for Data Pipelines | _coming_ |
| 10 | Observability and Monitoring | _coming_ |
| 11 | Scalability and Performance | _coming_ |
| 12 | Scheduling SQL Pipelines with Python | [`chapter_12_scheduling_sql_pipelines_python/`](chapter_12_scheduling_sql_pipelines_python/) |
| 13 | Workflow Orchestration with Apache Airflow | _coming_ |
| 14 | SQL Transformation Frameworks: dbt and SQLMesh | _coming_ |
| 15 | Beyond SQL: Complex Transformations with Apache Spark | _coming_ |
| 16 | Real-Time Data Transformation Patterns | _coming_ |
| 17 | End-to-End Case Study | _coming_ |
| 18 | AI-Assisted Data Engineering | _coming_ |

Each chapter's directory has its own `README.md` with the specific commands to run that chapter's code, the libraries it pins, and the outputs you should see.

## Quick start (Chapter 12)

```bash
cd chapter_12_scheduling_sql_pipelines_python/sqlsushi-pipeline-v1
cp .env.example .env
docker compose up -d

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/build_seed_data.py
python scripts/generate_data.py
python scripts/runner.py
```

Roughly 30 seconds from `git clone` to a populated `analytics.fact_sales`. See [`chapter_12_scheduling_sql_pipelines_python/sqlsushi-pipeline-v1/README.md`](chapter_12_scheduling_sql_pipelines_python/sqlsushi-pipeline-v1/README.md) for what to expect.

## Reporting errata

Found a bug, typo, or factual error in the book or the code? Please open an issue using the [Erratum template](.github/ISSUE_TEMPLATE/erratum.md). Include the chapter, page or section, and a clear description.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to suggest improvements. Pull requests that make the code more correct, more reproducible, or more aligned with current best practices are welcome.

## License

The code in this repository is MIT licensed. See [LICENSE](LICENSE). The text of *Data Transformation: The Definitive Guide* is © O'Reilly Media and is not distributed here.
