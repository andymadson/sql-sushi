# Chapter 16: Real-Time Data Transformation

Chapter 16 keeps real-time work small enough to run on a laptop. It does not build a streaming platform. It uses deterministic SQL-Sushi event batches to show the operating patterns that matter before you pick a streaming engine.

The exercise covers:

- event time versus arrival time
- micro-batch ingestion
- idempotent file processing
- allowed lateness and watermarks
- late-event capture
- 15-minute sales aggregates

## What's Here

```text
chapter_16_real_time_data_transformation/
|-- README.md
|-- requirements.txt
`-- scripts/
    |-- prepare_event_batches.py
    |-- run_micro_batches.py
    `-- verify_real_time_outputs.py
```

Chapter 16 generated files are written under `chapter_16_real_time_data_transformation/data/` and are ignored by Git:

- `events_batch_*.csv`
- `real_time.duckdb`
- `real_time_summary.json`
- `sales_15min_by_location.csv`
- `late_events.csv`

The preparation script also refreshes the Chapter 12 seed reference data because this example reuses SQL-Sushi master item identifiers.

## Requirements

- Python 3.12
- DuckDB

## Quick Start

Run these commands from the repo root.

Mac/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install \
  -r requirements-dev.txt \
  -r chapter_12_scheduling_sql_pipelines_python/requirements.txt \
  -r chapter_16_real_time_data_transformation/requirements.txt
.venv/bin/python chapter_16_real_time_data_transformation/scripts/prepare_event_batches.py
.venv/bin/python chapter_16_real_time_data_transformation/scripts/run_micro_batches.py --reset
.venv/bin/python chapter_16_real_time_data_transformation/scripts/run_micro_batches.py
.venv/bin/python chapter_16_real_time_data_transformation/scripts/verify_real_time_outputs.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install `
  -r requirements-dev.txt `
  -r chapter_12_scheduling_sql_pipelines_python\requirements.txt `
  -r chapter_16_real_time_data_transformation\requirements.txt
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\prepare_event_batches.py
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\run_micro_batches.py --reset
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\run_micro_batches.py
.\.venv\Scripts\python.exe chapter_16_real_time_data_transformation\scripts\verify_real_time_outputs.py
```

The second `run_micro_batches.py` call is intentional. It proves the runner is idempotent: already-processed batch files are skipped, and the outputs stay stable.

## What the Micro-Batch Runner Does

1. Reads deterministic event batch CSV files.
2. Tracks processed file names in DuckDB.
3. Maintains the maximum event time seen so far.
4. Computes a 30-minute event-time watermark.
5. Accepts events at or after the watermark.
6. Writes older arrivals to `late_events.csv`.
7. Rebuilds current 15-minute sales aggregates from accepted events.
8. Writes a summary JSON and machine-checkable CSV outputs.

The watermark is a late-arrival cutoff. The aggregate CSV is a current accepted-event view, not a list of only finalized windows.

## Expected Output

The deterministic event batches produce:

| Metric | Value |
|---|---:|
| Processed files | 4 |
| Accepted events | 27 |
| Late events | 3 |
| Aggregate rows | 6 |
| Accepted gross sales | `$352.50` |
| Current watermark | `2026-04-01 12:09:00` |

The verifier checks the summary, the late event IDs, and every 15-minute aggregate row.
