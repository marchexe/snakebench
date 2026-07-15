# Snakebench Advisor

CLI tool for analyzing PSB-style Snakemake benchmark telemetry and auditing declared Snakemake resources against observed runtime and memory usage.

## Scope

- Reads local PSB-style parquet telemetry.
- Normalizes PSB fields: `input_size`, `output_size`, `resources`, environment metadata.
- Summarizes runtime and memory by tool.
- Derives percentile-based resource suggestions.
- Audits simple static Snakefile resource declarations.
- Does not collect telemetry.

## Upstream Alignment

- PSB defines the telemetry schema, export format, and server.
- `snakemake-logger-plugin-benchmark-telemetry` collects benchmark telemetry from Snakemake.
- Snakebench consumes exported PSB-style telemetry locally.
- Snakebench should keep PSB field names and units.
- See [docs/psb_upstream_mapping.md](docs/psb_upstream_mapping.md).
- Architecture notes: [docs/architecture.md](docs/architecture.md).

Upstream references:

- <https://github.com/btraven00/psb/blob/main/docs/spec.md>
- <https://github.com/btraven00/psb/blob/main/docs/roadmap.md>
- <https://github.com/btraven00/snakemake-logger-plugin-benchmark-telemetry>

## Commands

- `snakebench summarize data/` - summarize runtime and memory by `tool`.
- `snakebench advise data/` - generate tool-level resource suggestions.
- `snakebench advise data/ --stratify input-size` - group suggestions by input-size bin.
- `snakebench dry data/` - check dataset readiness and PSB compatibility.
- `snakebench report data/ --out reports/example_report.md` - write a telemetry report.
- `snakebench audit examples/demo_snakemake/Snakefile --telemetry data/` - audit Snakefile resources.
- `snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --out reports/audit_report.md` - write an audit report.
- `snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --csv reports/audit_table.csv` - write the audit table.
- `snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --charts reports/audit_charts` - write audit charts.

Chart export requires `pip install .[charts]`.

## Demo

`examples/demo_snakemake/` contains an audit demo Snakefile for `samtools`, `bwa-mem2`, `gzip`, `awk`, and `wgsim`.

This is an audit demo Snakefile, not a complete executable workflow.

Matching uses PSB annotations:

- `_psb_tool` -> telemetry `tool`
- `_psb_primary_cmd` -> telemetry `command`

Run:

```bash
snakebench audit examples/demo_snakemake/Snakefile --telemetry data/ --out examples/demo_snakemake/expected_audit_report.md
```

## Layout

```text
src/snakebench/
  psb.py          # PSB normalization
  load.py         # parquet loading
  schema.py       # telemetry column names
  resources.py    # resource estimation helpers
  features.py     # input-size features
  summarize.py    # tool summaries
  advise.py       # resource suggestions
  snakefile.py    # Snakefile resource parsing
  matching.py     # audit matching helpers
  readiness.py    # readiness checks
  audit.py        # Snakefile resource audit
  audit_metrics.py
  audit_export.py
  charts.py
  report.py       # markdown reports
  cli.py          # CLI entry point

docs/
  psb_upstream_mapping.md
  audit_mode_design.md
  integration_notes.md
  architecture.md

examples/demo_snakemake/
  README.md
  Snakefile
  config.yaml
  expected_audit_report.md

reports/
  example_report.md
  readiness_report.md
  audit_report.md
  audit_table.csv
  audit_charts/
```

`reports/` contains generated example outputs.

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

## Limitations

- Simple static Snakefile parser.
- Best-effort rule matching.
- Percentile heuristics, not ML.
- No telemetry collection.
- No backend or dashboard.
- Demo data is small.
- Plugin currently may emit less metadata than the PSB spec supports.

## Next Integration Work

- Improve plugin output: `rule_name`, `resources`, `inputs`/`outputs`, `tool_version`, `category`.
- Improve rule matching.
- Make the demo workflow fully runnable.
- Add a rule mapping file for unmatched rules.
- Evaluate prediction later, after enough data and baselines exist.
