from __future__ import annotations

import os
import shlex
import sys
from datetime import datetime
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG


REPO_ROOT = Path(
    os.environ.get("SQL_SUSHI_REPO_ROOT", Path(__file__).resolve().parents[4])
).resolve()
PYTHON_BIN = os.environ.get("SQL_SUSHI_PYTHON", sys.executable)
DBT_RUNNER = REPO_ROOT / "chapter_14_sql_transformation_frameworks" / "scripts" / "run_dbt_path.py"


with DAG(
    dag_id="sql_sushi_chapter_14_dbt",
    description="Run the SQL-Sushi Chapter 14 dbt Core path.",
    start_date=datetime(2026, 4, 1),
    schedule="15 2 * * *",
    catchup=False,
    tags=["sql-sushi", "chapter-14", "dbt"],
) as dag:
    run_dbt_path = BashOperator(
        task_id="run_dbt_path",
        bash_command=f"{shlex.quote(PYTHON_BIN)} {shlex.quote(str(DBT_RUNNER))}",
        cwd=str(REPO_ROOT),
    )
