"""Generate markdown reports from telemetry data."""

import pandas as pd
from datetime import datetime
from typing import Optional


def build_markdown_report(
    summary_df: pd.DataFrame,
    suggestions_df: pd.DataFrame,
    dataset_size: int,
    stratified_suggestions_df: Optional[pd.DataFrame] = None,
) -> str:
    """
    Build a markdown report from telemetry summaries and suggestions.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Output from summarize_by_tool().
    suggestions_df : pd.DataFrame
        Output from suggest_resources().
    dataset_size : int
        Total number of observations in the raw dataset.
    stratified_suggestions_df : pd.DataFrame, optional
        Output from suggest_resources_stratified() for input-size-aware suggestions.

    Returns
    -------
    str
        Markdown-formatted report.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    num_tools = len(summary_df)

    report = f"""# Snakebench Advisor Report

**Generated:** {timestamp}

## Executive Summary

This report presents telemetry-driven resource usage summaries and confidence-aware Snakemake resource suggestions.
**Important: This is not a machine learning model.** The current version uses robust statistics (medians, percentiles) 
to characterize tool behavior from a small dataset.

## Dataset Overview

- **Total observations:** {dataset_size}
- **Tools analyzed:** {num_tools}
- **Data collection period:** PSB Week 11, 2026

### Dataset Characteristics

This dataset represents execution telemetry collected from a specific bioinformatics workflow.
The observations come from multiple runs of tools like AWK, BWA-MEM2, gzip, samtools, and wgsim.

## Tool Summary

The following table shows the distribution of observations and basic runtime/memory statistics for each tool:

"""

    # Format summary table
    summary_display = summary_df.copy()
    for col in [
        "median_runtime_sec",
        "p90_runtime_sec",
        "median_memory_mb",
        "p95_memory_mb",
    ]:
        if col in summary_display.columns:
            summary_display[col] = summary_display[col].round(2)

    report += "| " + " | ".join(summary_display.columns) + " |\n"
    report += "| " + " | ".join(["---"] * len(summary_display.columns)) + " |\n"

    for _, row in summary_display.iterrows():
        values = []
        for col in summary_display.columns:
            val = row[col]
            if isinstance(val, float):
                values.append(f"{val:.2f}")
            elif isinstance(val, int):
                values.append(str(val))
            else:
                values.append(str(val) if pd.notna(val) else "N/A")
        report += "| " + " | ".join(values) + " |\n"

    report += "\n## Resource Suggestions\n\n"
    report += "Based on the observed data, the following resource allocations are recommended for Snakemake rules:\n\n"

    # Format suggestions table
    suggestions_display = suggestions_df[
        [
            "tool",
            "observations",
            "p90_runtime_sec",
            "suggested_runtime",
            "p95_memory_mb",
            "suggested_mem_mb",
            "confidence",
        ]
    ].copy()

    report += "| " + " | ".join(suggestions_display.columns) + " |\n"
    report += "| " + " | ".join(["---"] * len(suggestions_display.columns)) + " |\n"

    for _, row in suggestions_display.iterrows():
        values = []
        for col in suggestions_display.columns:
            val = row[col]
            if isinstance(val, float) and col in [
                "p90_runtime_sec",
                "p95_memory_mb",
            ]:
                values.append(f"{val:.2f}")
            elif isinstance(val, float):
                values.append(f"{val:.2f}")
            elif isinstance(val, int):
                values.append(str(val))
            else:
                values.append(str(val) if pd.notna(val) else "N/A")
        report += "| " + " | ".join(values) + " |\n"

    report += f"""
### Interpreting Suggestions

- **suggested_runtime:** Compute `ceil(p90_runtime * 1.5)` to provide a safety margin above the 90th percentile.
  Use in Snakemake as `time=` parameter (e.g., `time=suggested_runtime`).
- **suggested_mem_mb:** Compute `ceil(p95_memory * 1.25 / 256) * 256` to round up to nearest 256 MB and include safety margin.
  Use in Snakemake as `mem_mb=` parameter.
- **confidence:** Reflects data quality and size:
  - **low:** < 10 observations. Use as a rough guide only.
  - **medium:** 10-50 observations. Use with caution.
  - **high:** >= 50 observations. More reliable, but still not a learned model.
"""

    # Add stratified suggestions section if available
    if stratified_suggestions_df is not None and len(stratified_suggestions_df) > 0:
        report += """
## Input-size-aware Suggestions

The following table provides resource suggestions stratified by input size.
This is more realistic than tool-only aggregates, since resource usage often scales with input size.
However, these are still heuristic suggestions based on robust statistics, not learned predictions.

"""
        # Format stratified suggestions table
        strat_display = stratified_suggestions_df[[
            col for col in [
                "tool",
                "input_size_bin",
                "threads",
                "observations",
                "p90_runtime_sec",
                "suggested_runtime",
                "p95_memory_mb",
                "suggested_mem_mb",
                "confidence",
            ]
            if col in stratified_suggestions_df.columns
        ]].copy()

        report += "| " + " | ".join(strat_display.columns) + " |\n"
        report += "| " + " | ".join(["---"] * len(strat_display.columns)) + " |\n"

        for _, row in strat_display.iterrows():
            values = []
            for col in strat_display.columns:
                val = row[col]
                if isinstance(val, float) and col in [
                    "p90_runtime_sec",
                    "p95_memory_mb",
                ]:
                    values.append(f"{val:.2f}")
                elif isinstance(val, float):
                    values.append(f"{val:.2f}")
                elif isinstance(val, int):
                    values.append(str(val))
                else:
                    values.append(str(val) if pd.notna(val) else "N/A")
            report += "| " + " | ".join(values) + " |\n"

        report += """
### Notes on Stratified Suggestions

- Stratified suggestions depend on the presence of input size metadata in the telemetry.
- If input size is unknown for some observations, they appear under `input_size_bin = unknown`.
- This stratification is still heuristic: it groups by observed ranges, not learned from input-size features.
"""

    report += f"""

## Limitations

This report has explicit limitations that you should understand before using these suggestions:

### 1. Not a Machine Learning Model
- The current pipeline uses **robust descriptive statistics** only (medians, percentiles).
- There is **no learned prediction function**. We do not predict runtime/memory based on input features.
- We are not training a model on this data; we are only characterizing the observed distribution.

### 2. Small Dataset
- The current dataset contains only **{dataset_size} total observations**, distributed across {num_tools} tools.
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
"""

    return report

