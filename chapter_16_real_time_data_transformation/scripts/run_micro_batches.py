"""Run the Chapter 16 local micro-batch transformation."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
from datetime import datetime, timedelta
from decimal import Decimal

import duckdb

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_16_DATA = REPO_ROOT / "chapter_16_real_time_data_transformation" / "data"
DATABASE = CHAPTER_16_DATA / "real_time.duckdb"
SUMMARY_JSON = CHAPTER_16_DATA / "real_time_summary.json"
AGGREGATES_CSV = CHAPTER_16_DATA / "sales_15min_by_location.csv"
LATE_EVENTS_CSV = CHAPTER_16_DATA / "late_events.csv"
ALLOWED_LATENESS = timedelta(minutes=30)


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _format_ts(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat(sep=" ", timespec="seconds")


def _connect() -> duckdb.DuckDBPyConnection:
    CHAPTER_16_DATA.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DATABASE))


def _reset_outputs() -> None:
    for path in [DATABASE, SUMMARY_JSON, AGGREGATES_CSV, LATE_EVENTS_CSV]:
        if path.exists():
            path.unlink()
    wal = DATABASE.with_suffix(".duckdb.wal")
    if wal.exists():
        wal.unlink()


def _init_db(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_state (
            state_key TEXT PRIMARY KEY,
            state_value TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_files (
            file_name TEXT PRIMARY KEY,
            processed_at TIMESTAMP NOT NULL,
            accepted_events INTEGER NOT NULL,
            late_events INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sales_events (
            event_id TEXT PRIMARY KEY,
            source_pos TEXT NOT NULL,
            location_id INTEGER NOT NULL,
            master_item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            amount_usd DECIMAL(12, 2) NOT NULL,
            event_ts TIMESTAMP NOT NULL,
            arrival_ts TIMESTAMP NOT NULL,
            source_file TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS late_events (
            event_id TEXT PRIMARY KEY,
            source_pos TEXT NOT NULL,
            location_id INTEGER NOT NULL,
            master_item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            amount_usd DECIMAL(12, 2) NOT NULL,
            event_ts TIMESTAMP NOT NULL,
            arrival_ts TIMESTAMP NOT NULL,
            source_file TEXT NOT NULL,
            watermark_ts TIMESTAMP NOT NULL,
            reason TEXT NOT NULL
        )
        """
    )


def _get_state_ts(conn: duckdb.DuckDBPyConnection, key: str) -> datetime | None:
    row = conn.execute(
        "SELECT state_value FROM pipeline_state WHERE state_key = ?",
        [key],
    ).fetchone()
    if row is None:
        return None
    return _parse_ts(str(row[0]))


def _set_state(conn: duckdb.DuckDBPyConnection, key: str, value: datetime) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO pipeline_state (state_key, state_value)
        VALUES (?, ?)
        """,
        [key, _format_ts(value)],
    )


def _is_processed(conn: duckdb.DuckDBPyConnection, file_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM processed_files WHERE file_name = ?",
        [file_name],
    ).fetchone()
    return row is not None


def _read_batch(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _insert_accepted(
    conn: duckdb.DuckDBPyConnection,
    row: dict[str, str],
    source_file: str,
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO sales_events
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            row["event_id"],
            row["source_pos"],
            int(row["location_id"]),
            row["master_item_id"],
            int(row["quantity"]),
            Decimal(row["amount_usd"]),
            _parse_ts(row["event_ts"]),
            _parse_ts(row["arrival_ts"]),
            source_file,
        ],
    )


def _insert_late(
    conn: duckdb.DuckDBPyConnection,
    row: dict[str, str],
    source_file: str,
    watermark_ts: datetime,
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO late_events
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            row["event_id"],
            row["source_pos"],
            int(row["location_id"]),
            row["master_item_id"],
            int(row["quantity"]),
            Decimal(row["amount_usd"]),
            _parse_ts(row["event_ts"]),
            _parse_ts(row["arrival_ts"]),
            source_file,
            watermark_ts,
            "event_ts older than current watermark",
        ],
    )


def _process_batch(conn: duckdb.DuckDBPyConnection, path: pathlib.Path) -> None:
    if _is_processed(conn, path.name):
        print(f"skipping already processed file: {path.name}")
        return

    rows = _read_batch(path)
    if not rows:
        raise ValueError(f"{path} has no event rows")

    file_max_event_ts = max(_parse_ts(row["event_ts"]) for row in rows)
    previous_max = _get_state_ts(conn, "max_event_ts")
    max_event_ts = max(
        [value for value in [previous_max, file_max_event_ts] if value is not None]
    )
    watermark_ts = max_event_ts - ALLOWED_LATENESS

    accepted_count = 0
    late_count = 0
    for row in rows:
        event_ts = _parse_ts(row["event_ts"])
        if event_ts < watermark_ts:
            _insert_late(conn, row, path.name, watermark_ts)
            late_count += 1
        else:
            _insert_accepted(conn, row, path.name)
            accepted_count += 1

    conn.execute(
        """
        INSERT INTO processed_files
        VALUES (?, current_timestamp, ?, ?)
        """,
        [path.name, accepted_count, late_count],
    )
    _set_state(conn, "max_event_ts", max_event_ts)
    _set_state(conn, "current_watermark_ts", watermark_ts)
    print(
        f"processed {path.name}: accepted={accepted_count}, "
        f"late={late_count}, watermark={_format_ts(watermark_ts)}"
    )


def _refresh_aggregates(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
        CREATE OR REPLACE TABLE sales_15min_by_location AS
        SELECT
            time_bucket(INTERVAL '15 minutes', event_ts) AS window_start,
            location_id,
            COUNT(*)::INTEGER AS event_count,
            ROUND(SUM(amount_usd), 2)::DECIMAL(12, 2) AS gross_sales_usd
        FROM sales_events
        GROUP BY 1, 2
        ORDER BY 1, 2
        """
    )


