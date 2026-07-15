# Audit Flow

Main command:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/
```

Question answered:

```text
Given a Snakefile and PSB-style telemetry, which resource declarations should be fixed?
```

## Inputs

Snakefile:

- rule names;
- declared `threads`;
- declared `resources.mem_mb`;
- declared `resources.runtime`;
- optional `_psb_tool`;
- optional `_psb_primary_cmd`.

Telemetry parquet:

- `tool`;
- `command`;
- `runtime_sec`;
- `max_rss_mb`;
- `threads`;
- `input_size`;
- `output_size`;
- `resources`;
- `rule_name`, when available.

`data/` is a small sample telemetry corpus. It is not proof that the demo Snakefile produced those rows.

## Matching

For each Snakefile rule, Snakebench tries:

1. `rule_name` equals the Snakefile rule name.
2. Snakefile `_psb_tool` equals telemetry `tool`.
3. Snakefile `_psb_primary_cmd` equals telemetry `command`.

`rule_name` is the clean match. Tool-only matching is a fallback and can mix unrelated rules that call the same tool.

## Resource Check

For matched rows:

- observed memory = p95 of `max_rss_mb`;
- `required_mem_mb = observed_p95_memory_mb * 1.25`;
- `suggested_mem_mb` is rounded up to the scheduler quantum;
- observed runtime = p90 of `runtime_sec`;
- `required_runtime_sec = ceil(observed_p90_runtime_sec * 1.5)`.

Audit status uses required values, not rounded suggestions.

Statuses:

- `missing_mem`;
- `missing_runtime`;
- `underrequested_mem`;
- `underrequested_runtime`;
- `overrequested_mem`;
- `overrequested_runtime`;
- `ok`;
- `unmatched`;
- `insufficient_data`.

## Outputs

Terminal:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/
```

Markdown:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --out reports/audit_report.md
```

CSV and charts:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --csv reports/audit_table.csv --charts reports/audit_charts
```
