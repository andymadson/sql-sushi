# SQLMesh Plus GitHub Actions

This option runs the SQLMesh path from GitHub Actions.

Use it when the team chooses SQLMesh and wants repository-native automation for validation or scheduled runs without operating a separate scheduler service.

## Workflow Example

The example workflow is in:

```text
sqlmesh_chapter14.yml
```

Copy it into `.github/workflows/` if you want it active in a real repository.

## Tradeoff

GitHub Actions is simple for repo-centered validation and scheduled jobs. It is not a full data orchestrator: it does not model data assets, freshness, backfills, or operator workflows the way Airflow or Dagster can.
