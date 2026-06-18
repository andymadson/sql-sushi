"""Run the Chapter 17 SQLMesh pipeline end to end."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

import duckdb


ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAPTER = ROOT / "chapter_17_end_to_end_sqlmesh_github_actions"
CHAPTER_12 = ROOT / "chapter_12_scheduling_sql_pipelines_python"
CHAPTER_12_SCRIPTS = CHAPTER_12 / "scripts"
CHAPTER_12_SQL = CHAPTER_12 / "sql"
DATABASE = CHAPTER / "data" / "sqlsushi_end_to_end.duckdb"
PROJECT_DIR = CHAPTER / "sqlmesh"
VERIFY = CHAPTER / "scripts" / "verify_outputs.py"

sys.path.insert(0, str(CHAPTER_12_SCRIPTS))

import build_seed_data  # noqa: E402
import generate_data  # noqa: E402
import load_raw  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)


def _tool(name: str) -> str:
    scripts_dir = pathlib.Path(sys.executable).resolve().parent
    candidates = [scripts_dir / f"{name}.exe", scripts_dir / name]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(
        f"Could not find {name!r}. Install Chapter 17 requirements first."
    )


def _run(command: list[str]) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def _execute_sql_file(conn: duckdb.DuckDBPyConnection, path: pathlib.Path) -> None:
    conn.execute(path.read_text(encoding="utf-8"))


def _prepare_raw_data() -> None:
    build_seed_data.main()
    generate_data.main()

    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DATABASE)) as conn:
        _execute_sql_file(conn, CHAPTER_12_SQL / "00_create_schemas.sql")
        _execute_sql_file(conn, CHAPTER_12_SQL / "10_raw_ddl.sql")
        conn.execute("BEGIN")
        try:
            counts = load_raw.main(conn)
        except Exception:
            conn.execute("ROLLBACK")
            raise
        conn.execute("COMMIT")

    print("prepared Chapter 17 raw tables")
    for table, row_count in counts.items():
        print(f"{table}: {row_count}")


def main() -> int:
    sqlmesh = _tool("sqlmesh")
    _prepare_raw_data()
    _run([sqlmesh, "-p", str(PROJECT_DIR), "plan", "--auto-apply", "--no-prompts"])
    _run([sys.executable, str(VERIFY)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
