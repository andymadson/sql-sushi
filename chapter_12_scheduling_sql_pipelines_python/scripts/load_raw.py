"""Load the CSVs in data/ into the raw schema using DuckDB COPY."""

from __future__ import annotations

import csv
import pathlib

import duckdb

from db import connect

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def _path_literal(csv_path: pathlib.Path) -> str:
    return "'" + csv_path.resolve().as_posix().replace("'", "''") + "'"


def _csv_header_columns(csv_path: pathlib.Path) -> str:
    with csv_path.open(newline="") as f:
        header = next(csv.reader(f))
    return ", ".join(f'"{column}"' for column in header)


def _count_rows(conn: duckdb.DuckDBPyConnection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _copy_csv(
    conn: duckdb.DuckDBPyConnection,
    table: str,
    csv_path: pathlib.Path,
    columns_sql: str | None = None,
) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV: {csv_path}")

    target = f"{table} ({columns_sql})" if columns_sql else table
    conn.execute(f"DELETE FROM {table}")
    conn.execute(f"COPY {target} FROM {_path_literal(csv_path)} (HEADER, DELIMITER ',')")
    return _count_rows(conn, table)


def _load_dim(conn: duckdb.DuckDBPyConnection, table: str, csv_path: pathlib.Path) -> int:
    return _copy_csv(conn, table, csv_path)


def _load_transactions(
    conn: duckdb.DuckDBPyConnection, target_table: str, csv_path: pathlib.Path
) -> int:
    columns_sql = _csv_header_columns(csv_path)
    return _copy_csv(conn, target_table, csv_path, columns_sql)


def _load_all(conn: duckdb.DuckDBPyConnection) -> dict[str, int]:
    counts: dict[str, int] = {}
    counts["raw.master_items"] = _load_dim(
        conn, "raw.master_items", DATA / "master_items.csv"
    )
    counts["raw.locations"] = _load_dim(conn, "raw.locations", DATA / "locations.csv")
    counts["raw.clover_transactions"] = _load_transactions(
        conn, "raw.clover_transactions", DATA / "clover_transactions.csv"
    )
    counts["raw.square_transactions"] = _load_transactions(
        conn, "raw.square_transactions", DATA / "square_transactions.csv"
    )
    counts["raw.toast_transactions"] = _load_transactions(
        conn, "raw.toast_transactions", DATA / "toast_transactions.csv"
    )
    return counts


def main(conn: duckdb.DuckDBPyConnection | None = None) -> dict[str, int]:
    if conn is not None:
        return _load_all(conn)

    owned_conn = connect()
    try:
        owned_conn.execute("BEGIN")
        try:
            counts = _load_all(owned_conn)
        except Exception:
            owned_conn.execute("ROLLBACK")
            raise
        owned_conn.execute("COMMIT")
        return counts
    finally:
        owned_conn.close()


if __name__ == "__main__":
    for table, n in main().items():
        print(f"{table}: {n} rows")
