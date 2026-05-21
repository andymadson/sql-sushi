"""Load the CSVs in data/ into the raw schema using server-side COPY.

Idempotent on the small dimension tables (TRUNCATE + COPY). For the
transactional tables it uses INSERT ... ON CONFLICT DO NOTHING so a
re-run won't duplicate rows. That covers the most common operator case:
re-run the loader after a transient failure.
"""

from __future__ import annotations

import pathlib

from db import connect

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def _load_dim(cur, table: str, csv_path: pathlib.Path) -> int:
    """TRUNCATE + COPY for dimension tables. Small, no reason to be clever."""
    cur.execute(f"TRUNCATE TABLE {table}")
    with csv_path.open("rb") as f, cur.copy(
        f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)"
    ) as copy:
        while data := f.read(65536):
            copy.write(data)
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]


def _load_transactions(cur, target_table: str, csv_path: pathlib.Path) -> int:
    """Load a transactional CSV through a staging temp table, then
    INSERT ... ON CONFLICT DO NOTHING into the real table.

    The temp table is created LIKE the target so column types and order
    match without us having to spell them out here.
    """
    cur.execute("DROP TABLE IF EXISTS _stage")
    cur.execute(
        f"""
        CREATE TEMP TABLE _stage (LIKE {target_table} INCLUDING DEFAULTS)
        ON COMMIT DROP
        """
    )
    # COPY into the temp table from CSV, excluding the loaded_at column
    # which carries a server-side default.
    columns_sql = _csv_header_columns(csv_path)
    with csv_path.open("rb") as f, cur.copy(
        f"COPY _stage ({columns_sql}) FROM STDIN WITH (FORMAT csv, HEADER true)"
    ) as copy:
        while data := f.read(65536):
            copy.write(data)
    cur.execute(
        f"""
        INSERT INTO {target_table} ({columns_sql})
        SELECT {columns_sql} FROM _stage
        ON CONFLICT (transaction_id) DO NOTHING
        """
    )
    cur.execute(f"SELECT COUNT(*) FROM {target_table}")
    return cur.fetchone()[0]


def _csv_header_columns(csv_path: pathlib.Path) -> str:
    with csv_path.open() as f:
        header = f.readline().strip()
    return header


def main() -> dict[str, int]:
    counts: dict[str, int] = {}
    with connect() as conn:
        with conn.cursor() as cur:
            counts["raw.master_items"] = _load_dim(
                cur, "raw.master_items", DATA / "master_items.csv"
            )
            counts["raw.locations"] = _load_dim(
                cur, "raw.locations", DATA / "locations.csv"
            )
            counts["raw.clover_transactions"] = _load_transactions(
                cur, "raw.clover_transactions", DATA / "clover_transactions.csv"
            )
            counts["raw.square_transactions"] = _load_transactions(
                cur, "raw.square_transactions", DATA / "square_transactions.csv"
            )
            counts["raw.toast_transactions"] = _load_transactions(
                cur, "raw.toast_transactions", DATA / "toast_transactions.csv"
            )
        conn.commit()
    return counts


if __name__ == "__main__":
    for table, n in main().items():
        print(f"{table}: {n} rows")
