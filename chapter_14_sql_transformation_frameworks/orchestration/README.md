# Chapter 14 Orchestration Pairings

Chapter 14 demonstrates dbt Core and SQLMesh as alternative transformation frameworks. It also shows four common ways those frameworks are operated.

These pairings are examples, not one combined production stack:

- `airflow_dbt/`: Airflow schedules and observes the dbt Core path.
- `dagster_sqlmesh/`: Dagster schedules and observes the SQLMesh path.
- `sqlmesh_cron/`: cron runs the SQLMesh path with the smallest operating surface.
- `sqlmesh_github_actions/`: GitHub Actions runs the SQLMesh path from repository automation.

For a real project, choose one transformation framework and one operating pattern that matches the team's needs.
