# Demo Snakemake Audit Input

This directory contains an audit demo Snakefile for Snakebench.

The Snakefile provides declared resources and PSB-style annotations. Telemetry
for the demo comes from `../../data/`; benchmark TSV files are not required.

It represents rules for tools present in the current telemetry:

- `samtools`
- `bwa-mem2`
- `gzip`
- `awk`
- `wgsim`

Matching uses PSB annotations in `params`:

- `_psb_tool` matches telemetry `tool`
- `_psb_primary_cmd` can match telemetry `command`

This is an audit demo Snakefile, not a complete executable workflow.

Run:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --out examples/demo_snakemake/expected_audit_report.md
```
