"""Run the pipeline end to end.

What this does:

  1. Read the step list from steps.py.
  2. Open one shared connection. Write a 'running' row to
     pipeline.pipeline_runs.
  3. For each step, write a 'running' row to pipeline.step_runs, execute
     the step inside its own transaction, then update the step row with
     the outcome.
  4. If a step fails, stop. Mark the pipeline run as failed and exit
     non-zero. The earlier successful steps stay committed.
  5. If every step succeeds, commit the final state and exit zero.

This is deliberately small. No DAG resolution. No retries. No parallelism.
Chapter 13 trades all of that simplicity in for a real orchestrator.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import uuid
from datetime import datetime, timezone

import psycopg

from db import connect
from steps import STEPS, Step

logger = logging.getLogger("runner")
BOOTSTRAP_STEP_NAMES = ("create_schemas", "pipeline_metadata_ddl")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _record_pipeline_start(cur: psycopg.Cursor, run_id: str) -> None:
    cur.execute(
        """
        INSERT INTO pipeline.pipeline_runs (run_id, started_at, status)
        VALUES (%s, %s, 'running')
        """,
        (run_id, _utcnow()),
    )


def _record_pipeline_end(
    cur: psycopg.Cursor, run_id: str, status: str, error_text: str | None = None
) -> None:
    cur.execute(
        """
        UPDATE pipeline.pipeline_runs
           SET completed_at = %s,
               status       = %s,
               error_text   = %s
         WHERE run_id = %s
        """,
        (_utcnow(), status, error_text, run_id),
    )


def _record_step_start(
    cur: psycopg.Cursor, run_id: str, step: Step, order_index: int
) -> None:
    cur.execute(
        """
        INSERT INTO pipeline.step_runs
            (run_id, step_name, step_order, started_at, status)
        VALUES (%s, %s, %s, %s, 'running')
        """,
        (run_id, step.name, order_index, _utcnow()),
    )


def _record_step_end(
    cur: psycopg.Cursor,
    run_id: str,
    step: Step,
    status: str,
    rows_affected: int | None,
    error_text: str | None,
) -> None:
    cur.execute(
        """
        UPDATE pipeline.step_runs
           SET completed_at  = %s,
               status        = %s,
               rows_affected = %s,
               error_text    = %s
         WHERE run_id = %s
           AND step_name = %s
        """,
        (_utcnow(), status, rows_affected, error_text, run_id, step.name),
    )


def _execute_sql_step(conn: psycopg.Connection, step: Step) -> int | None:
    """Execute a SQL file in its own transaction. Returns the rowcount of
    the last statement, which the runner uses purely as a sanity signal
    for the operator. Some statements report -1; treat that as None."""
    assert step.sql_file is not None
    sql_text = step.sql_file.read_text(encoding="utf-8")
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(sql_text)
            rowcount = cur.rowcount
    return rowcount if rowcount != -1 else None


def _execute_python_step(step: Step) -> int | None:
    """Run a Python step. The callable returns a mapping of table to row
    count; we record the sum as a coarse 'rows touched' signal."""
    assert step.python_callable is not None
    result = step.python_callable() or {}
    return sum(result.values()) if result else None


def _bootstrap_metadata(conn: psycopg.Connection) -> None:
    """Create the schema and metadata tables before recording the run."""
    steps_by_name = {step.name: step for step in STEPS}
    for name in BOOTSTRAP_STEP_NAMES:
        step = steps_by_name[name]
        _execute_sql_step(conn, step)


def run_pipeline() -> int:
    run_id = uuid.uuid4().hex[:12]
    logger.info("pipeline run %s starting", run_id)

    pipeline_failed = False
    pipeline_error: str | None = None

    with connect() as conn:
        _bootstrap_metadata(conn)
        # The bookkeeping connection commits on every metadata write so
        # the step rows survive a step failure. SQL steps run in their
        # own short transactions via conn.transaction().
        conn.autocommit = True
        with conn.cursor() as cur:
            _record_pipeline_start(cur, run_id)

        for order_index, step in enumerate(STEPS, start=1):
            with conn.cursor() as cur:
                _record_step_start(cur, run_id, step, order_index)

            t0 = time.perf_counter()
            try:
                if step.sql_file is not None:
                    rows = _execute_sql_step(conn, step)
                else:
                    rows = _execute_python_step(step)
            except Exception as exc:
                elapsed = time.perf_counter() - t0
                logger.exception("step %s failed after %.2fs", step.name, elapsed)
                with conn.cursor() as cur:
                    _record_step_end(
                        cur, run_id, step,
                        status="failed",
                        rows_affected=None,
                        error_text=str(exc),
                    )
                pipeline_failed = True
                pipeline_error = f"{step.name}: {exc}"
                break

            elapsed = time.perf_counter() - t0
            logger.info("step %s completed in %.2fs (rows=%s)",
                        step.name, elapsed, rows)
            with conn.cursor() as cur:
                _record_step_end(
                    cur, run_id, step,
                    status="success",
                    rows_affected=rows,
                    error_text=None,
                )

        with conn.cursor() as cur:
            _record_pipeline_end(
                cur, run_id,
                status="failed" if pipeline_failed else "success",
                error_text=pipeline_error,
            )

    if pipeline_failed:
        logger.error("pipeline run %s FAILED: %s", run_id, pipeline_error)
        return 1
    logger.info("pipeline run %s succeeded", run_id)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SQL-Sushi pipeline.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        return run_pipeline()
    except Exception as exc:
        logger.error("pipeline failed before metadata could be completed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
