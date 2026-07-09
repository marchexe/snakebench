# Snakebench Advisor

A local-first, presentable v0.2 prototype for turning Snakemake / PSB-style benchmark telemetry into resource usage reports and confidence-aware Snakemake resource suggestions.

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

This is useful because small telemetry datasets can support summaries and cautious advice, but not reliable ML prediction. The current dataset has limited input size metadata, so input-size-aware suggestions may fall back to `unknown`.

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

## What v0.2 does

- Loads local parquet telemetry.
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
