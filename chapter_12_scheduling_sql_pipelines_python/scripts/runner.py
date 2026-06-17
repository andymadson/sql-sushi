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
import re
import sys
import time
import uuid
from datetime import datetime, timezone

import duckdb

from db import connect
from steps import STEPS, Step

logger = logging.getLogger("runner")
BOOTSTRAP_STEP_NAMES = ("create_schemas", "pipeline_metadata_ddl")
DROP_TABLE_RE = re.compile(
    r"^\s*DROP\s+TABLE\s+IF\s+EXISTS\s+"
    r"([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)\s*;",
    re.IGNORECASE | re.MULTILINE,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _record_pipeline_start(conn: duckdb.DuckDBPyConnection, run_id: str) -> None:
    conn.execute(
        """
        INSERT INTO pipeline.pipeline_runs (run_id, started_at, status)
        VALUES (?, ?, 'running')
        """,
        [run_id, _utcnow()],
    )


def _record_pipeline_end(
    conn: duckdb.DuckDBPyConnection,
    run_id: str,
    status: str,
    error_text: str | None = None,
) -> None:
    conn.execute(
        """
        UPDATE pipeline.pipeline_runs
           SET completed_at = ?,
               status       = ?,
               error_text   = ?
         WHERE run_id = ?
        """,
        [_utcnow(), status, error_text, run_id],
    )


def _record_step_start(
    conn: duckdb.DuckDBPyConnection, run_id: str, step: Step, order_index: int
) -> None:
    conn.execute(
        """
        INSERT INTO pipeline.step_runs
            (run_id, step_name, step_order, started_at, status)
        VALUES (?, ?, ?, ?, 'running')
        """,
        [run_id, step.name, order_index, _utcnow()],
    )


def _record_step_end(
    conn: duckdb.DuckDBPyConnection,
    run_id: str,
    step: Step,
    status: str,
    rows_affected: int | None,
    error_text: str | None,
) -> None:
    conn.execute(
        """
        UPDATE pipeline.step_runs
           SET completed_at  = ?,
               status        = ?,
               rows_affected = ?,
               error_text    = ?
         WHERE run_id = ?
           AND step_name = ?
        """,
        [_utcnow(), status, rows_affected, error_text, run_id, step.name],
    )


def _relation_count(conn: duckdb.DuckDBPyConnection, relation: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {relation}").fetchone()[0])


def _in_transaction(conn: duckdb.DuckDBPyConnection, step: Step) -> int | None:
    conn.execute("BEGIN")
    try:
        if step.sql_file is not None:
            rows = _execute_sql_step(conn, step)
        else:
            rows = _execute_python_step(conn, step)
    except Exception:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")
    return rows


def _execute_sql_step(conn: duckdb.DuckDBPyConnection, step: Step) -> int | None:
    """Execute a SQL file and return the target row count when configured."""
    assert step.sql_file is not None
    sql_text = step.sql_file.read_text(encoding="utf-8")
    _drop_conflicting_views(conn, sql_text)
    conn.execute(sql_text)
    if step.row_count_relation:
        return _relation_count(conn, step.row_count_relation)
    return None


def _drop_conflicting_views(conn: duckdb.DuckDBPyConnection, sql_text: str) -> None:
    """Drop same-name views before SQL files refresh their target tables."""
    for relation in DROP_TABLE_RE.findall(sql_text):
        schema_name, table_name = relation.split(".", maxsplit=1)
        existing = conn.execute(
            """
            SELECT table_type
              FROM information_schema.tables
             WHERE table_schema = ?
               AND table_name = ?
            """,
            [schema_name, table_name],
        ).fetchone()
        if existing and str(existing[0]).upper() == "VIEW":
            conn.execute(f'DROP VIEW "{schema_name}"."{table_name}"')


def _execute_python_step(conn: duckdb.DuckDBPyConnection, step: Step) -> int | None:
    """Run a Python step. The callable returns a mapping of table to row
    count; we record the sum as a coarse 'rows touched' signal."""
    assert step.python_callable is not None
    result = step.python_callable(conn) or {}
    return sum(result.values()) if result else None


def _bootstrap_metadata(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the schema and metadata tables before recording the run."""
    steps_by_name = {step.name: step for step in STEPS}
    for name in BOOTSTRAP_STEP_NAMES:
        step = steps_by_name[name]
        _in_transaction(conn, step)


def run_pipeline() -> int:
    run_id = uuid.uuid4().hex[:12]
    logger.info("pipeline run %s starting", run_id)

    pipeline_failed = False
    pipeline_error: str | None = None

    conn = connect()
    try:
        _bootstrap_metadata(conn)
        _record_pipeline_start(conn, run_id)

        for order_index, step in enumerate(STEPS, start=1):
            _record_step_start(conn, run_id, step, order_index)

            t0 = time.perf_counter()
            try:
                rows = _in_transaction(conn, step)
            except Exception as exc:
                elapsed = time.perf_counter() - t0
                logger.exception("step %s failed after %.2fs", step.name, elapsed)
                _record_step_end(
                    conn, run_id, step,
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
            _record_step_end(
                conn, run_id, step,
                status="success",
                rows_affected=rows,
                error_text=None,
            )

        _record_pipeline_end(
            conn, run_id,
            status="failed" if pipeline_failed else "success",
            error_text=pipeline_error,
        )
    finally:
        conn.close()

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
