"""PSB compatibility helpers for local telemetry analysis."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import pandas as pd


PSB_CORE_COLUMNS = ["session_id", "record_id", "tool", "runtime_sec", "max_rss_mb"]
PSB_SPECIFIC_COLUMNS = [
    "input_size",
    "output_size",
    "resources",
    "host_hash",
    "cpu_model",
    "cpu_features",
    "cpu_cores",
    "kernel_version",
    "kernel_string",
    "sm_version",
    "deploy_mode",
]


def parse_resources(value: Any) -> dict:
    """Parse PSB/Snakemake resources metadata into a plain dictionary."""
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    try:
        if pd.isna(value):
            return {}
    except (TypeError, ValueError):
        return {}

    if not isinstance(value, str):
        return {}

    stripped = value.strip()
    if not stripped:
        return {}

    try:
        parsed = json.loads(stripped)
    except (TypeError, ValueError):
        return {}

    if isinstance(parsed, Mapping):
        return dict(parsed)
    return {}


def _resource_value(resources: dict, candidates: list[str]) -> Any:
    for key in candidates:
        if key in resources and resources[key] not in ("", None):
            return resources[key]
    return pd.NA


def is_psb_like_row(row) -> bool:
    """Return True when a row has core PSB evidence or PSB-specific fields."""
    index = row.index if hasattr(row, "index") else row.keys()
    has_core = all(
        column in index and pd.notna(row[column])
        for column in PSB_CORE_COLUMNS
    )
    if has_core:
        return True

    return any(
        column in index and pd.notna(row[column])
        for column in PSB_SPECIFIC_COLUMNS
    )


def normalize_psb_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize PSB-style parquet/export fields while preserving original columns.

    The function is intentionally small and idempotent. It does not parse full
    file-entry JSON yet; it only exposes PSB byte-size and resource metadata in
    analysis-friendly columns.
    """
    result = df.copy()

    if "input_size" in result.columns:
        input_bytes = pd.to_numeric(result["input_size"], errors="coerce")
        result["input_size_bytes"] = input_bytes
        result["input_size_mb"] = input_bytes / (1024 * 1024)

    if "output_size" in result.columns:
        output_bytes = pd.to_numeric(result["output_size"], errors="coerce")
        result["output_size_bytes"] = output_bytes
        result["output_size_mb"] = output_bytes / (1024 * 1024)

    if "num_inputs" in result.columns:
        result["input_file_count"] = result["num_inputs"]

    if "num_outputs" in result.columns:
        result["output_file_count"] = result["num_outputs"]

    if "input_type" in result.columns:
        result["input_types"] = result["input_type"]

    if "resources" in result.columns:
        parsed_resources = result["resources"].apply(parse_resources)
        result["declared_mem_mb"] = parsed_resources.apply(
            lambda item: _resource_value(item, ["mem_mb", "mem", "memory_mb"])
        )
        result["declared_runtime"] = parsed_resources.apply(
            lambda item: _resource_value(
                item,
                ["runtime", "time", "walltime", "wall_time", "runtime_min"],
            )
        )
        result["declared_cores"] = parsed_resources.apply(
            lambda item: _resource_value(item, ["_cores", "cores", "threads"])
        )

    if len(result) == 0:
        result["is_psb_like"] = pd.Series(dtype=bool)
    else:
        result["is_psb_like"] = result.apply(is_psb_like_row, axis=1)

    return result
