"""Verify dbt or SQLMesh produced the Chapter 12 transformed table counts."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

import duckdb

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_12 = ROOT / "chapter_12_scheduling_sql_pipelines_python"
EXPECTED_COUNTS = CHAPTER_12 / "expected_counts.json"
DATABASE = CHAPTER_12 / "data" / "sqlsushi.duckdb"
RELATION_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$")
REQUIRED_RELATIONS = (
    "raw.master_items",
    "raw.locations",
    "raw.clover_transactions",
    "raw.square_transactions",
    "raw.toast_transactions",
    "staging.stg_pos_transactions",
    "analytics.fact_sales",
    "analytics.agg_daily_sales_by_location",
    "analytics.agg_top_items_30d",
)


def _load_expected(path: pathlib.Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _relation_count(conn: duckdb.DuckDBPyConnection, relation: str) -> int:
    if not RELATION_RE.fullmatch(relation):
        raise ValueError(f"Unexpected relation name in manifest: {relation}")
    return int(conn.execute(f"SELECT COUNT(*) FROM {relation}").fetchone()[0])


def _record_check(
    errors: list[str], label: str, expected: int, actual: int, run_label: str
) -> None:
    prefix = f"{run_label} " if run_label else ""
    if actual == expected:
        print(f"OK   {prefix}{label}: {actual}")
        return
    message = f"{label}: expected {expected}, got {actual}"
    errors.append(message)
    print(f"FAIL {prefix}{message}")


def verify(expected_path: pathlib.Path, database_path: pathlib.Path, label: str) -> int:
    expected = _load_expected(expected_path)
    relation_counts = expected["relations"]
    errors: list[str] = []

    if not database_path.exists():
        print(f"FAIL Missing DuckDB database: {database_path}")
        return 1

    conn = duckdb.connect(str(database_path), read_only=True)
    try:
        for relation in REQUIRED_RELATIONS:
            actual = _relation_count(conn, relation)
            _record_check(errors, relation, int(relation_counts[relation]), actual, label)
    finally:
        conn.close()

    if errors:
        print("\nFramework verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nAll Chapter 14 framework counts verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Chapter 14 dbt or SQLMesh output counts."
    )
    parser.add_argument("--label", default="", help="Optional run label, such as dbt.")
    parser.add_argument(
        "--expected",
        type=pathlib.Path,
        default=EXPECTED_COUNTS,
        help="Path to Chapter 12 expected_counts.json.",
    )
    parser.add_argument(
        "--database",
        type=pathlib.Path,
        default=DATABASE,
        help="Path to the shared DuckDB database.",
    )
    args = parser.parse_args()
    return verify(args.expected, args.database, args.label)


if __name__ == "__main__":
    sys.exit(main())
