# Technical Summary

Snakebench is a local CLI/library for auditing Snakemake resource declarations against exported telemetry.

## Main Code Paths

- `cli.py`: command definitions.
- `load.py`: parquet loading.
- `psb.py`: PSB-style field normalization.
- `snakefile.py`: static Snakefile resource parser.
- `matching.py`: rule-to-telemetry matching.
- `resource_estimation.py`: memory/runtime formulas.
- `audit.py`: audit table construction.
- `audit_metrics.py`: status counts and summary metrics.
- `audit_export.py`: Markdown and CSV exports.
- `charts.py`: optional PNG chart exports.

Secondary commands still exist in code:

- `summarize`;
- `advise`;
- `dry`;
- `report`.

They are not the main project story right now.

## Current Audit Logic

Matching order:

1. telemetry `rule_name`;
2. Snakefile `_psb_tool` against telemetry `tool`;
3. Snakefile `_psb_primary_cmd` against telemetry `command`;
4. unmatched.

Memory:

- observed = p95 of `max_rss_mb`;
- required = observed * 1.25;
- suggested = required rounded up to scheduler-friendly MB.

Runtime:

- observed = p90 of `runtime_sec`;
- required = ceil(observed * 1.5);
- suggested = required formatted as `HH:MM:SS`.

Status comparison uses required values. Rounded suggestions are for output, not for deciding whether a rule is underrequested.

## Main Limitations

- Snakefile parsing is static and does not execute arbitrary Python.
- Tool-only matching is coarse.
- Current estimates are heuristics, not a predictive model.
- Failed/OOM rows are preserved but not deeply modeled.
- Environment metadata is preserved but not yet used for environment-aware advice.

## Validation Commands

Tests:

```bash
python -m pytest tests/ -v
```

Audit smoke:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --csv reports/audit_table.csv --charts reports/audit_charts
```
