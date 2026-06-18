from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import dagster as dg


REPO_ROOT = Path(
    os.environ.get("SQL_SUSHI_REPO_ROOT", Path(__file__).resolve().parents[5])
).resolve()
SQLMESH_RUNNER = (
    REPO_ROOT
    / "chapter_14_sql_transformation_frameworks"
    / "scripts"
    / "run_sqlmesh_path.py"
)


@dg.op
def run_sqlmesh_path(context: dg.OpExecutionContext) -> None:
    command = [sys.executable, str(SQLMESH_RUNNER)]
    context.log.info("Running %s", " ".join(command))
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"SQLMesh path failed with exit code {result.returncode}")


@dg.job
def sql_sushi_chapter_14_sqlmesh_job() -> None:
    run_sqlmesh_path()


sql_sushi_chapter_14_sqlmesh_daily_schedule = dg.ScheduleDefinition(
    name="sql_sushi_chapter_14_sqlmesh_daily_schedule",
    cron_schedule="15 2 * * *",
    job=sql_sushi_chapter_14_sqlmesh_job,
)


defs = dg.Definitions(
    jobs=[sql_sushi_chapter_14_sqlmesh_job],
    schedules=[sql_sushi_chapter_14_sqlmesh_daily_schedule],
)


def main() -> int:
    result = sql_sushi_chapter_14_sqlmesh_job.execute_in_process()
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
