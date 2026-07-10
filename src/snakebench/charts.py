"""PNG chart exports for Snakebench audit results."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd

from .audit_metrics import build_audit_metrics


CHART_ERROR = "Chart export requires matplotlib. Install with: pip install .[charts]"


def _load_pyplot():
    if "MPLCONFIGDIR" not in os.environ:
        config_dir = Path(tempfile.gettempdir()) / "snakebench-matplotlib"
        config_dir.mkdir(parents=True, exist_ok=True)
        os.environ["MPLCONFIGDIR"] = str(config_dir)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(CHART_ERROR) from exc
    return plt


def _save_empty_chart(plt, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_title(title)
    ax.text(0.5, 0.5, "No rows with required values", ha="center", va="center")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _plot_status_counts(plt, audit_df: pd.DataFrame, output_dir: Path) -> None:
    metrics = build_audit_metrics(audit_df)
    labels = [
        "ok",
        "missing_mem",
        "missing_runtime",
        "underrequested_mem",
        "underrequested_runtime",
        "overrequested_mem",
        "overrequested_runtime",
        "unmatched",
    ]
    values = [
        metrics["ok_count"],
        metrics["missing_mem_count"],
        metrics["missing_runtime_count"],
        metrics["underrequested_mem_count"],
        metrics["underrequested_runtime_count"],
        metrics["overrequested_mem_count"],
        metrics["overrequested_runtime_count"],
        metrics["unmatched_rules"],
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels, values)
    ax.set_title("Audit status counts")
    ax.set_xlabel("Rules")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(output_dir / "status_counts.png")
    plt.close(fig)


def _plot_declared_vs_required(
    plt,
    audit_df: pd.DataFrame,
    output_dir: Path,
    declared_column: str,
    required_column: str,
    output_name: str,
    title: str,
    ylabel: str,
) -> None:
    available = audit_df.copy()
    available[declared_column] = pd.to_numeric(available[declared_column], errors="coerce")
    available[required_column] = pd.to_numeric(available[required_column], errors="coerce")
    available = available.dropna(subset=["rule_name", declared_column, required_column])
    path = output_dir / output_name
    if len(available) == 0:
        _save_empty_chart(plt, path, title)
        return

    labels = available["rule_name"].astype(str).tolist()
    x_positions = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(
        [x - width / 2 for x in x_positions],
        available[declared_column],
        width,
        label="declared",
    )
    ax.bar(
        [x + width / 2 for x in x_positions],
        available[required_column],
        width,
        label="required",
    )
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_audit_charts(audit_df: pd.DataFrame, output_dir: str | Path) -> None:
    """Write audit PNG charts to a directory."""
    plt = _load_pyplot()
    chart_dir = Path(output_dir)
    chart_dir.mkdir(parents=True, exist_ok=True)

    _plot_status_counts(plt, audit_df, chart_dir)
    _plot_declared_vs_required(
        plt,
        audit_df,
        chart_dir,
        "declared_mem_mb",
        "required_mem_mb",
        "declared_vs_required_memory_mb.png",
        "Memory declarations vs telemetry requirement",
        "Memory (MB)",
    )
    _plot_declared_vs_required(
        plt,
        audit_df,
        chart_dir,
        "declared_runtime_sec",
        "required_runtime_sec",
        "declared_vs_required_runtime_sec.png",
        "Runtime declarations vs telemetry requirement",
        "Runtime (seconds)",
    )
