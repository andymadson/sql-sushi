"""Generate one month of synthetic transactions across three POS systems.

Seeded with 42. Same seed, same data, every time. Writes three CSVs:
  data/clover_transactions.csv  -- amounts in cents
  data/square_transactions.csv  -- amounts in dollars
  data/toast_transactions.csv   -- amounts in dollars, TIMESTAMPTZ

Date range is April 2026, baked into PERIOD_START and PERIOD_END below.
The 30-day window is intentional. The chapter explains the scaling
story when readers run this against the full SQL-Sushi catalog.
"""

from __future__ import annotations

import csv
import pathlib
import random
from datetime import datetime, time, timedelta, timezone

SEED = 42
ORDERS_PER_LOCATION_PER_DAY = 80  # 6 locations * 80 = ~480 orders/day, ~14,400/month
AVG_LINES_PER_ORDER = 4
PERIOD_START = datetime(2026, 4, 1, tzinfo=timezone.utc)
PERIOD_END = datetime(2026, 5, 1, tzinfo=timezone.utc)  # exclusive

PAYMENT_METHODS = ["card", "cash", "mobile", "gift_card"]
PAYMENT_WEIGHTS = [0.70, 0.10, 0.18, 0.02]

# Most rolls and bowls get one of these mass-noun multipliers applied
# so the data isn't perfectly uniform. Drives a realistic Pareto curve.
ITEM_POPULARITY_WEIGHTS = {
    "rolls": 5.0,
    "nigiri": 3.0,
    "bowls": 2.5,
    "sides": 4.0,
    "drinks": 6.0,
}

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load_items() -> list[dict[str, str]]:
    with (DATA / "master_items.csv").open() as f:
        return list(csv.DictReader(f))


def load_locations() -> list[dict[str, str]]:
    with (DATA / "locations.csv").open() as f:
        return list(csv.DictReader(f))


def daterange(start: datetime, end: datetime):
    cur = start
    while cur < end:
        yield cur
        cur += timedelta(days=1)


def random_time_of_day(rng: random.Random) -> time:
    # Bimodal: lunch peak around 12:30, dinner peak around 19:00.
    # gauss is fine for synthetic data; we clamp to operating hours.
    if rng.random() < 0.40:
        hour = rng.gauss(12.5, 1.2)
    else:
        hour = rng.gauss(19.0, 1.5)
    hour = max(11.0, min(22.0, hour))
    h = int(hour)
    m = int((hour - h) * 60)
    s = rng.randint(0, 59)
    return time(h, m, s)


def pick_items(rng: random.Random, items: list[dict[str, str]], n_lines: int):
    weights = [ITEM_POPULARITY_WEIGHTS[item["category"]] for item in items]
    return rng.choices(items, weights=weights, k=n_lines)


def write_clover(rows: list[dict]) -> None:
    """Clover: amount in cents (INTEGER), split date and time, native item name."""
    path = DATA / "clover_transactions.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "transaction_id",
                "location_id",
                "item_name",
                "amount_cents",
                "quantity",
                "payment_method",
                "txn_date",
                "txn_time",
            ],
        )
        writer.writeheader()
        for r in rows:
            ts: datetime = r["ts"]
            writer.writerow(
                {
                    "transaction_id": r["transaction_id"],
                    "location_id": r["location_id"],
                    "item_name": r["pos_name"],
                    "amount_cents": int(round(r["amount_usd"] * 100)),
                    "quantity": r["quantity"],
                    "payment_method": r["payment_method"],
                    "txn_date": ts.date().isoformat(),
                    "txn_time": ts.time().isoformat(timespec="seconds"),
                }
            )
    print(f"wrote {len(rows)} rows to {path.relative_to(ROOT)}")


