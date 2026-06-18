"""Run the Chapter 14 SQLMesh path end to end."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
PROJECT_DIR = ROOT / "chapter_14_sql_transformation_frameworks" / "sqlmesh"
PREPARE = ROOT / "chapter_14_sql_transformation_frameworks" / "scripts" / "prepare_raw_data.py"
VERIFY = (
    ROOT
    / "chapter_14_sql_transformation_frameworks"
    / "scripts"
    / "verify_framework_counts.py"
)


def _tool(name: str) -> str:
    scripts_dir = pathlib.Path(sys.executable).resolve().parent
    candidates = [scripts_dir / f"{name}.exe", scripts_dir / name]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(f"Could not find {name!r}. Install Chapter 14 requirements first.")


def _run(command: list[str]) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    sqlmesh = _tool("sqlmesh")
    _run([sys.executable, str(PREPARE)])
    _run([sqlmesh, "-p", str(PROJECT_DIR), "plan", "--auto-apply", "--no-prompts"])
    _run([sys.executable, str(VERIFY), "--label", "sqlmesh"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
