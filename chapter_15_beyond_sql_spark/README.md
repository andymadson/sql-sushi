# Chapter 15: Beyond SQL

Chapter 15 keeps the SQL-Sushi pipeline from becoming a full Spark platform. It uses Spark for one focused mini-example: reconstructing same-order baskets from POS line items and counting item pairs that appear together.

That shape is possible in SQL, but it gets awkward quickly. Spark lets the example use grouped arrays, a small Python pair generator, and distributed aggregation without rewriting the Chapter 12 pipeline.

## What's Here

```text
chapter_15_beyond_sql_spark/
|-- README.md
|-- requirements.txt
`-- scripts/
    |-- prepare_spark_inputs.py
    |-- build_basket_pairs.py
    `-- verify_basket_pairs.py
```

Generated files are written under `chapter_15_beyond_sql_spark/data/` and are ignored by Git:

- `basket_pair_counts.csv`
- `basket_summary.json`

## Requirements

- Python 3.12
- Java 17 or another Java version supported by the pinned PySpark runtime

## Quick Start

Run these commands from the repo root.

Mac/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_15_beyond_sql_spark/requirements.txt
.venv/bin/python chapter_15_beyond_sql_spark/scripts/prepare_spark_inputs.py
.venv/bin/python chapter_15_beyond_sql_spark/scripts/build_basket_pairs.py
.venv/bin/python chapter_15_beyond_sql_spark/scripts/verify_basket_pairs.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install `
  -r requirements-dev.txt `
  -r chapter_12_scheduling_sql_pipelines_python\requirements.txt `
  -r chapter_15_beyond_sql_spark\requirements.txt
.\.venv\Scripts\python.exe chapter_15_beyond_sql_spark\scripts\prepare_spark_inputs.py
.\.venv\Scripts\python.exe chapter_15_beyond_sql_spark\scripts\build_basket_pairs.py
.\.venv\Scripts\python.exe chapter_15_beyond_sql_spark\scripts\verify_basket_pairs.py
```

If `java` is not on `PATH`, the Spark build step will fail before it starts the local Spark session. Install a JDK and rerun the build.

On Windows, Spark may warn that `winutils.exe` is missing. This example still runs locally without a Hadoop install because Spark computes the pair counts and Python writes the small final CSV. Treat the warning as harmless if the verifier passes.

## What the Spark Job Does

1. Reads the Chapter 12 Clover, Square, and Toast CSV exports.
2. Normalizes them into a common line-item schema.
3. Joins POS item aliases to `master_items.csv`.
4. Reconstructs baskets using source POS, location, timestamp, and payment method.
5. Builds distinct sorted item arrays for baskets with at least two items.
6. Generates all item pairs in each basket.
7. Aggregates top co-purchased item pairs.

## Expected Output

The deterministic Chapter 12 input data produces:

| Metric | Value |
|---|---:|
| Reconstructed baskets | 15,819 |
| Baskets with at least two distinct items | 14,735 |
| Distinct item pairs | 435 |

The top pair is:

| item_a | item_b | basket_count |
|---|---|---:|
| `DRINK_001` | `DRINK_002` | 385 |

The verifier checks the summary metrics and the top 10 item pairs.

