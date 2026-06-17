"""The ordered list of pipeline steps.

A step is a SQL file (executed in one transaction) or a Python callable
(for tasks that aren't pure SQL, like loading CSVs through COPY). The
runner walks this list in order and writes one row per step into
pipeline.step_runs.

If you change the step list, the runner picks it up on the next run.
That's the whole point.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Callable

import duckdb

import load_raw

ROOT = pathlib.Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"


@dataclass(frozen=True)
class Step:
    name: str
    # Exactly one of sql_file or python_callable is set.
    sql_file: pathlib.Path | None = None
    python_callable: Callable[[duckdb.DuckDBPyConnection], dict[str, int]] | None = None
    row_count_relation: str | None = None


STEPS: list[Step] = [
    Step("create_schemas",         sql_file=SQL_DIR / "00_create_schemas.sql"),
    Step("raw_ddl",                sql_file=SQL_DIR / "10_raw_ddl.sql"),
    Step("pipeline_metadata_ddl",  sql_file=SQL_DIR / "30_pipeline_metadata.sql"),
    Step("load_raw",               python_callable=load_raw.main),
    Step("stg_pos_transactions",   sql_file=SQL_DIR / "staging" / "stg_pos_transactions.sql",
         row_count_relation="staging.stg_pos_transactions"),
    Step("fact_sales",             sql_file=SQL_DIR / "analytics" / "fact_sales.sql",
         row_count_relation="analytics.fact_sales"),
    Step("agg_daily_sales_by_location",
         sql_file=SQL_DIR / "analytics" / "agg_daily_sales_by_location.sql",
         row_count_relation="analytics.agg_daily_sales_by_location"),
    Step("agg_top_items_30d",
         sql_file=SQL_DIR / "analytics" / "agg_top_items_30d.sql",
         row_count_relation="analytics.agg_top_items_30d"),
]
