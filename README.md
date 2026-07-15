# Snakebench Advisor

Snakebench checks whether Snakemake resource declarations match observed PSB-style telemetry.

Main command:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/
```

Audit outputs can be written as:

- terminal table
- CSV table
- PNG charts
- Markdown report

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --csv reports/audit_table.csv
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --charts reports/audit_charts
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --out reports/audit_report.md
```

## How It Works

1. Load PSB-style telemetry from local parquet files.
2. Parse declared resources and PSB-style annotations from a Snakefile.
3. Match Snakefile rules to telemetry rows.
4. Compare declared memory/runtime with observed telemetry.
5. Export the audit results.

See [docs/walkthrough.md](docs/walkthrough.md) for a concrete example and [docs/architecture.md](docs/architecture.md) for module boundaries.

## Demo

`examples/demo_snakemake/` contains an audit demo Snakefile for `samtools`, `bwa-mem2`, `gzip`, `awk`, and `wgsim`.

The Snakefile provides declared resources and PSB-style annotations. Telemetry comes from `data/`; benchmark TSV files are not required.

This is an audit demo Snakefile, not a complete executable workflow.

## Secondary Commands

- `snakebench summarize data/` - summarize runtime and memory by `tool`.
- `snakebench advise data/` - generate tool-level resource suggestions.
- `snakebench advise data/ --stratify input-size` - group suggestions by input-size bin.
- `snakebench dry data/` - check dataset readiness and PSB compatibility.
- `snakebench report data/ --out reports/example_report.md` - write a telemetry report.

Chart export requires `pip install .[charts]`.

## Upstream Alignment

- PSB defines the telemetry schema, export format, and server.
- `snakemake-logger-plugin-benchmark-telemetry` collects benchmark telemetry from Snakemake.
- Snakebench consumes exported PSB-style telemetry locally.
- Snakebench should keep PSB field names and units.
- See [docs/psb_upstream_mapping.md](docs/psb_upstream_mapping.md).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/ -v
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest tests/ -v
```

Dependencies are `pandas`, `pyarrow`, and `tabulate`. Test dependency is `pytest`.

## Repository Layout

```text
src/snakebench/
  load.py
  snakefile.py
  matching.py
  resource_estimation.py
  audit.py
  audit_export.py
  audit_metrics.py
  telemetry_schema.py
  psb.py
  charts.py
  summarize.py
  advise.py
  readiness.py
  features.py
  report.py
  cli.py

docs/
  walkthrough.md
  architecture.md
  psb_upstream_mapping.md
  audit_mode_design.md
  integration_notes.md

reports/
  example_report.md
  readiness_report.md
  audit_report.md
  audit_table.csv
  audit_charts/
```

`reports/` contains generated example outputs.

## Limitations

- Simple static Snakefile parser.
- Best-effort rule matching.
- Percentile heuristics, not ML.
- No telemetry collection.
- No backend or dashboard.
- Demo data is small.
