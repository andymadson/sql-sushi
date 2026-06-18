"""Verify the Chapter 17 end-to-end SQLMesh outputs."""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

import duckdb


ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER = ROOT / "chapter_17_end_to_end_sqlmesh_github_actions"
CHAPTER_12 = ROOT / "chapter_12_scheduling_sql_pipelines_python"
EXPECTED_COUNTS = CHAPTER_12 / "expected_counts.json"
DATABASE = CHAPTER / "data" / "sqlsushi_end_to_end.duckdb"
RELATION_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$")
REQUIRED_RELATIONS = (
    "raw.master_items",
    "raw.locations",
    "raw.clover_transactions",
    "raw.square_transactions",
    "raw.toast_transactions",
    "staging.stg_pos_transactions",
    "analytics.fact_sales",
    "analytics.daily_menu_sales",
    "analytics.agg_daily_sales_by_location",
    "analytics.agg_top_items_30d",
)


def _load_expected(path: pathlib.Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _relation_count(conn: duckdb.DuckDBPyConnection, relation: str) -> int:
    if not RELATION_RE.fullmatch(relation):
        raise ValueError(f"Unexpected relation name: {relation}")
    return int(conn.execute(f"SELECT COUNT(*) FROM {relation}").fetchone()[0])


def _scalar(conn: duckdb.DuckDBPyConnection, sql: str) -> int:
    return int(conn.execute(sql).fetchone()[0])


def _record_check(errors: list[str], label: str, expected: int, actual: int) -> None:
    if actual == expected:
        print(f"OK   {label}: {actual}")
        return
    errors.append(f"{label}: expected {expected}, got {actual}")
    print(f"FAIL {label}: expected {expected}, got {actual}")


def main() -> int:
    expected = _load_expected(EXPECTED_COUNTS)
    relation_counts = expected["relations"]
    errors: list[str] = []

    if not DATABASE.exists():
        print(f"FAIL Missing DuckDB database: {DATABASE}")
        return 1

    conn = duckdb.connect(str(DATABASE), read_only=True)
    try:
        for relation in REQUIRED_RELATIONS:
            actual = _relation_count(conn, relation)
            _record_check(errors, relation, int(relation_counts[relation]), actual)

        duplicate_fact_keys = _scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM (
                SELECT transaction_id
                FROM analytics.fact_sales
                GROUP BY transaction_id
                HAVING COUNT(*) > 1
            )
            """,
        )
        _record_check(
            errors,
            "analytics.fact_sales duplicate transaction_id groups",
            0,
            duplicate_fact_keys,
        )

        daily_rows = _relation_count(conn, "analytics.daily_menu_sales")
        daily_grain_rows = _scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM (
                SELECT sales_date, location_id, master_item_id
                FROM analytics.daily_menu_sales
                GROUP BY sales_date, location_id, master_item_id
            )
            """,
        )
        _record_check(
            errors,
            "analytics.daily_menu_sales unique grain rows",
            daily_rows,
            daily_grain_rows,
        )

        null_menu_keys = _scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM analytics.daily_menu_sales
            WHERE sales_date IS NULL
               OR location_id IS NULL
               OR master_item_id IS NULL
               OR location_name IS NULL
               OR menu_category IS NULL
            """,
        )
        _record_check(
            errors,
            "analytics.daily_menu_sales null key or label fields",
            0,
            null_menu_keys,
        )
    finally:
        conn.close()

    if errors:
        print("\nChapter 17 verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nAll Chapter 17 SQLMesh outputs verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
