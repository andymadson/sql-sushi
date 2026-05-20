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

The wrong kind of pull request: rewriting Chapter 12's runner to use Airflow because Airflow is "better." Chapter 13 covers that already. Each version of the pipeline (`sqlsushi-pipeline-v1`, `v2`, `v3`, `v4`) is deliberately at a specific level of sophistication.

## Development setup

Most chapters use Python 3.12+, Docker, and a pinned set of libraries declared in each chapter's `requirements.txt`. Set up each chapter independently:

```bash
cd chapter_12_scheduling_sql_pipelines_python/sqlsushi-pipeline-v1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running checks locally

The CI workflow runs `ruff check` against every chapter's Python code and parses every `.sql` file with `sqlglot` to catch syntax errors. Before opening a PR, please run both locally from the repo root:

```bash
pip install ruff sqlglot
ruff check chapter_*/
find chapter_* -name "*.sql" -exec python3 -c \
  "import sys, sqlglot; sqlglot.parse(open(sys.argv[1]).read(), dialect='postgres')" {} \;
```

If you're touching a chapter's runnable pipeline, run it end to end and confirm the expected outputs documented in that chapter's README still match.

## What this repo isn't

It isn't a place to discuss general data engineering topics. Open a discussion on the book's O'Reilly forum for that, or reach out to [@andymadson](https://github.com/andymadson) directly.

It isn't a fork base for new pipelines unrelated to the book. That's what the MIT license is for: take what's useful and build your own thing.
