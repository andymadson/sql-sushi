-- Pipeline-run metadata. Two tables, deliberately simple. The runner writes
-- one row per pipeline invocation and one row per step within that
-- invocation. Chapter 10's observability stack consumes these tables; for
-- now we want to be able to answer "did it run, how long did it take, what
-- failed" by running plain SQL.

CREATE TABLE IF NOT EXISTS pipeline.pipeline_runs (
    run_id        TEXT        PRIMARY KEY,
    started_at    TIMESTAMP   NOT NULL,
    completed_at  TIMESTAMP,
    status        TEXT        NOT NULL CHECK (status IN ('running', 'success', 'failed')),
    error_text    TEXT
);

CREATE TABLE IF NOT EXISTS pipeline.step_runs (
    run_id         TEXT        NOT NULL REFERENCES pipeline.pipeline_runs (run_id),
    step_name      TEXT        NOT NULL,
    step_order     INTEGER     NOT NULL,
    started_at     TIMESTAMP   NOT NULL,
    completed_at   TIMESTAMP,
    status         TEXT        NOT NULL CHECK (status IN ('running', 'success', 'failed', 'skipped')),
    rows_affected  BIGINT,
    error_text     TEXT,
    PRIMARY KEY (run_id, step_name)
);

CREATE INDEX IF NOT EXISTS ix_step_runs_started_at
    ON pipeline.step_runs (started_at);
