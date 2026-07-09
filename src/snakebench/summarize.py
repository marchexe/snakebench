"""Summarize telemetry data by tool."""

import pandas as pd
import numpy as np


def _find_column(df: pd.DataFrame, candidates: list) -> str:
    """
    Find the first column name that exists in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The data frame to search.
    candidates : list
        List of candidate column names to search for.

    Returns
    -------
    str or None
        The first matching column name, or None if no match found.
    """
    for col in candidates:
        if col in df.columns:
            return col
    return None


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
    if "tool" not in df.columns:
        raise ValueError("DataFrame must contain a 'tool' column")

    # Find runtime column
    runtime_col = _find_column(
        df,
        ["runtime_sec", "runtime_seconds", "seconds", "s", "runtime"]
    )

    # Find memory column
    memory_col = _find_column(
        df,
        ["max_rss_mb", "max_memory_mb", "memory_mb", "max_rss", "mem_mb"]
    )

    # Find thread column
    thread_col = _find_column(df, ["threads", "num_threads", "n_threads"])

    # Find tool version column (optional)
    version_col = _find_column(
        df,
        ["tool_version", "version", "release"]
    )

    summaries = []

    for tool_name in df["tool"].unique():
        tool_df = df[df["tool"] == tool_name]

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
