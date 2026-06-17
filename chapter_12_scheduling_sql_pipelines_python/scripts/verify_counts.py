"""Verify deterministic Chapter 12 CSV and DuckDB row counts."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

import duckdb

from db import DATABASE

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPECTED_COUNTS = ROOT / "expected_counts.json"
RELATION_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$")


def _load_expected(path: pathlib.Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _csv_row_count(path: pathlib.Path) -> int:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        line_count = sum(1 for _ in f)
    return max(line_count - 1, 0)


def _relation_count(conn: duckdb.DuckDBPyConnection, relation: str) -> int:
    if not RELATION_RE.fullmatch(relation):
        raise ValueError(f"Unexpected relation name in manifest: {relation}")
    return int(conn.execute(f"SELECT COUNT(*) FROM {relation}").fetchone()[0])


def _record_check(
    errors: list[str], label: str, expected: int | str, actual: int | str
) -> None:
    if actual == expected:
        print(f"OK   {label}: {actual}")
        return
    message = f"{label}: expected {expected}, got {actual}"
    errors.append(message)
    print(f"FAIL {message}")


def _verify_csvs(expected: dict[str, int], errors: list[str]) -> None:
    for relative_path, expected_count in expected.items():
        actual = _csv_row_count(ROOT / relative_path)
        _record_check(errors, relative_path, expected_count, actual)


def _verify_relations(
    conn: duckdb.DuckDBPyConnection, expected: dict[str, int], errors: list[str]
) -> None:
    for relation, expected_count in expected.items():
        actual = _relation_count(conn, relation)
        _record_check(errors, relation, expected_count, actual)


def _verify_latest_pipeline_run(
    conn: duckdb.DuckDBPyConnection, expected: dict[str, int | str], errors: list[str]
) -> None:
    row = conn.execute(
        """
        SELECT run_id, status
        FROM pipeline.pipeline_runs
        ORDER BY started_at DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        errors.append("pipeline.pipeline_runs: no runs recorded")
        print("FAIL pipeline.pipeline_runs: no runs recorded")
        return

    run_id, status = row
    _record_check(
        errors,
        "pipeline.latest_run_status",
        str(expected["latest_run_status"]),
        status,
    )

    step_count = int(
        conn.execute(
            "SELECT COUNT(*) FROM pipeline.step_runs WHERE run_id = ?",
            [run_id],
        ).fetchone()[0]
    )
    _record_check(
        errors,
        "pipeline.latest_run_step_count",
        int(expected["latest_run_step_count"]),
        step_count,
    )

    failed_step_count = int(
        conn.execute(
            """
            SELECT COUNT(*)
            FROM pipeline.step_runs
            WHERE run_id = ?
              AND status <> 'success'
            """,
            [run_id],
        ).fetchone()[0]
    )
    _record_check(errors, "pipeline.latest_run_failed_steps", 0, failed_step_count)


def verify(expected_path: pathlib.Path, database_path: pathlib.Path) -> int:
    expected = _load_expected(expected_path)
    errors: list[str] = []

    _verify_csvs(expected["csv_rows"], errors)

    if not database_path.exists():
        errors.append(f"Missing DuckDB database: {database_path}")
        print(f"FAIL Missing DuckDB database: {database_path}")
    else:
        conn = duckdb.connect(str(database_path), read_only=True)
        try:
            _verify_relations(conn, expected["relations"], errors)
            _verify_latest_pipeline_run(conn, expected["pipeline"], errors)
        finally:
            conn.close()

    if errors:
        print("\nVerification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nAll expected counts verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Chapter 12 deterministic row counts."
    )
    parser.add_argument(
        "--expected",
        type=pathlib.Path,
        default=EXPECTED_COUNTS,
        help="Path to expected_counts.json.",
    )
    parser.add_argument(
        "--database",
        type=pathlib.Path,
        default=DATABASE,
        help="Path to the DuckDB database.",
    )
    args = parser.parse_args()
    return verify(args.expected, args.database)


if __name__ == "__main__":
    sys.exit(main())
