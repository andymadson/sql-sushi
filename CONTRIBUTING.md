# Contributing to sql-sushi

Thanks for taking the time to contribute. This repository holds the companion code for *Data Transformation: The Definitive Guide* (O'Reilly, 2026). The book is the source of truth; this code exists so readers can run the examples and learn by doing.

## Reporting errata

If you found a typo, bug, or factual error:

1. Check [existing issues](../../issues) to see if it's already been reported.
2. Open a new issue using the [Erratum template](../../issues/new?template=erratum.md).
3. Include the chapter, page or section reference, and a clear description of what you observed versus what you expected.

## Suggesting improvements to the code

The code in each chapter is meant to teach a specific point clearly. The right kind of pull request:

- **Targets a single chapter.** Cross-chapter changes are hard to review and almost always indicate a discussion that should happen in an issue first.
- **Explains what changed and why.** A one-paragraph description in the PR body, with a link to the issue if there is one.
- **Doesn't break the chapter's expected output.** Each chapter's README has a section listing the row counts, file sizes, or query results readers should see after running the code. If your change alters those numbers, the change is probably out of scope.
- **Stays in the chapter's voice.** This is book code, not production code. Optimizations and abstractions that obscure what the code is teaching are usually the wrong direction.

The wrong kind of pull request: rewriting Chapter 12's runner to use Airflow because Airflow is "better." Chapter 13 covers orchestration. Chapter 12 is deliberately the small local DuckDB runner that everything else builds from.

## Development setup

Runnable chapters use Python 3.12 and pinned dependencies. Chapter 12 doesn't require Docker or an external database. From the repo root:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt -r chapter_12_scheduling_sql_pipelines_python/requirements.txt
```

## Running checks locally

The CI workflow runs Ruff, parses Chapter 12 SQL with SQLGlot's DuckDB dialect, and runs the Chapter 12 pipeline end to end. Before opening a PR, run the same checks locally from the repo root:

```bash
python -m ruff check chapter_12_scheduling_sql_pipelines_python
python -c 'import pathlib, sqlglot; [sqlglot.parse(path.read_text(encoding="utf-8"), dialect="duckdb") for path in pathlib.Path("chapter_12_scheduling_sql_pipelines_python/sql").rglob("*.sql")]'
python chapter_12_scheduling_sql_pipelines_python/scripts/build_seed_data.py
python chapter_12_scheduling_sql_pipelines_python/scripts/generate_data.py
python chapter_12_scheduling_sql_pipelines_python/scripts/runner.py
python chapter_12_scheduling_sql_pipelines_python/scripts/verify_counts.py
```

Chapter 12 writes generated CSV files and `data/sqlsushi.duckdb` under `chapter_12_scheduling_sql_pipelines_python/data/`. Those files are local artifacts. Don't commit them.

## What this repo isn't

It isn't a place to discuss general data engineering topics. Open a discussion on the book's O'Reilly forum for that, or reach out to [@andymadson](https://github.com/andymadson) directly.

It isn't a fork base for new pipelines unrelated to the book. That's what the MIT license is for: take what's useful and build your own thing.
