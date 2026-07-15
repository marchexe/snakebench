"""Generate resource suggestions."""

import pandas as pd
import numpy as np
from typing import Optional, List

from .resources import required_memory_mb, required_runtime_sec, suggested_memory_mb, suggested_runtime_string
from .schema import MEMORY_COLUMNS, RUNTIME_COLUMNS, find_column


def confidence_level(n: int, cv: float = None) -> str:
    """
    Determine confidence level based on observation count and variability.

    Parameters
    ----------
    n : int
        Number of observations.
    cv : float, optional
        Coefficient of variation (stddev / mean). Higher values indicate more variability.

    Returns
    -------
    str
        Confidence level: "low", "medium", or "high".
    """
    if n < 10:
        base_confidence = "low"
    elif n < 50:
        base_confidence = "medium"
    else:
        base_confidence = "high"

    # Downgrade if high variability (CV > 0.5)
    if cv is not None and cv > 0.5:
        if base_confidence == "high":
            return "medium"
        elif base_confidence == "medium":
            return "low"

    return base_confidence


def _format_seconds_to_hms(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS.

    Parameters
    ----------
    seconds : float
        Number of seconds.

    Returns
    -------
    str
        Formatted time string.
    """
    return suggested_runtime_string(seconds)


def suggest_resources(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate resource suggestions based on telemetry summaries.

    Input DataFrame should be the output of summarize_by_tool().

    Parameters
    ----------
    df : pd.DataFrame
        Summary statistics from summarize_by_tool() with at least:
        - tool
        - observations
        - median_runtime_sec
        - p90_runtime_sec
        - median_memory_mb
        - p95_memory_mb

    Returns
    -------
    pd.DataFrame
        Resource suggestions with columns:
        - tool
        - observations
        - median_runtime_sec
        - p90_runtime_sec
        - suggested_runtime
        - median_memory_mb
        - p95_memory_mb
        - required_mem_mb
        - suggested_mem_mb
        - confidence
        - reason
    """
    suggestions = []

    for _, row in df.iterrows():
        tool = row["tool"]
        obs = row["observations"]

        # Get metrics, handle NaN
        median_runtime = row.get("median_runtime_sec", np.nan)
        p90_runtime = row.get("p90_runtime_sec", np.nan)
        median_memory = row.get("median_memory_mb", np.nan)
        p95_memory = row.get("p95_memory_mb", np.nan)

        # Calculate suggestions
        suggested_runtime_sec = required_runtime_sec(p90_runtime)
        suggested_runtime_hms = suggested_runtime_string(suggested_runtime_sec)
        if suggested_runtime_sec is None:
            suggested_runtime_sec = np.nan

        required_mem_mb = required_memory_mb(p95_memory)
        suggested_mem_mb = suggested_memory_mb(required_mem_mb)
        if required_mem_mb is None:
            required_mem_mb = np.nan
        if suggested_mem_mb is None:
            suggested_mem_mb = np.nan

        # Calculate coefficient of variation for runtime (if we have variance info)
        cv = None
        reason_parts = []

        if obs < 10:
            reason_parts.append("Few observations")
        elif obs < 50:
            reason_parts.append("Limited observations")
        else:
            reason_parts.append("Good observation count")

        conf = confidence_level(obs, cv)
        reason = "; ".join(reason_parts)

        suggestions.append(
            {
                "tool": tool,
                "observations": obs,
                "median_runtime_sec": median_runtime,
                "p90_runtime_sec": p90_runtime,
                "suggested_runtime": suggested_runtime_hms,
                "median_memory_mb": median_memory,
                "p95_memory_mb": p95_memory,
                "required_mem_mb": required_mem_mb,
                "suggested_mem_mb": suggested_mem_mb,
                "confidence": conf,
                "reason": reason,
            }
        )

    result = pd.DataFrame(suggestions)
    return result


def suggest_resources_stratified(
    df: pd.DataFrame,
    by: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Generate resource suggestions stratified by input size (and optionally threads).

    This groups observations by tool, input size bin, and optionally threads
    to provide more targeted resource suggestions.

    Parameters
    ----------
    df : pd.DataFrame
        Raw telemetry data (not a summary).
    by : list[str], optional
        Columns to group by. Default is ["tool", "input_size_bin"].
        Can include "tool", "input_size_bin", "threads".

    Returns
    -------
    pd.DataFrame
        Stratified resource suggestions with columns:
        - all grouping columns (tool, input_size_bin, threads)
        - observations
        - median_runtime_sec
        - p90_runtime_sec
        - suggested_runtime
        - median_memory_mb
        - p95_memory_mb
        - required_mem_mb
        - suggested_mem_mb
        - confidence
        - reason
    """
    from .features import add_size_bins, detect_input_size_column

    if by is None:
        by = ["tool", "input_size_bin"]

    # Validate requested grouping columns
    if "tool" not in by:
        by = ["tool"] + by

    # Add size bins
    df_with_bins = add_size_bins(df)

    # Check which grouping columns actually exist
    available_cols = [col for col in by if col in df_with_bins.columns]
    missing_cols = [col for col in by if col not in df_with_bins.columns]

    if not available_cols:
        raise ValueError(f"No valid grouping columns found. Requested: {by}")

    # Find runtime and memory columns (same as in suggest_resources)
    runtime_col = find_column(df_with_bins, RUNTIME_COLUMNS)
    memory_col = find_column(df_with_bins, MEMORY_COLUMNS)

    suggestions = []

    # Group by the requested columns
    grouped = df_with_bins.groupby(available_cols, dropna=False)

    for group_keys, group_df in grouped:
        # Create a dict for the group key(s)
        if len(available_cols) == 1:
            group_key_dict = {available_cols[0]: group_keys}
        else:
            group_key_dict = {col: key for col, key in zip(available_cols, group_keys)}

        obs = len(group_df)

        # Runtime metrics
        if runtime_col:
            median_runtime = float(group_df[runtime_col].median())
            p90_runtime = float(group_df[runtime_col].quantile(0.90))
        else:
            median_runtime = np.nan
            p90_runtime = np.nan

        # Memory metrics
        if memory_col:
            median_memory = float(group_df[memory_col].median())
            p95_memory = float(group_df[memory_col].quantile(0.95))
        else:
            median_memory = np.nan
            p95_memory = np.nan

        # Calculate suggestions
        suggested_runtime_sec = required_runtime_sec(p90_runtime)
        suggested_runtime_hms = suggested_runtime_string(suggested_runtime_sec)
        if suggested_runtime_sec is None:
            suggested_runtime_sec = np.nan

        required_mem_mb = required_memory_mb(p95_memory)
        suggested_mem_mb = suggested_memory_mb(required_mem_mb)
        if required_mem_mb is None:
            required_mem_mb = np.nan
        if suggested_mem_mb is None:
            suggested_mem_mb = np.nan

        # Confidence and reason
        cv = None
        reason_parts = []

        if obs < 10:
            reason_parts.append("Few observations")
        elif obs < 50:
            reason_parts.append("Limited observations")
        else:
            reason_parts.append("Good observation count")

        # Note if input size is unknown
        if "input_size_bin" in group_key_dict:
            if group_key_dict["input_size_bin"] == "unknown":
                reason_parts.append("input size unknown")

        conf = confidence_level(obs, cv)
        reason = "; ".join(reason_parts)

        suggestion = group_key_dict.copy()
        suggestion.update(
            {
                "observations": obs,
                "median_runtime_sec": median_runtime,
                "p90_runtime_sec": p90_runtime,
                "suggested_runtime": suggested_runtime_hms,
                "median_memory_mb": median_memory,
                "p95_memory_mb": p95_memory,
                "required_mem_mb": required_mem_mb,
                "suggested_mem_mb": suggested_mem_mb,
                "confidence": conf,
                "reason": reason,
            }
        )

        suggestions.append(suggestion)

    result = pd.DataFrame(suggestions)

    # Sort by tool and input size
    sort_cols = [col for col in ["tool", "input_size_bin", "threads"] if col in result.columns]
    if sort_cols:
        result = result.sort_values(sort_cols).reset_index(drop=True)

    return result
