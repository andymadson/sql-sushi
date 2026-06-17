"""Prepare the Chapter 12 raw DuckDB tables for Chapter 14 frameworks."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_12 = ROOT / "chapter_12_scheduling_sql_pipelines_python"
CHAPTER_12_SCRIPTS = CHAPTER_12 / "scripts"
SQL_DIR = CHAPTER_12 / "sql"

sys.path.insert(0, str(CHAPTER_12_SCRIPTS))

import build_seed_data  # noqa: E402
import generate_data  # noqa: E402
import load_raw  # noqa: E402
from db import connect  # noqa: E402


def _execute_sql_file(path: pathlib.Path) -> None:
    with connect() as conn:
        conn.execute(path.read_text(encoding="utf-8"))


def main() -> int:
    build_seed_data.main()
    generate_data.main()
    _execute_sql_file(SQL_DIR / "00_create_schemas.sql")
    _execute_sql_file(SQL_DIR / "10_raw_ddl.sql")
    with connect() as conn:
        conn.execute("BEGIN")
        try:
            counts = load_raw.main(conn)
        except Exception:
            conn.execute("ROLLBACK")
            raise
        conn.execute("COMMIT")
    print("prepared Chapter 12 raw tables for Chapter 14")
    for table, row_count in counts.items():
        print(f"{table}: {row_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
