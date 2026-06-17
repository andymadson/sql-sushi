# SQLMesh Plus cron

This option runs the SQLMesh path from a standard cron entry.

Use it when the team chooses SQLMesh and wants the smallest reliable scheduler around a local or server-hosted checkout.

## Cron Example

```cron
15 2 * * * cd /path/to/sql-sushi && .venv/bin/python chapter_14_sql_transformation_frameworks/scripts/run_sqlmesh_path.py >> chapter_14_sql_transformation_frameworks/logs/sqlmesh-cron.log 2>&1
```

The command runs the SQLMesh path and exits non-zero if preparation, planning, or verification fails.

## Tradeoff

cron is simple and robust, but it does not provide a rich UI, task-level retry graph, or run catalog. SQLMesh still owns the model plan and environment behavior.
