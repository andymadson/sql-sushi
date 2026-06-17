# Chapter 13: Workflow Orchestration

Chapter 12 gave SQL-Sushi Co. a local DuckDB pipeline that runs on demand. This chapter adds the first orchestration layer: a schedulable command that CRON or Windows Task Scheduler can wake up.

The wrapper stays deliberately small. It doesn't replace the runner with Airflow or Dagster. It prepares deterministic local data, runs the Chapter 12 pipeline, verifies the expected counts, writes a job log, and exits non-zero if anything fails.

## What's Here

```text
chapter_13_workflow_orchestration/
|-- README.md
|-- requirements.txt
|-- schedules/
|   |-- sql_sushi_pipeline.cron.example
|   `-- register_sql_sushi_task.ps1
`-- scripts/
    `-- run_scheduled_pipeline.py
```

Generated logs are written to `logs/` at runtime.

## Quick Start

Run these commands from the repo root.

```bash
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

```bash
. .venv/bin/activate
```

Install dependencies and run the scheduled-job wrapper once:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt -r chapter_12_scheduling_sql_pipelines_python/requirements.txt -r chapter_13_workflow_orchestration/requirements.txt
python chapter_13_workflow_orchestration/scripts/run_scheduled_pipeline.py --log-file chapter_13_workflow_orchestration/logs/manual-run.log
```

That command runs the same Chapter 12 sequence the scheduler will run:

1. Build seed data.
2. Generate deterministic POS source CSVs.
3. Run the DuckDB pipeline.
4. Verify expected CSV, relation, and pipeline metadata counts.

The wrapper is successful only when the verifier passes.

## Schedule It on Mac or Linux

Open your crontab:

```bash
crontab -e
```

Add a line like this, replacing `/path/to/sql-sushi` with the absolute path to your checkout:

```cron
15 2 * * * cd /path/to/sql-sushi && .venv/bin/python chapter_13_workflow_orchestration/scripts/run_scheduled_pipeline.py --log-file chapter_13_workflow_orchestration/logs/nightly.log --quiet
```

That runs the pipeline every day at 2:15 a.m. local time.

## Schedule It on Windows

PowerShell uses Task Scheduler rather than CRON. From the repo root, after the virtual environment exists and dependencies are installed, run:

```powershell
.\chapter_13_workflow_orchestration\schedules\register_sql_sushi_task.ps1
```

That registers a daily 2:15 a.m. task named `SQL-Sushi Chapter 13 Pipeline`.

## Where GitHub Actions Fits

This repo's CI workflow already runs the Chapter 13 wrapper on push and pull request events. You could also run the same command from a manually triggered `workflow_dispatch` workflow or from a scheduled workflow for a small repo-centered job. GitHub's docs cover event-based, manual, and scheduled workflow triggers. https://docs.github.com/actions/using-workflows/events-that-trigger-workflows and https://docs.github.com/actions/managing-workflow-runs/manually-running-a-workflow

Don't treat that as a replacement for Airflow or Dagster. Actions is useful for code validation, demos, and lightweight repo automation. It doesn't model data assets, dependency graphs, freshness, or operational backfills the way a data orchestrator is meant to.

## Expected Result

The scheduled wrapper should end with:

```text
All expected counts verified.
```

It also appends a line like this to the configured log file:

```text
[2026-06-17T19:30:00+00:00] SCHEDULED JOB SUCCEEDED
```

If any step fails, the wrapper stops at that step, writes `SCHEDULED JOB FAILED`, and returns the failing exit code. That failure behavior is what makes the script useful to CRON and Task Scheduler. A scheduler doesn't need to understand DuckDB. It needs an exit code it can trust.

## Why Not Airflow or Dagster Yet?

Airflow and Dagster solve real problems: retries, dependency graphs, backfills, observability, alerts, asset catalogs, and deployment discipline. They also add services, configuration, packaging, and operational work.

Chapter 13 starts with CRON because SQL-Sushi's current pipeline is still one linear local job. The moment the team needs per-step retries, dependency-aware backfills, multiple environments, or a UI for operators, the tradeoff changes.

Start with the scheduler that matches the pipeline you actually have.
