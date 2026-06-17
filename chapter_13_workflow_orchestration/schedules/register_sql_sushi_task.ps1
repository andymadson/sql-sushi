# Example Windows Task Scheduler registration for Chapter 13.
# Run this from the repo root after creating .venv and installing dependencies.

$repoRoot = (Get-Location).Path
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$script = Join-Path $repoRoot "chapter_13_workflow_orchestration\scripts\run_scheduled_pipeline.py"
$logFile = Join-Path $repoRoot "chapter_13_workflow_orchestration\logs\nightly.log"

$action = New-ScheduledTaskAction `
    -Execute $python `
    -Argument "`"$script`" --log-file `"$logFile`" --quiet" `
    -WorkingDirectory $repoRoot

$trigger = New-ScheduledTaskTrigger -Daily -At 2:15am

Register-ScheduledTask `
    -TaskName "SQL-Sushi Chapter 13 Pipeline" `
    -Action $action `
    -Trigger $trigger `
    -Description "Runs the SQL-Sushi Chapter 12 DuckDB pipeline through the Chapter 13 scheduler wrapper."
