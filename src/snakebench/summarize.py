"""Summarize telemetry data by tool."""

import pandas as pd
import numpy as np

from .telemetry_schema import (
    MEMORY_COLUMNS,
    RUNTIME_COLUMNS,
    THREAD_COLUMNS,
    TOOL_VERSION_COLUMNS,
    find_column,
    require_column,
)


def summarize_by_tool(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize telemetry data by tool.

    Calculates robust statistics (median, percentiles) for each tool.

    Parameters
    ----------
    df : pd.DataFrame
        Telemetry data with at least a 'tool' column.

    Returns
    -------
    pd.DataFrame
        Summary statistics by tool with columns:
        - tool
        - observations
        - median_runtime_sec
        - p90_runtime_sec
        - median_memory_mb
        - p95_memory_mb
        - min_threads
        - max_threads
        - num_tool_versions (if applicable)
    """
    tool_col = require_column(df, ["tool"], "tool")

    # Find runtime column
    runtime_col = find_column(df, RUNTIME_COLUMNS)

    # Find memory column
    memory_col = find_column(df, MEMORY_COLUMNS)

    # Find thread column
    thread_col = find_column(df, THREAD_COLUMNS)

    # Find tool version column (optional)
    version_col = find_column(df, TOOL_VERSION_COLUMNS)

    summaries = []

    for tool_name in df[tool_col].unique():
        tool_df = df[df[tool_col] == tool_name]

        summary = {"tool": tool_name, "observations": len(tool_df)}

        # Runtime metrics
        if runtime_col:
            summary["median_runtime_sec"] = float(tool_df[runtime_col].median())
            summary["p90_runtime_sec"] = float(
                tool_df[runtime_col].quantile(0.90)
            )
        else:
            summary["median_runtime_sec"] = np.nan
            summary["p90_runtime_sec"] = np.nan

        # Memory metrics
        if memory_col:
            summary["median_memory_mb"] = float(tool_df[memory_col].median())
            summary["p95_memory_mb"] = float(
                tool_df[memory_col].quantile(0.95)
            )
        else:
            summary["median_memory_mb"] = np.nan
            summary["p95_memory_mb"] = np.nan

        # Thread metrics
        if thread_col:
            summary["min_threads"] = int(tool_df[thread_col].min())
            summary["max_threads"] = int(tool_df[thread_col].max())
        else:
            summary["min_threads"] = np.nan
            summary["max_threads"] = np.nan

        # Tool version diversity
        if version_col:
            summary["num_tool_versions"] = tool_df[version_col].nunique()
        else:
            summary["num_tool_versions"] = np.nan

        summaries.append(summary)

    result = pd.DataFrame(summaries)
    return result.sort_values("observations", ascending=False).reset_index(
        drop=True
    )
