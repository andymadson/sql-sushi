"""Run the Chapter 14 dbt Core path end to end."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
PROJECT_DIR = ROOT / "chapter_14_sql_transformation_frameworks" / "dbt"
PROFILES_DIR = PROJECT_DIR
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
    dbt = _tool("dbt")
    _run([sys.executable, str(PREPARE)])
    _run([dbt, "run", "--project-dir", str(PROJECT_DIR), "--profiles-dir", str(PROFILES_DIR)])
    _run([dbt, "test", "--project-dir", str(PROJECT_DIR), "--profiles-dir", str(PROFILES_DIR)])
    _run([sys.executable, str(VERIFY), "--label", "dbt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
