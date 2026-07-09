"""Tests for the summarize module."""

import pandas as pd
import numpy as np
from snakebench.summarize import summarize_by_tool


def test_summarize_by_tool_returns_one_row_per_tool():
    """Test that summarize_by_tool returns exactly one row per tool."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a", "tool_a", "tool_b", "tool_b", "tool_b"],
            "runtime_sec": [10.0, 12.0, 20.0, 25.0, 22.0],
            "max_rss_mb": [100.0, 110.0, 200.0, 210.0, 205.0],
        }
    )

    result = summarize_by_tool(df)

    assert len(result) == 2
    assert set(result["tool"].values) == {"tool_a", "tool_b"}


def test_summarize_by_tool_calculates_medians():
    """Test that median calculations are correct."""
    df = pd.DataFrame(
        {
            "tool": ["toolx"] * 5,
            "runtime_sec": [10.0, 20.0, 30.0, 40.0, 50.0],
            "max_rss_mb": [100.0, 200.0, 300.0, 400.0, 500.0],
        }
    )

    result = summarize_by_tool(df)

    assert result.loc[0, "median_runtime_sec"] == 30.0
    assert result.loc[0, "median_memory_mb"] == 300.0


def test_summarize_by_tool_calculates_percentiles():
    """Test that p90 and p95 are calculated correctly."""
    df = pd.DataFrame(
        {
            "tool": ["toolx"] * 10,
            "runtime_sec": list(range(1, 11)),
            "max_rss_mb": list(range(100, 1100, 100)),
        }
    )

    result = summarize_by_tool(df)

    # For 10 values 1-10: p90 should be 9.1
    assert abs(result.loc[0, "p90_runtime_sec"] - 9.1) < 0.1
    # For 10 values 100-1000: p95 should be around 950
    assert abs(result.loc[0, "p95_memory_mb"] - 950.0) < 10


def test_summarize_by_tool_handles_missing_columns():
    """Test that missing metric columns result in NaN, not crash."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a", "tool_a"],
            # No runtime_sec or max_rss_mb columns
        }
    )

    result = summarize_by_tool(df)

    assert pd.isna(result.loc[0, "median_runtime_sec"])
    assert pd.isna(result.loc[0, "median_memory_mb"])


def test_summarize_by_tool_finds_alternate_column_names():
    """Test that alternate column names are recognized."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a", "tool_a"],
            "runtime_seconds": [10.0, 20.0],
            "max_memory_mb": [100.0, 200.0],
        }
    )

    result = summarize_by_tool(df)

    assert result.loc[0, "median_runtime_sec"] == 15.0
    assert result.loc[0, "median_memory_mb"] == 150.0


def test_summarize_by_tool_counts_observations():
    """Test that observation count is correct."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"] * 42 + ["tool_b"] * 18,
            "runtime_sec": [10.0] * 60,
        }
    )

    result = summarize_by_tool(df)

    obs_a = result[result["tool"] == "tool_a"]["observations"].values[0]
    obs_b = result[result["tool"] == "tool_b"]["observations"].values[0]

    assert obs_a == 42
    assert obs_b == 18


if __name__ == "__main__":
    test_summarize_by_tool_returns_one_row_per_tool()
    test_summarize_by_tool_calculates_medians()
    test_summarize_by_tool_calculates_percentiles()
    test_summarize_by_tool_handles_missing_columns()
    test_summarize_by_tool_finds_alternate_column_names()
    test_summarize_by_tool_counts_observations()
    print("All tests passed!")
