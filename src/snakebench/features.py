"""Feature extraction utilities for telemetry data."""

import pandas as pd
import numpy as np
from typing import Optional


def detect_input_size_column(df: pd.DataFrame) -> Optional[str]:
    """
    Detect if the DataFrame has an input size column.

    Checks for these columns in order:
    - input_size_mb, inputs_size_mb, total_input_size_mb (MB)
    - input_bytes, inputs_bytes, total_input_bytes, input_size (bytes)

    Parameters
    ----------
    df : pd.DataFrame
        Telemetry data.

    Returns
    -------
    str or None
        The name of the input size column, or None if not found.
    """
    mb_candidates = ["input_size_mb", "inputs_size_mb", "total_input_size_mb"]
    bytes_candidates = [
        "input_bytes",
        "inputs_bytes",
        "total_input_bytes",
        "input_size",
    ]

    # Check MB columns first
    for col in mb_candidates:
        if col in df.columns:
            return col

    # Check bytes columns
    for col in bytes_candidates:
        if col in df.columns:
            return col

    return None


def extract_input_size_mb(df: pd.DataFrame) -> pd.Series:
    """
    Extract input size in MB from telemetry data.

    If no input size column is found, returns a Series of NaN.

    Parameters
    ----------
    df : pd.DataFrame
        Telemetry data.

    Returns
    -------
    pd.Series
        Input size in MB.
    """
    col = detect_input_size_column(df)

    if col is None:
        # No input size data
        return pd.Series(np.nan, index=df.index)

    if col in ["input_size_mb", "inputs_size_mb", "total_input_size_mb"]:
        # Already in MB
        return df[col].copy()
    else:
        # PSB parquet exports use input_size in bytes.
        return pd.to_numeric(df[col], errors="coerce") / (1024 * 1024)


def add_size_bins(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add input size bins to DataFrame.

    Creates bins:
    - unknown: no input size data
    - zero: exactly 0 MB
    - small: 0-100 MB
    - medium: 100-1000 MB
    - large: 1000-10000 MB
    - xlarge: >10000 MB

    Parameters
    ----------
    df : pd.DataFrame
        Telemetry data.

    Returns
    -------
    pd.DataFrame
        DataFrame with new 'input_size_bin' column.
    """
    result = df.copy()

    # Extract input size in MB
    size_mb = extract_input_size_mb(df)

    # Create bins
    bins = []
    for size in size_mb:
        if pd.isna(size):
            bins.append("unknown")
        elif size == 0:
            bins.append("zero")
        elif size < 100:
            bins.append("small")
        elif size < 1000:
            bins.append("medium")
        elif size < 10000:
            bins.append("large")
        else:
            bins.append("xlarge")

    result["input_size_bin"] = bins
    result["input_size_mb"] = size_mb

    return result
