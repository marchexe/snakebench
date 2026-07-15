# Purpose

Snakebench is a downstream local audit layer for PSB-style Snakemake telemetry.

# Data Flow

Snakemake workflow
-> `snakemake-logger-plugin-benchmark-telemetry`
-> PSB-style telemetry export
-> Snakebench

# Module Boundaries

- `load.py`: load local parquet telemetry files.
- `psb.py`: normalize PSB-style fields while preserving source columns.
- `schema.py`: centralize telemetry column names and lookup helpers.
- `features.py`: derive local feature columns such as input-size bins.
- `summarize.py`: summarize observed runtime and memory by tool.
- `resources.py`: shared memory, runtime, gap, and ratio calculations.
- `advise.py`: build percentile-based resource suggestions.
- `snakefile.py`: parse simple static Snakefile resource declarations.
- `matching.py`: match Snakefile rules to telemetry in audit priority order.
- `audit.py`: compare declared rule resources against observed telemetry.
- `audit_metrics.py`: aggregate audit result counts.
- `audit_export.py`: write audit Markdown and CSV artifacts.
- `charts.py`: write optional audit PNG charts.
- `readiness.py`: inspect telemetry completeness and PSB compatibility.
- `report.py`: build Markdown summary reports.
- `cli.py`: command-line entry point.

# Audit Semantics

- Observed memory uses p95 of `max_rss_mb`.
- `required_mem_mb` is observed p95 memory multiplied by the safety factor.
- `suggested_mem_mb` rounds `required_mem_mb` up to the scheduler quantum.
- Observed runtime uses p90 of `runtime_sec`.
- `required_runtime_sec` is observed p90 runtime multiplied by the safety factor and rounded up.
- Audit status compares declared memory against `required_mem_mb`, not rounded `suggested_mem_mb`.
- Audit status compares declared runtime against `required_runtime_sec`.

This means a small rule can have `required_mem_mb` near 10 MB and `suggested_mem_mb` of 256 MB. The status should treat a declaration above 10 MB as aligned even though the scheduler-friendly suggestion is 256 MB.

# Matching Strategy

Audit matching is best-effort and uses this priority:

1. `rule_name` if telemetry has `rule_name`.
2. `_psb_tool` against telemetry `tool`.
3. `_psb_primary_cmd` against telemetry `command`.
4. `unmatched`.

# Non-Goals

Currently not implemented:

- ML prediction.
- Web dashboard.
- PSB server.
- Telemetry collection.
- Workflow execution.
- Full Snakemake parser.
