# Snakebench Advisor

A local-first, presentable v0.2.1 prototype for turning Snakemake / PSB-style benchmark telemetry into resource usage reports and confidence-aware Snakemake resource suggestions.

Snakebench Advisor explores a simple path:

```text
telemetry -> resource report -> advisor -> future prediction
```

It is intentionally lightweight. The current version uses robust descriptive statistics, optional input-size stratification, and dataset readiness checks. It is not an ML model yet.

## Current dataset

This repository includes Week 11, 2026 telemetry from five bioinformatics tools:

- `awk-2026-W11.parquet`
- `bwa-mem2-2026-W11.parquet`
- `gzip-2026-W11.parquet`
- `samtools-2026-W11.parquet`
- `wgsim-2026-W11.parquet`

The dataset has about 205 observations. That is enough to demonstrate the local telemetry pipeline and generate cautious heuristic advice, but it is too small and incomplete for reliable ML prediction.

## Relationship to PSB

PSB (Parsl Scalability Benchmark) provides the telemetry protocol, collector/server, and Snakemake logger plugin that define the upstream field names and semantics. Snakebench Advisor consumes PSB-style telemetry locally and turns it into summaries, readiness checks, and cautious resource suggestions.

Snakebench does not replace PSB. It is a local analysis layer for PSB-style parquet exports and similar telemetry files. Where possible, Snakebench follows PSB field names and units directly.

## PSB compatibility

Snakebench v0.2.1 recognizes canonical PSB parquet/export fields:

- `input_size` and `output_size` are byte counts in PSB parquet exports.
- Snakebench derives `input_size_mb` and `output_size_mb` for local analysis.
- `resources` is treated as the upstream declared-resource carrier.
- Simple JSON resources such as `{"_cores": 4, "mem_mb": 8000}` are parsed into `declared_cores` and `declared_mem_mb`.
- PSB environment fields such as `host_hash`, `cpu_model`, `cpu_features`, `cpu_cores`, `kernel_version`, `kernel_string`, `sm_version`, and `deploy_mode` are recognized by readiness checks.

Current limitations:

- `resources` may be present but empty in exported data.
- Snakebench does not parse full `inputs` / `outputs` file-entry JSON yet.
- Snakebench does not parse Snakefiles or audit declared rule resources yet.
- Prediction and ML remain future work and require more data and evaluation.

## Installation

Use one local virtual environment named `.venv`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Runtime dependencies are intentionally minimal:

- pandas
- pyarrow
- tabulate

## Usage

Summarize telemetry by tool:

```bash
snakebench summarize data/
```

Generate tool-level resource suggestions:

```bash
snakebench advise data/
```

Generate input-size-aware suggestions when input size metadata is available:

```bash
snakebench advise data/ --stratify input-size
```

Generate a markdown report:

```bash
snakebench report data/ --out reports/example_report.md
```

## Dataset readiness / dry mode

Dry mode does not run workflows. It audits the telemetry dataset and checks whether the available metadata is enough for:

- tool-level advisor
- input-size advisor
- future ML prediction
- workflow resource audit

This is useful because small telemetry datasets can support summaries and cautious advice, but not reliable ML prediction. PSB input-size fields are recognized when present; rows with missing input-size values may still fall back to `unknown`.

```bash
snakebench dry data/
```

```bash
snakebench readiness data/ --out reports/readiness_report.md
```

The readiness report calls out missing metadata and recommends the next fields to collect, including input size, rule name, declared resources, workflow version, failed/OOM jobs, and environment ID.

## Reports

Example generated reports live in `reports/`:

- [reports/example_report.md](reports/example_report.md)
- [reports/readiness_report.md](reports/readiness_report.md)

## What v0.2.1 does

- Loads local parquet telemetry.
- Normalizes canonical PSB fields such as `input_size`, `output_size`, `resources`, and environment metadata.
- Summarizes runtime and memory by tool.
- Generates heuristic Snakemake resource suggestions.
- Supports optional input-size stratification with `--stratify input-size`.
- Generates markdown reports.
- Adds dataset readiness/dry mode for honest analysis gating.

## Limitations

- The current advisor uses robust statistics, not learned prediction.
- The included dataset is small.
- Some metadata needed for input-size-aware advice, environment comparison, workflow resource auditing, and ML prediction may be missing.
- Suggestions are starting points and should be checked against your own workflow and cluster behavior.

## Tests

```bash
python -m pytest tests/ -v
```

## Roadmap

- Collect more telemetry across workflows, environments, input sizes, tool versions, and failures.
- Compare declared Snakemake resources against observed runtime and memory.
- Add feature engineering for input size and environment metadata.
- Use larger datasets to explore future runtime and memory prediction.
