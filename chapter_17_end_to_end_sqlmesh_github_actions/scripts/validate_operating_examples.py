"""Validate the Chapter 17 operating examples."""

from __future__ import annotations

import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER = ROOT / "chapter_17_end_to_end_sqlmesh_github_actions"
FILES = {
    "github_actions": CHAPTER / "github_actions" / "sqlmesh_chapter17.yml",
    "cron": CHAPTER / "cron" / "sql_sushi_chapter17.cron.example",
}


def _read(path: pathlib.Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing expected file: {path}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    active_workflow = ROOT / ".github" / "workflows" / "sqlmesh_chapter17.yml"
    if active_workflow.exists():
        errors.append(
            "Chapter 17 workflow should be a copyable example, "
            f"not active: {active_workflow}"
        )

    required_text = {
        "github_actions": [
            "workflow_dispatch:",
            "schedule:",
            "actions/checkout@v6",
            "actions/setup-python@v6",
            "chapter_17_end_to_end_sqlmesh_github_actions/scripts/run_pipeline.py",
        ],
        "cron": [
            "15 2 * * *",
            "chapter_17_end_to_end_sqlmesh_github_actions/scripts/run_pipeline.py",
            "chapter_17_end_to_end_sqlmesh_github_actions/logs/sqlmesh-chapter17.log",
        ],
    }

    for key, required_items in required_text.items():
        try:
            text = _read(FILES[key])
        except Exception as exc:
            errors.append(str(exc))
            continue
        for item in required_items:
            if item not in text:
                errors.append(f"{FILES[key]}: missing {item!r}")

    if errors:
        print("Chapter 17 operating example validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Chapter 17 operating examples verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
