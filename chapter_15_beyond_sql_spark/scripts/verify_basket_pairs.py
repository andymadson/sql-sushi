"""Verify the deterministic Chapter 15 Spark basket-pair output."""

from __future__ import annotations

import csv
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_15_DATA = REPO_ROOT / "chapter_15_beyond_sql_spark" / "data"
PAIR_COUNTS_CSV = CHAPTER_15_DATA / "basket_pair_counts.csv"
SUMMARY_JSON = CHAPTER_15_DATA / "basket_summary.json"

EXPECTED_SUMMARY = {
    "total_baskets": 15819,
    "eligible_baskets": 14735,
    "distinct_item_pairs": 435,
}

EXPECTED_TOP_10 = [
    {"item_a": "DRINK_001", "item_b": "DRINK_002", "basket_count": "385"},
    {"item_a": "DRINK_001", "item_b": "SUSHI_008", "basket_count": "346"},
    {"item_a": "DRINK_002", "item_b": "SUSHI_007", "basket_count": "334"},
    {"item_a": "DRINK_002", "item_b": "SUSHI_012", "basket_count": "333"},
    {"item_a": "DRINK_002", "item_b": "SUSHI_005", "basket_count": "328"},
    {"item_a": "DRINK_002", "item_b": "SUSHI_002", "basket_count": "327"},
    {"item_a": "DRINK_002", "item_b": "SUSHI_009", "basket_count": "323"},
    {"item_a": "DRINK_002", "item_b": "SUSHI_010", "basket_count": "322"},
    {"item_a": "DRINK_001", "item_b": "SUSHI_012", "basket_count": "320"},
    {"item_a": "DRINK_001", "item_b": "SUSHI_010", "basket_count": "317"},
]


def _load_summary() -> dict[str, int]:
    if not SUMMARY_JSON.exists():
        raise FileNotFoundError(
            "Missing basket_summary.json. Run build_basket_pairs.py first."
        )
    return json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))


def _load_pair_counts() -> list[dict[str, str]]:
    if not PAIR_COUNTS_CSV.exists():
        raise FileNotFoundError(
            "Missing basket_pair_counts.csv. Run build_basket_pairs.py first."
        )
    with PAIR_COUNTS_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    summary = _load_summary()
    for key, expected in EXPECTED_SUMMARY.items():
        actual = summary.get(key)
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")
        print(f"OK {key}: {actual}")

    rows = _load_pair_counts()
    actual_top_10 = rows[:10]
    if actual_top_10 != EXPECTED_TOP_10:
        raise AssertionError(
            f"top 10 basket pairs changed: expected {EXPECTED_TOP_10}, "
            f"got {actual_top_10}"
        )

    print("OK top 10 basket pairs")
    print("All Chapter 15 Spark basket checks verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
