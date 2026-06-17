-- Four schemas, one purpose each. Idempotent so the runner can call this
-- on every startup without breaking.
--
-- raw       Landing zone for source extracts. One table per POS, kept close
--           to the source shape on purpose so reloads stay easy.
-- staging   Cleaned, typed, unified data. One row per real POS line item,
--           same columns regardless of POS.
-- analytics fact_sales plus the daily menu sales grain and aggregate marts
--           the analysts query directly.
-- pipeline  Metadata about the runner itself: what ran, when, how long,
--           how many rows moved.

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS pipeline;
