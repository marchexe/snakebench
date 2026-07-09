# Snakebench Advisor Report

**Generated:** 2026-07-09 15:46:20 UTC

## Executive Summary

This report presents telemetry-driven resource usage summaries and confidence-aware Snakemake resource suggestions.
**Important: This is not a machine learning model.** The current version uses robust statistics (medians, percentiles) 
to characterize tool behavior from a small dataset.

## Dataset Overview

- **Total observations:** 205
- **Tools analyzed:** 5
- **Data collection period:** PSB Week 11, 2026

### Dataset Characteristics

This dataset represents execution telemetry collected from a specific bioinformatics workflow.
The observations come from multiple runs of tools like AWK, BWA-MEM2, gzip, samtools, and wgsim.

## Tool Summary

The following table shows the distribution of observations and basic runtime/memory statistics for each tool:

| tool | observations | median_runtime_sec | p90_runtime_sec | median_memory_mb | p95_memory_mb | min_threads | max_threads | num_tool_versions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| samtools | 86 | 0.53 | 1.21 | 33.11 | 403.51 | 0 | 4 | 2 |
| gzip | 61 | 12.25 | 12.69 | 5.71 | 5.80 | 0 | 1 | 1 |
| bwa-mem2 | 29 | 18.64 | 19.09 | 439.77 | 442.34 | 0 | 4 | 2 |
| wgsim | 19 | 2.14 | 2.19 | 8.26 | 21.56 | 0 | 1 | 2 |
| awk | 10 | 0.15 | 0.16 | 7.90 | 7.95 | 0 | 1 | 1 |

## Resource Suggestions

Based on the observed data, the following resource allocations are recommended for Snakemake rules:

| tool | observations | p90_runtime_sec | suggested_runtime | p95_memory_mb | suggested_mem_mb | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| samtools | 86 | 1.21 | 00:00:02 | 403.51 | 512 | high |
| gzip | 61 | 12.69 | 00:00:20 | 5.80 | 256 | high |
| bwa-mem2 | 29 | 19.09 | 00:00:29 | 442.34 | 768 | medium |
| wgsim | 19 | 2.19 | 00:00:04 | 21.56 | 256 | medium |
| awk | 10 | 0.16 | 00:00:01 | 7.95 | 256 | medium |

### Interpreting Suggestions

- **suggested_runtime:** Compute `ceil(p90_runtime * 1.5)` to provide a safety margin above the 90th percentile.
  Use in Snakemake as `time=` parameter (e.g., `time=suggested_runtime`).
- **suggested_mem_mb:** Compute `ceil(p95_memory * 1.25 / 256) * 256` to round up to nearest 256 MB and include safety margin.
  Use in Snakemake as `mem_mb=` parameter.
- **confidence:** Reflects data quality and size:
  - **low:** < 10 observations. Use as a rough guide only.
  - **medium:** 10-50 observations. Use with caution.
  - **high:** >= 50 observations. More reliable, but still not a learned model.

## Input-size-aware Suggestions

The following table provides resource suggestions stratified by input size.
This is more realistic than tool-only aggregates, since resource usage often scales with input size.
However, these are still heuristic suggestions based on robust statistics, not learned predictions.

| tool | input_size_bin | observations | p90_runtime_sec | suggested_runtime | p95_memory_mb | suggested_mem_mb | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| awk | unknown | 10 | 0.16 | 00:00:01 | 7.95 | 256 | medium |
| bwa-mem2 | unknown | 29 | 19.09 | 00:00:29 | 442.34 | 768 | medium |
| gzip | unknown | 61 | 12.69 | 00:00:20 | 5.80 | 256 | high |
| samtools | unknown | 86 | 1.21 | 00:00:02 | 403.51 | 512 | high |
| wgsim | unknown | 19 | 2.19 | 00:00:04 | 21.56 | 256 | medium |

### Notes on Stratified Suggestions

- Stratified suggestions depend on the presence of input size metadata in the telemetry.
- If input size is unknown for some observations, they appear under `input_size_bin = unknown`.
- This stratification is still heuristic: it groups by observed ranges, not learned from input-size features.


## Limitations

This report has explicit limitations that you should understand before using these suggestions:

### 1. Not a Machine Learning Model
- The current pipeline uses **robust descriptive statistics** only (medians, percentiles).
- There is **no learned prediction function**. We do not predict runtime/memory based on input features.
- We are not training a model on this data; we are only characterizing the observed distribution.

### 2. Small Dataset
- The current dataset contains only **205 total observations**, distributed across 5 tools.
- Many tools have fewer than 50 observations, which limits statistical reliability.
- A statistically robust ML model typically requires hundreds or thousands of observations.

### 3. Single Environment & Workflow
- This data comes from a **single execution environment** (week 11, 2026).
- Different hardware, OS versions, and input distributions may produce different results.
- Generalization to other environments is uncertain.

### 4. Robust Statistics != Prediction
- Medians and percentiles describe **past observations**, not future performance.
- High variability within a tool's execution profile may not be captured by these summaries.
- Unknown input sizes or edge cases are not forecasted.

### 5. Suggestions Are Heuristic
- The 1.25x and 1.5x multipliers are heuristic choices, not empirically validated.
- They are reasonable starting points but should be validated in your environment.

## Suggested Next Steps

To move toward a future predictive resource advisor:

1. **Collect more observations:** Expand the dataset to hundreds or thousands of observations across diverse environments and input sizes.
2. **Stratify data:** Collect telemetry tagged by input size, environment, and other relevant features.
3. **Feature engineering:** Identify which input/environment features most strongly influence runtime and memory.
4. **Train an ML model:** With sufficient data and features, build a regression or quantile model to predict runtime/memory.
5. **Validate predictions:** Test suggestions on held-out data and real workflows.
6. **Connect to PSB:** Integrate with the broader Parsl Scalability Benchmark to share telemetry and models.

## Relationship to PSB (Parsl Scalability Benchmark)

PSB provides:
- The telemetry schema (columns, units, collection patterns).
- A reference implementation for collecting standardized benchmark data.
- A repository of publicly available benchmark results.

Snakebench Advisor explores the next step in this pipeline:
- Ingesting PSB-style telemetry.
- Summarizing it for local use.
- Providing immediate, confidence-aware suggestions.
- Laying the foundation for future ML-based resource prediction.

---

**Version:** Snakebench Advisor v0.2  
**Status:** Prototype  
**Audience:** Early adopters, researchers, Snakemake users exploring telemetry-driven resource allocation.
