"""Verify deterministic Chapter 16 real-time transformation outputs."""

from __future__ import annotations

import csv
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_16_DATA = REPO_ROOT / "chapter_16_real_time_data_transformation" / "data"
SUMMARY_JSON = CHAPTER_16_DATA / "real_time_summary.json"
AGGREGATES_CSV = CHAPTER_16_DATA / "sales_15min_by_location.csv"
LATE_EVENTS_CSV = CHAPTER_16_DATA / "late_events.csv"

EXPECTED_SUMMARY = {
    "processed_files": 4,
    "accepted_events": 27,
    "late_events": 3,
    "aggregate_rows": 6,
    "gross_sales_usd": "352.50",
    "max_event_ts": "2026-04-01 12:39:00",
    "current_watermark_ts": "2026-04-01 12:09:00",
}

EXPECTED_AGGREGATES = [
    {
        "window_start": "2026-04-01 11:00:00",
        "location_id": "1",
        "event_count": "8",
        "gross_sales_usd": "99.50",
    },
    {
        "window_start": "2026-04-01 11:15:00",
        "location_id": "1",
        "event_count": "4",
        "gross_sales_usd": "52.00",
    },
    {
        "window_start": "2026-04-01 11:30:00",
        "location_id": "1",
        "event_count": "4",
        "gross_sales_usd": "53.50",
    },
    {
        "window_start": "2026-04-01 12:00:00",
        "location_id": "1",
        "event_count": "3",
        "gross_sales_usd": "39.00",
    },
    {
        "window_start": "2026-04-01 12:15:00",
        "location_id": "1",
        "event_count": "5",
        "gross_sales_usd": "65.00",
    },
    {
        "window_start": "2026-04-01 12:30:00",
        "location_id": "1",
        "event_count": "3",
        "gross_sales_usd": "43.50",
    },
]

EXPECTED_LATE_EVENT_IDS = ["EVT-0025", "EVT-0026", "EVT-0027"]


def _load_json(path: pathlib.Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run run_micro_batches.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run run_micro_batches.py first.")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _verify_summary(errors: list[str]) -> None:
    summary = _load_json(SUMMARY_JSON)
    for key, expected in EXPECTED_SUMMARY.items():
        actual = summary.get(key)
        if actual == expected:
            print(f"OK summary.{key}: {actual}")
            continue
        errors.append(f"summary.{key}: expected {expected}, got {actual}")


def _verify_aggregates(errors: list[str]) -> None:
    rows = _load_csv(AGGREGATES_CSV)
    if rows == EXPECTED_AGGREGATES:
        print("OK sales_15min_by_location rows")
        return
    errors.append(f"aggregate rows changed: expected {EXPECTED_AGGREGATES}, got {rows}")


def _verify_late_events(errors: list[str]) -> None:
    rows = _load_csv(LATE_EVENTS_CSV)
    actual_ids = [row["event_id"] for row in rows]
    if actual_ids == EXPECTED_LATE_EVENT_IDS:
        print(f"OK late event IDs: {actual_ids}")
        return
    errors.append(f"late event IDs changed: expected {EXPECTED_LATE_EVENT_IDS}, got {actual_ids}")


def main() -> int:
    errors: list[str] = []
    _verify_summary(errors)
    _verify_aggregates(errors)
    _verify_late_events(errors)

    if errors:
        print("\nVerification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("All Chapter 16 real-time checks verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
