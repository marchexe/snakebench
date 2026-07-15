"""Generate markdown reports from telemetry data."""

from datetime import datetime
from typing import Optional

import pandas as pd


def _format_markdown_table(df: pd.DataFrame) -> str:
    if len(df) == 0:
        return "- None.\n"

    lines = []
    lines.append("| " + " | ".join(df.columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(df.columns)) + " |")

    for _, row in df.iterrows():
        values = []
        for column in df.columns:
            value = row[column]
            if isinstance(value, float):
                values.append("N/A" if pd.isna(value) else f"{value:.2f}")
            elif pd.isna(value):
                values.append("N/A")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines) + "\n"


def build_markdown_report(
    summary_df: pd.DataFrame,
    suggestions_df: pd.DataFrame,
    dataset_size: int,
    stratified_suggestions_df: Optional[pd.DataFrame] = None,
    psb_report: Optional[dict] = None,
) -> str:
    """Build a markdown report from telemetry summaries and suggestions."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    num_tools = len(summary_df)

    summary_display = summary_df.copy()
    for column in [
        "median_runtime_sec",
        "p90_runtime_sec",
        "median_memory_mb",
        "p95_memory_mb",
    ]:
        if column in summary_display.columns:
            summary_display[column] = summary_display[column].round(2)

    suggestion_columns = [
        "tool",
        "observations",
        "p90_runtime_sec",
        "suggested_runtime",
        "p95_memory_mb",
        "required_mem_mb",
        "suggested_mem_mb",
        "confidence",
    ]
    suggestions_display = suggestions_df[
        [column for column in suggestion_columns if column in suggestions_df.columns]
    ].copy()

    report = f"""# Snakebench Advisor Report

**Generated:** {timestamp}

## Summary

- **Total observations:** {dataset_size}
- **Tools analyzed:** {num_tools}
- **Data collection period:** PSB Week 11, 2026
- **Method:** medians, percentiles, and fixed safety margins
- **ML model:** no

"""

    if psb_report:
        report += f"""## PSB Compatibility

- **PSB-like records:** {psb_report["psb_like_records"]} ({psb_report["psb_like_fraction"]:.1%})
- **Input size recognized:** {"yes" if psb_report["has_input_size"] else "no"}
- **Resources recognized:** {"yes" if psb_report["has_declared_resources"] else "no"}
- **Environment metadata recognized:** {"yes" if psb_report["has_environment_metadata"] else "no"}

"""

    report += f"""## Tool Summary

{_format_markdown_table(summary_display)}

## Resource Suggestions

Runtime suggestion uses `ceil(p90_runtime * 1.5)`. Memory requirement uses p95(max_rss_mb) × 1.25. The displayed suggested_mem_mb is rounded up to the nearest 256 MB for scheduler-friendly resource declarations.

Audit memory status is based on required_mem_mb, not the rounded suggested_mem_mb.

{_format_markdown_table(suggestions_display)}
"""

    if stratified_suggestions_df is not None and len(stratified_suggestions_df) > 0:
        strat_columns = [
            "tool",
            "input_size_bin",
            "threads",
            "observations",
            "p90_runtime_sec",
            "suggested_runtime",
            "p95_memory_mb",
            "required_mem_mb",
            "suggested_mem_mb",
            "confidence",
        ]
        strat_display = stratified_suggestions_df[
            [column for column in strat_columns if column in stratified_suggestions_df.columns]
        ].copy()

        report += f"""
## Input-Size Stratified Suggestions

{_format_markdown_table(strat_display)}
"""

    report += f"""
## Limitations

- Suggestions are percentile heuristics.
- Results depend on the observed workflow, input distribution, and environment.
- Current dataset size: {dataset_size} observations.
- No telemetry collection is performed by Snakebench.

## Next Steps

- Keep field names and units aligned with PSB.
- Improve plugin metadata for `rule_name`, `resources`, inputs/outputs, tool versions, and categories.
- Validate suggestions on held-out workflow runs before evaluating prediction.

---

**Version:** Snakebench Advisor v0.6.2
**Status:** Prototype
"""

    return report
