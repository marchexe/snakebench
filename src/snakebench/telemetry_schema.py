"""Telemetry schema helpers and accepted column names."""

from __future__ import annotations

import pandas as pd

TOOL_COLUMNS = ["tool", "rule", "rule_name"]
RUNTIME_COLUMNS = ["runtime_sec", "runtime_seconds", "seconds", "s", "runtime"]
MEMORY_COLUMNS = ["max_rss_mb", "max_memory_mb", "memory_mb", "max_rss", "mem_mb"]
THREAD_COLUMNS = ["threads", "num_threads", "n_threads"]
TOOL_VERSION_COLUMNS = ["tool_version", "version", "release"]

INPUT_SIZE_MB_COLUMNS = ["input_size_mb", "inputs_size_mb", "total_input_size_mb"]
INPUT_SIZE_BYTE_COLUMNS = [
    "input_bytes",
    "inputs_bytes",
    "total_input_bytes",
    "input_size",
]
INPUT_SIZE_COLUMNS = [
    "input_size_mb",
    "input_size",
    "inputs_size_mb",
    "total_input_size_mb",
    "input_bytes",
    "inputs_bytes",
    "total_input_bytes",
    "inputs",
    "num_inputs",
    "input_type",
]
OUTPUT_SIZE_COLUMNS = ["output_size_mb", "output_size", "output_bytes", "outputs_bytes"]

DECLARED_RESOURCE_COLUMNS = [
    "declared_mem_mb",
    "declared_runtime",
    "declared_cores",
    "resources",
]
FAILURE_COLUMNS = ["status", "exit_code", "failed", "oom", "error_type"]
ENVIRONMENT_COLUMNS = [
    "environment_id",
    "env_id",
    "host_hash",
    "hostname_hash",
    "cpu_model",
    "cpu_features",
    "cpu_cores",
    "l2_cache_kb",
    "l3_cache_kb",
    "cpu_freq_mhz",
    "os",
    "kernel",
    "kernel_version",
    "kernel_string",
    "platform",
    "sm_version",
    "snakemake_version",
    "deploy_mode",
]
PSB_INPUT_SIZE_COLUMNS = ["input_size", "inputs", "num_inputs", "input_type"]
PSB_RESOURCE_COLUMNS = ["resources"]
PSB_ENVIRONMENT_COLUMNS = [
    "host_hash",
    "cpu_model",
    "cpu_features",
    "cpu_cores",
    "l2_cache_kb",
    "l3_cache_kb",
    "cpu_freq_mhz",
    "os",
    "kernel_version",
    "kernel_string",
    "sm_version",
    "deploy_mode",
]


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first candidate column present in a DataFrame."""
    for column in candidates:
        if column in df.columns:
            return column
    return None


def find_columns(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    """Return all candidate columns present in a DataFrame."""
    return [column for column in candidates if column in df.columns]


def has_column(df: pd.DataFrame, candidates: list[str]) -> bool:
    """Return whether any candidate column exists in a DataFrame."""
    return find_column(df, candidates) is not None


def require_column(
    df: pd.DataFrame,
    candidates: list[str],
    logical_name: str,
) -> str:
    """Return the first matching column or raise a ValueError."""
    column = find_column(df, candidates)
    if column is None:
        raise ValueError(f"DataFrame must contain a '{logical_name}' column")
    return column
