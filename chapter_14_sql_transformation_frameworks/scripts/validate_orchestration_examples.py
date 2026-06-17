"""Validate Chapter 14 orchestration pairing examples.

The main CI job runs the dbt and SQLMesh paths directly. This script keeps the
optional Airflow, Dagster, cron, and GitHub Actions examples structurally valid
without requiring CI to install every optional scheduler.
"""

from __future__ import annotations

import ast
import pathlib
import sys


CHAPTER = pathlib.Path(__file__).resolve().parents[1]
ORCH = CHAPTER / "orchestration"
FILES = {
    "airflow_dag": ORCH / "airflow_dbt" / "dags" / "sql_sushi_dbt_dag.py",
    "dagster_defs": (
        ORCH
        / "dagster_sqlmesh"
        / "src"
        / "sql_sushi_sqlmesh_dagster"
        / "definitions.py"
    ),
    "cron": ORCH / "sqlmesh_cron" / "sql_sushi_sqlmesh.cron.example",
    "github_actions": ORCH / "sqlmesh_github_actions" / "sqlmesh_chapter14.yml",
}


def _read(path: pathlib.Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing expected file: {path}")
    return path.read_text(encoding="utf-8")


def _parse_python(path: pathlib.Path) -> None:
    ast.parse(_read(path), filename=str(path))


def main() -> int:
    errors: list[str] = []
    for key in ["airflow_dag", "dagster_defs"]:
        try:
            _parse_python(FILES[key])
        except Exception as exc:
            errors.append(f"{FILES[key]}: {exc}")

    required_text = {
        "airflow_dag": [
            "from airflow.sdk import DAG",
            "BashOperator",
            "sql_sushi_chapter_14_dbt",
            "run_dbt_path.py",
        ],
        "dagster_defs": [
            "import dagster as dg",
            "@dg.op",
            "@dg.job",
            "dg.ScheduleDefinition",
            "dg.Definitions",
            "run_sqlmesh_path.py",
        ],
        "cron": ["run_sqlmesh_path.py", "15 2 * * *"],
        "github_actions": [
            "workflow_dispatch:",
            "schedule:",
            "actions/checkout@v6",
            "run_sqlmesh_path.py",
        ],
    }
    for key, required_items in required_text.items():
        try:
            text = _read(FILES[key])
        except Exception as exc:
            errors.append(str(exc))
            continue
        for item in required_items:
            if item not in text:
                errors.append(f"{FILES[key]}: missing {item!r}")

    if errors:
        print("Chapter 14 orchestration example validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Chapter 14 orchestration examples verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
