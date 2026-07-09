"""Tests for dataset readiness checks."""

import pandas as pd

from snakebench.readiness import (
    build_readiness_markdown,
    inspect_dataset,
    readiness_levels,
)


def test_inspect_dataset_detects_observations_and_tools():
    df = pd.DataFrame(
        {
            "tool": ["a", "a", "b"],
            "runtime_sec": [1.0, 2.0, 3.0],
            "max_rss_mb": [10.0, 20.0, 30.0],
        }
    )

    report = inspect_dataset(df)

    assert report["observations"] == 3
    assert report["tools"] == 2


def test_inspect_dataset_detects_runtime_and_memory_columns():
    df = pd.DataFrame(
        {
            "tool": ["a"],
            "runtime_seconds": [1.0],
            "memory_mb": [10.0],
        }
    )

    report = inspect_dataset(df)

    assert report["runtime_column"] == "runtime_seconds"
    assert report["memory_column"] == "memory_mb"


def test_tool_level_advisor_ready_with_metrics_and_enough_observations():
    df = pd.DataFrame(
        {
            "tool": ["a"] * 20,
            "runtime_sec": [1.0] * 20,
            "max_rss_mb": [10.0] * 20,
        }
    )

    levels = readiness_levels(inspect_dataset(df))

    assert levels["tool_level_advisor"]["status"] == "ready"


def test_input_size_advisor_limited_when_input_size_missing():
    df = pd.DataFrame(
        {
            "tool": ["a"] * 20,
            "runtime_sec": [1.0] * 20,
            "max_rss_mb": [10.0] * 20,
        }
    )

    levels = readiness_levels(inspect_dataset(df))

    assert levels["input_size_advisor"]["status"] in {"limited", "not_ready"}


def test_ml_prediction_not_ready_for_small_datasets():
    df = pd.DataFrame(
        {
            "tool": ["a"] * 20,
            "runtime_sec": [1.0] * 20,
            "max_rss_mb": [10.0] * 20,
            "input_size_mb": [100.0] * 20,
            "tool_version": ["1.0"] * 20,
            "environment_id": ["local"] * 20,
        }
    )

    levels = readiness_levels(inspect_dataset(df))

    assert levels["ml_prediction"]["status"] == "not_ready"


def test_workflow_resource_audit_ready_only_with_declared_resources():
    base = {
        "tool": ["a"] * 20,
        "runtime_sec": [1.0] * 20,
        "max_rss_mb": [10.0] * 20,
    }

    missing_levels = readiness_levels(inspect_dataset(pd.DataFrame(base)))
    ready_levels = readiness_levels(
        inspect_dataset(
            pd.DataFrame(
                {
                    **base,
                    "declared_mem_mb": [256] * 20,
                    "declared_runtime": [60] * 20,
                }
            )
        )
    )

    assert missing_levels["workflow_resource_audit"]["status"] != "ready"
    assert ready_levels["workflow_resource_audit"]["status"] == "ready"


def test_build_readiness_markdown_contains_expected_sections():
    df = pd.DataFrame(
        {
            "tool": ["a"] * 20,
            "runtime_sec": [1.0] * 20,
            "max_rss_mb": [10.0] * 20,
        }
    )

    markdown = build_readiness_markdown(df)

    assert "Snakebench Dataset Readiness Report" in markdown
    assert "Dataset overview" in markdown
    assert "Readiness levels" in markdown
    assert "Recommended next telemetry fields" in markdown
