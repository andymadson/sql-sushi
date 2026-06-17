"""Prepare deterministic event batches for Chapter 16.

The batches are intentionally tiny. They teach event-time processing and late
data without requiring Kafka, Flink, or a managed streaming service.
"""

from __future__ import annotations

import csv
import pathlib
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from decimal import Decimal

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_12 = REPO_ROOT / "chapter_12_scheduling_sql_pipelines_python"
CHAPTER_12_DATA = CHAPTER_12 / "data"
CHAPTER_16_DATA = REPO_ROOT / "chapter_16_real_time_data_transformation" / "data"

FIELDNAMES = [
    "event_id",
    "source_pos",
    "location_id",
    "master_item_id",
    "quantity",
    "amount_usd",
    "event_ts",
    "arrival_ts",
]

BATCH_SCHEDULE = [
    ("events_batch_01.csv", [0, 5, 8, 9, 10, 11, 12, 14]),
    ("events_batch_02.csv", [22, 24, 26, 28, 31, 33, 35, 36]),
    ("events_batch_03.csv", [70, 72, 74, 75, 78, 81, 84, 86]),
    ("events_batch_04_late.csv", [18, 22, 31, 90, 95, 99]),
]

LATE_BATCH_EVENT_NUMBERS = {25, 26, 27}


def _run_chapter_12_seed(script_name: str) -> None:
    script = CHAPTER_12 / "scripts" / script_name
    subprocess.run([sys.executable, str(script)], cwd=REPO_ROOT, check=True)


def _load_master_item_ids() -> list[str]:
    path = CHAPTER_12_DATA / "master_items.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return [row["master_item_id"] for row in csv.DictReader(f)]


def _event_amount(event_number: int) -> Decimal:
    return Decimal("10.00") + Decimal((event_number - 1) % 5) * Decimal("1.50")


def _format_ts(value: datetime) -> str:
    return value.isoformat(sep=" ", timespec="seconds")


def _build_event(
    event_number: int,
    minute_offset: int,
    item_ids: list[str],
    base_ts: datetime,
) -> dict[str, str]:
    event_ts = base_ts + timedelta(minutes=minute_offset)
    if event_number in LATE_BATCH_EVENT_NUMBERS:
        arrival_ts = base_ts + timedelta(minutes=102 + event_number)
    else:
        arrival_ts = event_ts + timedelta(minutes=2 + event_number % 4)

    source_pos = ["clover", "square", "toast"][(event_number - 1) % 3]
    return {
        "event_id": f"EVT-{event_number:04d}",
        "source_pos": source_pos,
        "location_id": "1",
        "master_item_id": item_ids[(event_number - 1) % len(item_ids)],
        "quantity": "1",
        "amount_usd": f"{_event_amount(event_number):.2f}",
        "event_ts": _format_ts(event_ts),
        "arrival_ts": _format_ts(arrival_ts),
    }


def _write_batch(path: pathlib.Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} events to {path.relative_to(REPO_ROOT)}")


def main() -> int:
    _run_chapter_12_seed("build_seed_data.py")
    item_ids = _load_master_item_ids()

    if CHAPTER_16_DATA.exists():
        shutil.rmtree(CHAPTER_16_DATA)
    CHAPTER_16_DATA.mkdir(parents=True, exist_ok=True)

    base_ts = datetime(2026, 4, 1, 11, 0, 0)
    event_number = 1
    for file_name, offsets in BATCH_SCHEDULE:
        rows = []
        for offset in offsets:
            rows.append(_build_event(event_number, offset, item_ids, base_ts))
            event_number += 1
        _write_batch(CHAPTER_16_DATA / file_name, rows)

    print("prepared Chapter 16 deterministic event batches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
