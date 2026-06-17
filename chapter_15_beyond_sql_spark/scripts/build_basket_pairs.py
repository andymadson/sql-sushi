"""Build basket item-pair counts with PySpark.

The example intentionally does not replace the Chapter 12 SQL pipeline. It uses
Spark for one shape where arrays and pair generation are clearer than a long SQL
self-join: co-purchased item pairs within reconstructed baskets.
"""

from __future__ import annotations

import csv
import json
import os
import pathlib
import shutil

from pyspark.sql import SparkSession, functions as F, types as T

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_12_DATA = REPO_ROOT / "chapter_12_scheduling_sql_pipelines_python" / "data"
CHAPTER_15_DATA = REPO_ROOT / "chapter_15_beyond_sql_spark" / "data"
PAIR_COUNTS_CSV = CHAPTER_15_DATA / "basket_pair_counts.csv"
SUMMARY_JSON = CHAPTER_15_DATA / "basket_summary.json"


PAIR_SCHEMA = T.ArrayType(
    T.StructType(
        [
            T.StructField("item_a", T.StringType(), nullable=False),
            T.StructField("item_b", T.StringType(), nullable=False),
        ]
    )
)


@F.udf(returnType=PAIR_SCHEMA)
def item_pairs(items):
    if not items:
        return []
    ordered = sorted(set(items))
    return [
        {"item_a": ordered[i], "item_b": ordered[j]}
        for i in range(len(ordered))
        for j in range(i + 1, len(ordered))
    ]


def _require_inputs() -> None:
    required = [
        "master_items.csv",
        "locations.csv",
        "clover_transactions.csv",
        "square_transactions.csv",
        "toast_transactions.csv",
    ]
    missing = [name for name in required if not (CHAPTER_12_DATA / name).exists()]
    if missing:
        missing_text = ", ".join(missing)
        msg = (
            f"Missing Chapter 12 input files: {missing_text}. "
            "Run chapter_15_beyond_sql_spark/scripts/prepare_spark_inputs.py first."
        )
        raise FileNotFoundError(msg)


def _require_java() -> None:
    if os.environ.get("JAVA_HOME") or shutil.which("java"):
        return
    raise RuntimeError(
        "Java is required for the Chapter 15 Spark example. "
        "Install a JDK and make java available on PATH or set JAVA_HOME."
    )


def _read_csv(spark: SparkSession, name: str):
    return spark.read.option("header", True).csv(str(CHAPTER_12_DATA / name))


def _normalize_pos_lines(spark: SparkSession):
    master = _read_csv(spark, "master_items.csv")

    clover = (
        _read_csv(spark, "clover_transactions.csv")
        .join(master, F.col("item_name") == F.col("clover_name"), "inner")
        .select(
            F.lit("clover").alias("source_pos"),
            F.col("transaction_id").alias("line_id"),
            F.col("location_id").cast("int").alias("location_id"),
            F.col("master_item_id"),
            (F.col("amount_cents").cast("double") / F.lit(100.0)).alias(
                "amount_usd"
            ),
            F.col("quantity").cast("int").alias("quantity"),
            F.col("payment_method"),
            F.concat_ws(" ", F.col("txn_date"), F.col("txn_time")).alias(
                "transaction_ts"
            ),
        )
    )

    square = (
        _read_csv(spark, "square_transactions.csv")
        .join(master, F.col("item_name") == F.col("square_name"), "inner")
        .select(
            F.lit("square").alias("source_pos"),
            F.col("transaction_id").alias("line_id"),
            F.col("location_id").cast("int").alias("location_id"),
            F.col("master_item_id"),
            F.col("amount").cast("double").alias("amount_usd"),
            F.col("quantity").cast("int").alias("quantity"),
            F.col("payment_method"),
            F.col("transaction_at").alias("transaction_ts"),
        )
    )

    toast = (
        _read_csv(spark, "toast_transactions.csv")
        .join(master, F.col("item_name") == F.col("toast_name"), "inner")
        .select(
            F.lit("toast").alias("source_pos"),
            F.col("transaction_id").alias("line_id"),
            F.col("location_id").cast("int").alias("location_id"),
            F.col("master_item_id"),
            F.col("amount").cast("double").alias("amount_usd"),
            F.col("quantity").cast("int").alias("quantity"),
            F.col("payment_method"),
            F.col("transaction_ts"),
        )
    )

    return clover.unionByName(square).unionByName(toast)


def _write_single_csv(data_frame, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.stem}.tmp")
    with temp_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data_frame.columns)
        writer.writeheader()
        for row in data_frame.toLocalIterator():
            writer.writerow(row.asDict())
    temp_path.replace(path)


def main() -> int:
    _require_inputs()
    _require_java()
    CHAPTER_15_DATA.mkdir(parents=True, exist_ok=True)

    spark = (
        SparkSession.builder.appName("sql-sushi-chapter-15-basket-pairs")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        normalized = _normalize_pos_lines(spark)
        basket_keys = [
            "source_pos",
            "location_id",
            "transaction_ts",
            "payment_method",
        ]
        baskets = normalized.groupBy(*basket_keys).agg(
            F.array_sort(F.collect_set("master_item_id")).alias("items"),
            F.count("*").alias("line_count"),
            F.round(F.sum("amount_usd"), 2).alias("basket_amount_usd"),
        )
        eligible_baskets = baskets.where(F.size(F.col("items")) >= 2)
        pair_counts = (
            eligible_baskets.select(F.explode(item_pairs("items")).alias("pair"))
            .select(F.col("pair.item_a"), F.col("pair.item_b"))
            .groupBy("item_a", "item_b")
            .agg(F.count("*").alias("basket_count"))
            .orderBy(F.desc("basket_count"), F.asc("item_a"), F.asc("item_b"))
        )

        summary = {
            "total_baskets": baskets.count(),
            "eligible_baskets": eligible_baskets.count(),
            "distinct_item_pairs": pair_counts.count(),
        }
        _write_single_csv(pair_counts, PAIR_COUNTS_CSV)
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        print("wrote Chapter 15 Spark basket outputs")
        print(json.dumps(summary, indent=2))
    finally:
        spark.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
