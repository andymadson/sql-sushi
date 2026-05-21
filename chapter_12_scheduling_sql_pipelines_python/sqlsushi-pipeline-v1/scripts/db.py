"""Postgres connection helper.

Reads credentials from the local .env file and environment variables.
There is no fallback to hardcoded defaults on purpose. The runner
refuses to start if the required variables aren't set.
"""

from __future__ import annotations

import os
import pathlib

import psycopg

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

REQUIRED_ENV_VARS = (
    "PG_HOST",
    "PG_PORT",
    "PG_DATABASE",
    "PG_USER",
    "PG_PASSWORD",
)


def _load_env_file(path: pathlib.Path = ENV_FILE) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip("\"'"))


def connection_string() -> str:
    _load_env_file()
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". See .env.example."
        )
    return (
        f"host={os.environ['PG_HOST']} "
        f"port={os.environ['PG_PORT']} "
        f"dbname={os.environ['PG_DATABASE']} "
        f"user={os.environ['PG_USER']} "
        f"password={os.environ['PG_PASSWORD']}"
    )


def connect() -> psycopg.Connection:
    """Return a new autocommit-off Connection. Caller is responsible for
    closing it (use a `with` block)."""
    return psycopg.connect(connection_string())
