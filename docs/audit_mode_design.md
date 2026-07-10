# Snakebench Audit Mode Design

Audit mode is the bridge between PSB-normalized telemetry and actual
Snakemake resource declarations. It compares declared resources in a Snakefile
against observed telemetry summaries and Snakebench's existing heuristic
suggestions.

## What Audit Mode Does

Audit mode reads a Snakefile and local telemetry, then produces a per-rule audit.
For each parsed rule it tries to answer:

- Does this rule have matching telemetry?
- Does the rule declare memory?
- Does the rule declare runtime?
- Are declared resources lower than Snakebench's telemetry-based suggestions?
- Are declared resources much higher than Snakebench's suggestions?

The intended command shape is:

```bash
snakebench audit Snakefile --telemetry data/
snakebench audit Snakefile --telemetry data/ --out reports/audit_report.md
```

The telemetry path is loaded through the normal Snakebench parquet loader, so
PSB normalization applies before auditing.

## What Audit Mode Does Not Do

Audit mode is not a full Snakemake execution engine or parser. It does not:

- execute Snakefiles;
- import workflow Python modules;
- expand wildcards;
- evaluate arbitrary Python expressions;
- inspect actual DAG jobs;
- run workflows;
- train or use ML models;
- upload data to PSB or any backend.

It is a local static audit for common rule shapes.

## Snakefile Parsing

The parser supports common static patterns such as:

```python
rule sort_bam:
    threads: 4
    benchmark:
        "benchmarks/sort_bam.tsv"
    resources:
        mem_mb=2000,
        runtime="00:30:00"
    params:
        _psb_tool="samtools",
        _psb_primary_cmd="sort",
```

It also supports simple one-line variants when values are literal and easy to
parse. Values that are dynamic, computed, function calls, variables, or otherwise
not simple literals are left as `None`.

This is deliberate. Audit mode supports common static Snakefile patterns, not every
possible dynamic Python/Snakemake expression.

## Rule Matching

Rules are matched to telemetry in this order:

1. If telemetry has `rule_name`, match `rule_name`.
2. Else if a rule has `_psb_tool`, match telemetry `tool`.
3. Else if a rule has `_psb_primary_cmd` and telemetry has `command`, match
   telemetry `command`.
4. Otherwise mark the rule as unmatched.

PSB annotations improve matching because tool names and primary commands are
more stable than trying to infer tool identity from shell text.

## Audit Statuses

Audit rows can report one or more semicolon-separated statuses:

- `unmatched`: no telemetry matched the rule.
- `insufficient_data`: fewer than 3 telemetry observations matched.
- `missing_mem`: the rule has no parsed memory declaration.
- `missing_runtime`: the rule has no parsed runtime declaration.
- `underrequested_mem`: suggested memory is more than 10% above declared memory.
- `underrequested_runtime`: suggested runtime is more than 10% above declared runtime.
- `overrequested_mem`: declared memory is more than 2x suggested memory.
- `overrequested_runtime`: declared runtime is more than 2x suggested runtime.
- `ok`: telemetry exists and no configured issue was detected.

Statuses are heuristic signals, not hard scheduling truth.

## Limitations

- Static parsing can miss dynamic Snakefile constructs.
- Matching is best-effort and depends on rule names, PSB annotations, or command
  fields being present.
- The resource suggestions come from robust statistics and safety multipliers,
  not a learned model.
- The current telemetry may be too small or too environment-specific for broad
  conclusions.
- Audit mode does not parse full `inputs` / `outputs` file-entry JSON or perform
  workflow-wide DAG analysis.
