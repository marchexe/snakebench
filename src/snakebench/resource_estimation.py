"""Resource estimation helpers shared by advice and audit code."""

from __future__ import annotations

from math import ceil

import pandas as pd


def required_memory_mb(
    observed_p95_memory_mb: float | None,
    safety_factor: float = 1.25,
) -> float | None:
    """Return required memory before scheduler rounding."""
    if observed_p95_memory_mb is None or pd.isna(observed_p95_memory_mb):
        return None
    if observed_p95_memory_mb <= 0:
        return None
    return float(observed_p95_memory_mb) * safety_factor


def suggested_memory_mb(
    required_mem_mb: float | None,
    quantum_mb: int = 256,
) -> float | None:
    """Round required memory up to the scheduler quantum."""
    if required_mem_mb is None or pd.isna(required_mem_mb):
        return None
    if required_mem_mb <= 0:
        return None
    return ceil(float(required_mem_mb) / quantum_mb) * quantum_mb


def required_runtime_sec(
    observed_p90_runtime_sec: float | None,
    safety_factor: float = 1.5,
) -> int | None:
    """Return required runtime seconds using the current audit formula."""
    if observed_p90_runtime_sec is None or pd.isna(observed_p90_runtime_sec):
        return None
    if observed_p90_runtime_sec <= 0:
        return None
    return ceil(float(observed_p90_runtime_sec) * safety_factor)


def suggested_runtime_string(seconds: float | None) -> str:
    """Format required runtime seconds as HH:MM:SS."""
    if seconds is None or pd.isna(seconds):
        return "N/A"
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def safe_gap(declared: float | None, required: float | None) -> float | None:
    """Return declared minus required, preserving missing values as None."""
    if declared is None or required is None:
        return None
    if pd.isna(declared) or pd.isna(required):
        return None
    return float(declared) - float(required)


def safe_ratio(declared: float | None, required: float | None) -> float | None:
    """Return declared divided by required, preserving invalid ratios as None."""
    if declared is None or required is None:
        return None
    if pd.isna(declared) or pd.isna(required) or float(required) == 0:
        return None
    return float(declared) / float(required)
