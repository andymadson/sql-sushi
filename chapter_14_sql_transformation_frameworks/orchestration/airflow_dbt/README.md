# Airflow Plus dbt Core

This optional Airflow project runs the Chapter 14 dbt Core implementation.

Use it when the team chooses dbt Core for transformations and wants Airflow for scheduling, retries, task history, and operator-facing visibility.

## Project Shape

```text
airflow_dbt/
|-- README.md
|-- requirements.txt
`-- dags/
    `-- sql_sushi_dbt_dag.py
```

The DAG has one task that calls:

```text
chapter_14_sql_transformation_frameworks/scripts/run_dbt_path.py
```

The dbt project stays in `chapter_14_sql_transformation_frameworks/dbt/`. Airflow owns orchestration only.

## Install

Use the official Airflow constraints file for your Python version. For Python 3.12:

```bash
python -m venv .venv-airflow-dbt
.venv-airflow-dbt/bin/python -m pip install --upgrade pip
.venv-airflow-dbt/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_14_sql_transformation_frameworks/requirements.txt \
  -r chapter_14_sql_transformation_frameworks/orchestration/airflow_dbt/requirements.txt \
  --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.2.2/constraints-3.12.txt
```

## Run a Local DAG Test

```bash
export AIRFLOW_HOME="$PWD/chapter_14_sql_transformation_frameworks/orchestration/airflow_dbt/.airflow_home"
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/chapter_14_sql_transformation_frameworks/orchestration/airflow_dbt/dags"
export SQL_SUSHI_REPO_ROOT="$PWD"
export SQL_SUSHI_PYTHON="$PWD/.venv-airflow-dbt/bin/python"
airflow db migrate
airflow dags test sql_sushi_chapter_14_dbt 2026-04-02
```

## Tradeoff

Airflow is a good fit when the team already operates Airflow or needs DAG scheduling, retries, and task history around dbt. It is extra machinery for a small local pipeline.
