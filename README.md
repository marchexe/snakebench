# Snakebench

Snakebench checks Snakemake resource declarations against a PSB-style telemetry corpus.

I made it because `mem_mb` and `runtime` in Snakefiles are often guessed. If we collect telemetry from real runs, we can use it to find rules where the declared resources are missing, too low, too high, or roughly fine.

This is not a predictor yet. It is an audit tool.

## Main Command

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/
```

Inputs:

- `examples/demo_snakemake/Snakefile`: demo rules with declared `threads`, `mem_mb`, `runtime`, and `_psb_*` hints.
- `data/`: small sample of PSB-style telemetry. In the real use case this would be a larger shared telemetry export.

Output:

- terminal audit table.

See [audit flow](docs/audit_flow.md) for the step-by-step path from Snakefile and telemetry to the audit table.

## What Happens

1. Read declared resources from the Snakefile.
2. Load telemetry rows from parquet files.
3. Match each Snakefile rule to telemetry.
4. Estimate required memory and runtime from matched observations.
5. Compare declared values with required values.
6. Report missing, underrequested, overrequested, aligned, or unmatched rules.

## Matching

Best match:

- telemetry has `rule_name`, and it equals the Snakefile rule name.

Fallbacks:

- Snakefile `params._psb_tool` matches telemetry `tool`.
- Snakefile `params._psb_primary_cmd` matches telemetry `command`.

The demo mostly uses `_psb_tool`, so it is a coarse example. For a real shared telemetry corpus, `rule_name` is the most important upstream field to add.

See [telemetry contract](docs/telemetry_contract.md) for the PSB fields Snakebench uses and the upstream fields that matter most.

## Exports

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --out reports/audit_report.md
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --csv reports/audit_table.csv
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --charts reports/audit_charts
```

Generated audit artifacts:

- `reports/audit_report.md`
- `reports/audit_table.csv`
- `reports/audit_charts/status_counts.png`
- `reports/audit_charts/declared_vs_required_memory_mb.png`
- `reports/audit_charts/declared_vs_required_runtime_sec.png`

## What It Does Not Do

- does not run Snakemake;
- does not collect or submit telemetry;
- does not rewrite Snakefiles;
- does not train ML models;
- does not run a backend or dashboard.

## Current Limits

- Tool-only matching can mix unrelated rules that call the same tool.
- The Snakefile parser handles simple static declarations, not arbitrary Python logic.
- Required resources are heuristic: memory p95 with a margin, runtime p90 with a margin.
- The sample `data/` directory is only a tiny stand-in for the larger telemetry corpus this is meant to audit against.

See [technical summary](docs/technical_summary.md) for module names, formulas, and validation commands.
