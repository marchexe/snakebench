# Snakebench Dataset Readiness Report

## Dataset overview

- **Observations:** 205
- **Tools:** 5
- **Unique environments:** 2

## Available metadata

- **Runtime column:** runtime_sec
- **Memory column:** max_rss_mb
- **Threads column:** threads
- **Input size metadata:** no
- **Tool version metadata:** yes
- **Environment metadata:** yes
- **Declared Snakemake resources:** no
- **Failure/OOM information:** yes

## Readiness levels

- **tool level advisor:** ready - Runtime and memory metadata are present with at least 20 observations.
- **input size advisor:** limited - Tool-level advice is ready, but input size metadata is missing.
- **ml prediction:** limited - Enough data exists for exploratory analysis, but not full ML readiness.
- **workflow resource audit:** limited - Observed runtime/memory exist, but declared Snakemake resources are missing.

The current data should be treated honestly: small or incomplete telemetry can support summaries and heuristic advice, but it is not enough for reliable ML prediction unless the ML prediction level is marked ready.

## Missing metadata

- input size metadata
- declared Snakemake resources

## Recommended next telemetry fields

- input_size_mb
- rule name
- declared mem_mb
- declared runtime
- workflow name/version
- failed/OOM jobs
- environment ID
