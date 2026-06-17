"""DuckDB connection helper for the Chapter 12 pipeline."""

from __future__ import annotations

import pathlib

import duckdb

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATABASE = DATA / "sqlsushi.duckdb"


def connect(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Return a connection to the local Chapter 12 DuckDB database."""
    DATA.mkdir(exist_ok=True)
    return duckdb.connect(str(DATABASE), read_only=read_only)