def _write_query_csv(
    conn: duckdb.DuckDBPyConnection,
    query: str,
    path: pathlib.Path,
) -> None:
    cursor = conn.execute(query)
    columns = [item[0] for item in cursor.description]
    rows = cursor.fetchall()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow([_stringify_csv_value(value) for value in row])


def _stringify_csv_value(value: object) -> object:
    if isinstance(value, datetime):
        return _format_ts(value)
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    return value


def _scalar(conn: duckdb.DuckDBPyConnection, query: str) -> object:
    return conn.execute(query).fetchone()[0]


def _write_outputs(conn: duckdb.DuckDBPyConnection) -> None:
    _refresh_aggregates(conn)
    max_event_ts = _get_state_ts(conn, "max_event_ts")
    watermark_ts = _get_state_ts(conn, "current_watermark_ts")
    gross_sales = _scalar(
        conn,
        "SELECT COALESCE(ROUND(SUM(amount_usd), 2), 0)::DECIMAL(12, 2) FROM sales_events",
    )

    summary = {
        "processed_files": int(_scalar(conn, "SELECT COUNT(*) FROM processed_files")),
        "accepted_events": int(_scalar(conn, "SELECT COUNT(*) FROM sales_events")),
        "late_events": int(_scalar(conn, "SELECT COUNT(*) FROM late_events")),
        "aggregate_rows": int(
            _scalar(conn, "SELECT COUNT(*) FROM sales_15min_by_location")
        ),
        "gross_sales_usd": f"{gross_sales:.2f}",
        "max_event_ts": _format_ts(max_event_ts),
        "current_watermark_ts": _format_ts(watermark_ts),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _write_query_csv(
        conn,
        """
        SELECT window_start, location_id, event_count, gross_sales_usd
        FROM sales_15min_by_location
        ORDER BY window_start, location_id
        """,
        AGGREGATES_CSV,
    )
    _write_query_csv(
        conn,
        """
        SELECT event_id, event_ts, arrival_ts, source_file, watermark_ts, reason
        FROM late_events
        ORDER BY event_id
        """,
        LATE_EVENTS_CSV,
    )
    print(f"wrote {SUMMARY_JSON.relative_to(REPO_ROOT)}")
    print(f"wrote {AGGREGATES_CSV.relative_to(REPO_ROOT)}")
    print(f"wrote {LATE_EVENTS_CSV.relative_to(REPO_ROOT)}")


def run(reset: bool) -> int:
    if reset:
        _reset_outputs()
    batch_files = sorted(CHAPTER_16_DATA.glob("events_batch_*.csv"))
    if not batch_files:
        raise FileNotFoundError(
            "Missing Chapter 16 event batches. Run "
            "chapter_16_real_time_data_transformation/scripts/"
            "prepare_event_batches.py first."
        )

    conn = _connect()
    try:
        _init_db(conn)
        for path in batch_files:
            _process_batch(conn, path)
        _write_outputs(conn)
    finally:
        conn.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Chapter 16 local micro-batch transformation."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete prior Chapter 16 generated outputs before processing.",
    )
    args = parser.parse_args()
    return run(args.reset)


if __name__ == "__main__":
    sys.exit(main())
