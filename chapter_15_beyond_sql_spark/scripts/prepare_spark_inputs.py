"""Prepare the deterministic Chapter 12 CSV inputs for Chapter 15."""

from __future__ import annotations

import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_12 = REPO_ROOT / "chapter_12_scheduling_sql_pipelines_python"


def _run(script_name: str) -> None:
    script = CHAPTER_12 / "scripts" / script_name
    subprocess.run([sys.executable, str(script)], cwd=REPO_ROOT, check=True)


def main() -> int:
    _run("build_seed_data.py")
    _run("generate_data.py")
    print("prepared Chapter 12 CSV inputs for Chapter 15 Spark example")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