def write_square(rows: list[dict]) -> None:
    """Square: amount in dollars (NUMERIC), single TIMESTAMP, snake_case item name."""
    path = DATA / "square_transactions.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "transaction_id",
                "location_id",
                "item_name",
                "amount",
                "quantity",
                "payment_method",
                "transaction_at",
            ],
        )
        writer.writeheader()
        for r in rows:
            ts: datetime = r["ts"]
            writer.writerow(
                {
                    "transaction_id": r["transaction_id"],
                    "location_id": r["location_id"],
                    "item_name": r["pos_name"],
                    "amount": f"{r['amount_usd']:.2f}",
                    "quantity": r["quantity"],
                    "payment_method": r["payment_method"],
                    "transaction_at": ts.replace(tzinfo=None).isoformat(sep=" "),
                }
            )
    print(f"wrote {len(rows)} rows to {path.relative_to(ROOT)}")


def write_toast(rows: list[dict]) -> None:
    """Toast: amount in dollars (NUMERIC), TIMESTAMP WITH TIME ZONE, romaji name."""
    path = DATA / "toast_transactions.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "transaction_id",
                "location_id",
                "item_name",
                "amount",
                "quantity",
                "payment_method",
                "transaction_ts",
            ],
        )
        writer.writeheader()
        for r in rows:
            ts: datetime = r["ts"]
            writer.writerow(
                {
                    "transaction_id": r["transaction_id"],
                    "location_id": r["location_id"],
                    "item_name": r["pos_name"],
                    "amount": f"{r['amount_usd']:.2f}",
                    "quantity": r["quantity"],
                    "payment_method": r["payment_method"],
                    "transaction_ts": ts.isoformat(sep=" "),
                }
            )
    print(f"wrote {len(rows)} rows to {path.relative_to(ROOT)}")


def main() -> None:
    rng = random.Random(SEED)
    items = load_items()
    locations = load_locations()

    pos_buckets: dict[str, list[dict]] = {"clover": [], "square": [], "toast": []}
    counters = {"clover": 0, "square": 0, "toast": 0}
    prefixes = {"clover": "CLV-", "square": "SQR-", "toast": "TST-"}
    name_columns = {"clover": "clover_name", "square": "square_name", "toast": "toast_name"}

    for day in daterange(PERIOD_START, PERIOD_END):
        for loc in locations:
            pos = loc["pos_system"]
            # Weekday volume baseline; weekends get a bump.
            mult = 1.25 if day.weekday() >= 4 else 1.0
            n_orders = int(rng.gauss(ORDERS_PER_LOCATION_PER_DAY * mult, 12))
            n_orders = max(20, n_orders)

            for _ in range(n_orders):
                n_lines = max(1, int(rng.gauss(AVG_LINES_PER_ORDER, 1.3)))
                tod = random_time_of_day(rng)
                order_ts = datetime.combine(day.date(), tod, tzinfo=timezone.utc)
                payment = rng.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS, k=1)[0]

                for item in pick_items(rng, items, n_lines):
                    counters[pos] += 1
                    txn_id = f"{prefixes[pos]}{counters[pos]:07d}"
                    quantity = 1 if rng.random() < 0.85 else 2
                    base = float(item["base_price_usd"])
                    # Small per-line price jitter to simulate promotions and rounding.
                    amount = round(base * quantity * rng.uniform(0.92, 1.05), 2)
                    pos_buckets[pos].append(
                        {
                            "transaction_id": txn_id,
                            "location_id": int(loc["location_id"]),
                            "pos_name": item[name_columns[pos]],
                            "amount_usd": amount,
                            "quantity": quantity,
                            "payment_method": payment,
                            "ts": order_ts,
                        }
                    )

    write_clover(pos_buckets["clover"])
    write_square(pos_buckets["square"])
    write_toast(pos_buckets["toast"])

    total = sum(len(b) for b in pos_buckets.values())
    print(f"total: {total} line items across {len(locations)} locations, "
          f"{(PERIOD_END - PERIOD_START).days} days")


if __name__ == "__main__":
    main()
