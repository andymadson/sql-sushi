"""Run the Chapter 12 pipeline as a schedulable job.

This is the smallest orchestration layer worth showing. cron or Task Scheduler
wakes up this script. The script prepares deterministic local data, runs the
Chapter 12 pipeline, verifies the expected counts, writes one job log, and exits
non-zero on failure.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER_12 = REPO_ROOT / "chapter_12_scheduling_sql_pipelines_python"
DEFAULT_LOG = (
    REPO_ROOT
    / "chapter_13_workflow_orchestration"
    / "logs"
    / "scheduled-pipeline.log"
)


def _timestamp() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def _run_step(
    command: list[str],
    label: str,
    log_file: pathlib.Path,
    echo: bool,
) -> int:
    header = f"\n[{_timestamp()}] START {label}\n$ {' '.join(command)}\n"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8", newline="\n") as f:
        f.write(header)
        f.flush()
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        f.write(result.stdout)
        f.write(f"[{_timestamp()}] END {label} exit={result.returncode}\n")

    if echo:
        print(header, end="")
        print(result.stdout, end="")
        print(f"[{_timestamp()}] END {label} exit={result.returncode}")

    return result.returncode


def _chapter_12_script(name: str) -> str:
    return str(CHAPTER_12 / "scripts" / name)


def run_scheduled_pipeline(
    log_file: pathlib.Path,
    skip_data_prep: bool,
    echo: bool,
) -> int:
    steps = []
    if not skip_data_prep:
        steps.extend(
            [
                ("build seed data", _chapter_12_script("build_seed_data.py")),
                ("generate source data", _chapter_12_script("generate_data.py")),
            ]
        )
    steps.extend(
        [
            ("run pipeline", _chapter_12_script("runner.py")),
            ("verify expected counts", _chapter_12_script("verify_counts.py")),
        ]
    )

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"\n[{_timestamp()}] SCHEDULED JOB START\n")

    for label, script in steps:
        exit_code = _run_step([sys.executable, script], label, log_file, echo)
        if exit_code != 0:
            with log_file.open("a", encoding="utf-8", newline="\n") as f:
                f.write(f"[{_timestamp()}] SCHEDULED JOB FAILED at {label}\n")
            return exit_code

    with log_file.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"[{_timestamp()}] SCHEDULED JOB SUCCEEDED\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the SQL-Sushi Chapter 12 pipeline as a scheduled job."
    )
    parser.add_argument(
        "--log-file",
        type=pathlib.Path,
        default=DEFAULT_LOG,
        help="Path for the scheduled job log.",
    )
    parser.add_argument(
        "--skip-data-prep",
        action="store_true",
        help="Run only the pipeline and verifier. Use this when source CSVs exist.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Write the log file without also echoing command output.",
    )
    args = parser.parse_args()

    return run_scheduled_pipeline(
        log_file=args.log_file,
        skip_data_prep=args.skip_data_prep,
        echo=not args.quiet,
    )


if __name__ == "__main__":
    sys.exit(main())
