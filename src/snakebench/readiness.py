"""Dataset readiness checks for Snakebench telemetry."""

from __future__ import annotations

import pandas as pd

RUNTIME_COLUMNS = ["runtime_sec", "runtime_seconds", "seconds", "s", "runtime"]
MEMORY_COLUMNS = ["max_rss_mb", "max_memory_mb", "memory_mb", "max_rss", "mem_mb"]
THREAD_COLUMNS = ["threads", "num_threads", "n_threads"]
INPUT_SIZE_COLUMNS = [
    "input_size_mb",
    "inputs_size_mb",
    "total_input_size_mb",
    "input_bytes",
    "inputs_bytes",
    "total_input_bytes",
]
DECLARED_RESOURCE_COLUMNS = [
    "declared_mem_mb",
    "resources_mem_mb",
    "declared_runtime",
    "resources_runtime",
]
FAILURE_COLUMNS = ["status", "exit_code", "failed", "oom", "error_type"]
ENVIRONMENT_COLUMNS = [
    "environment_id",
    "env_id",
    "hostname_hash",
    "cpu_model",
    "os",
    "kernel",
    "platform",
    "snakemake_version",
    "deploy_mode",
]
TOOL_VERSION_COLUMNS = ["tool_version"]


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def _find_columns(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    return [column for column in candidates if column in df.columns]


def inspect_dataset(df: pd.DataFrame) -> dict:
    """Inspect telemetry columns and return compact readiness facts."""
    tool_col = _find_column(df, ["tool", "rule", "rule_name"])
    runtime_col = _find_column(df, RUNTIME_COLUMNS)
    memory_col = _find_column(df, MEMORY_COLUMNS)
    threads_col = _find_column(df, THREAD_COLUMNS)
    input_size_col = _find_column(df, INPUT_SIZE_COLUMNS)
    tool_version_col = _find_column(df, TOOL_VERSION_COLUMNS)
    declared_resource_cols = _find_columns(df, DECLARED_RESOURCE_COLUMNS)
    failure_cols = _find_columns(df, FAILURE_COLUMNS)
    environment_cols = _find_columns(df, ENVIRONMENT_COLUMNS)

    unique_environments = None
    environment_id_col = _find_column(df, ["environment_id", "env_id", "hostname_hash"])
    if environment_id_col:
        unique_environments = int(df[environment_id_col].nunique(dropna=True))
    elif environment_cols:
        unique_environments = int(df[environment_cols].drop_duplicates().shape[0])

    return {
        "observations": int(len(df)),
        "tool_column": tool_col,
        "tools": int(df[tool_col].nunique(dropna=True)) if tool_col else 0,
        "has_tool": tool_col is not None,
        "runtime_column": runtime_col,
        "has_runtime": runtime_col is not None,
        "memory_column": memory_col,
        "has_memory": memory_col is not None,
        "threads_column": threads_col,
        "has_threads": threads_col is not None,
        "input_size_column": input_size_col,
        "has_input_size": input_size_col is not None,
        "tool_version_column": tool_version_col,
        "has_tool_version": tool_version_col is not None,
        "environment_columns": environment_cols,
        "has_environment_metadata": bool(environment_cols),
        "unique_environments": unique_environments,
        "declared_resource_columns": declared_resource_cols,
        "has_declared_resources": bool(declared_resource_cols),
        "failure_columns": failure_cols,
        "has_failure_info": bool(failure_cols),
    }


def readiness_levels(report: dict) -> dict:
    """Classify the dataset for each Snakebench analysis level."""
    observations = report["observations"]
    has_runtime_memory = report["has_runtime"] and report["has_memory"]

    levels = {}

    if observations >= 20 and has_runtime_memory:
        levels["tool_level_advisor"] = {
            "status": "ready",
            "reason": "Runtime and memory metadata are present with at least 20 observations.",
        }
    elif has_runtime_memory:
        levels["tool_level_advisor"] = {
            "status": "limited",
            "reason": "Runtime and memory metadata are present, but there are fewer than 20 observations.",
        }
    else:
        levels["tool_level_advisor"] = {
            "status": "not_ready",
            "reason": "Runtime and memory metadata are required for tool-level advice.",
        }

    if levels["tool_level_advisor"]["status"] == "ready" and report["has_input_size"]:
        levels["input_size_advisor"] = {
            "status": "ready",
            "reason": "Tool-level advice is ready and input size metadata is available.",
        }
    elif levels["tool_level_advisor"]["status"] == "ready":
        levels["input_size_advisor"] = {
            "status": "limited",
            "reason": "Tool-level advice is ready, but input size metadata is missing.",
        }
    else:
        levels["input_size_advisor"] = {
            "status": "not_ready",
            "reason": "Input-size advice requires a ready tool-level advisor first.",
        }

    if (
        observations >= 1000
        and report["has_input_size"]
        and report["has_environment_metadata"]
        and report["has_tool_version"]
    ):
        levels["ml_prediction"] = {
            "status": "ready",
            "reason": "Dataset has enough observations and key feature metadata for ML exploration.",
        }
    elif observations >= 200 and has_runtime_memory and report["has_tool"]:
        levels["ml_prediction"] = {
            "status": "limited",
            "reason": "Enough data exists for exploratory analysis, but not full ML readiness.",
        }
    else:
        levels["ml_prediction"] = {
            "status": "not_ready",
            "reason": "Reliable ML prediction needs more observations plus input, environment, and version metadata.",
        }

    if report["has_declared_resources"] and has_runtime_memory:
        levels["workflow_resource_audit"] = {
            "status": "ready",
            "reason": "Declared resource columns and observed runtime/memory metadata are present.",
        }
    elif has_runtime_memory:
        levels["workflow_resource_audit"] = {
            "status": "limited",
            "reason": "Observed runtime/memory exist, but declared Snakemake resources are missing.",
        }
    else:
        levels["workflow_resource_audit"] = {
            "status": "not_ready",
            "reason": "Workflow resource audit requires observed runtime and memory metadata.",
        }

    return levels


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def build_readiness_markdown(df: pd.DataFrame) -> str:
    """Build a readable markdown readiness report."""
    report = inspect_dataset(df)
    levels = readiness_levels(report)

    missing = []
    if not report["has_input_size"]:
        missing.append("input size metadata")
    if not report["has_tool_version"]:
        missing.append("tool_version")
    if not report["has_environment_metadata"]:
        missing.append("environment metadata")
    if not report["has_declared_resources"]:
        missing.append("declared Snakemake resources")
    if not report["has_failure_info"]:
        missing.append("failure/OOM metadata")

    if missing:
        missing_text = "\n".join(f"- {item}" for item in missing)
    else:
        missing_text = "- No major readiness metadata gaps detected."

    level_lines = []
    for name, item in levels.items():
        display_name = name.replace("_", " ")
        level_lines.append(f"- **{display_name}:** {item['status']} - {item['reason']}")

    unique_env = report["unique_environments"]
    unique_env_text = "unknown" if unique_env is None else str(unique_env)

    return f"""# Snakebench Dataset Readiness Report

## Dataset overview

- **Observations:** {report["observations"]}
- **Tools:** {report["tools"]}
- **Unique environments:** {unique_env_text}

## Available metadata

- **Runtime column:** {report["runtime_column"] or "missing"}
- **Memory column:** {report["memory_column"] or "missing"}
- **Threads column:** {report["threads_column"] or "missing"}
- **Input size metadata:** {_yes_no(report["has_input_size"])}
- **Tool version metadata:** {_yes_no(report["has_tool_version"])}
- **Environment metadata:** {_yes_no(report["has_environment_metadata"])}
- **Declared Snakemake resources:** {_yes_no(report["has_declared_resources"])}
- **Failure/OOM information:** {_yes_no(report["has_failure_info"])}

## Readiness levels

{chr(10).join(level_lines)}

The current data should be treated honestly: small or incomplete telemetry can support summaries and heuristic advice, but it is not enough for reliable ML prediction unless the ML prediction level is marked ready.

## Missing metadata

{missing_text}

## Recommended next telemetry fields

- input_size_mb
- rule name
- declared mem_mb
- declared runtime
- workflow name/version
- failed/OOM jobs
- environment ID
"""
