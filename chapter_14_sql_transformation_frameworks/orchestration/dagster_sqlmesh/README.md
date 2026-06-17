# SQLMesh Plus Dagster

This optional Dagster project runs the Chapter 14 SQLMesh implementation.

Use it when the team chooses SQLMesh for transformations and wants Dagster for job definitions, schedules, local UI, and Python-native orchestration around the SQLMesh plan workflow.

## Project Shape

```text
dagster_sqlmesh/
|-- README.md
|-- pyproject.toml
`-- src/
    `-- sql_sushi_sqlmesh_dagster/
        |-- __init__.py
        `-- definitions.py
```

The Dagster job calls:

```text
chapter_14_sql_transformation_frameworks/scripts/run_sqlmesh_path.py
```

The SQLMesh project stays in `chapter_14_sql_transformation_frameworks/sqlmesh/`. Dagster owns orchestration only.

## Install

```bash
python -m venv .venv-dagster-sqlmesh
.venv-dagster-sqlmesh/bin/python -m pip install --upgrade pip
.venv-dagster-sqlmesh/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_14_sql_transformation_frameworks/requirements.txt
.venv-dagster-sqlmesh/bin/python -m pip install -e chapter_14_sql_transformation_frameworks/orchestration/dagster_sqlmesh
```

## Run

Execute the job directly:

```bash
.venv-dagster-sqlmesh/bin/python -m sql_sushi_sqlmesh_dagster.definitions
```

Run the Dagster development UI:

```bash
.venv-dagster-sqlmesh/bin/dagster dev -m sql_sushi_sqlmesh_dagster.definitions
```

The project exposes one job, `sql_sushi_chapter_14_sqlmesh_job`, and one daily schedule, `sql_sushi_chapter_14_sqlmesh_daily_schedule`.

## Tradeoff

Dagster is useful when the team wants Python-native orchestration around SQLMesh and a richer local UI. It is more operational surface than cron or GitHub Actions.
