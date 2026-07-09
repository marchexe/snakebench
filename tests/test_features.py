"""Tests for v0.2 features: input-size-aware advising."""

import pandas as pd
import numpy as np
from snakebench.features import (
    detect_input_size_column,
    extract_input_size_mb,
    add_size_bins,
)
from snakebench.advise import suggest_resources_stratified


def test_detect_input_size_column_finds_mb():
    """Test that detect_input_size_column finds MB columns."""
    df = pd.DataFrame(
        {
            "tool": ["a"],
            "input_size_mb": [100.0],
        }
    )
    assert detect_input_size_column(df) == "input_size_mb"


def test_detect_input_size_column_finds_bytes():
    """Test that detect_input_size_column finds bytes columns."""
    df = pd.DataFrame(
        {
            "tool": ["a"],
            "input_bytes": [1024 * 1024 * 100],  # 100 MB in bytes
        }
    )
    assert detect_input_size_column(df) == "input_bytes"


def test_detect_input_size_column_returns_none():
    """Test that detect_input_size_column returns None if no size column."""
    df = pd.DataFrame(
        {
            "tool": ["a"],
            "runtime_sec": [10.0],
        }
    )
    assert detect_input_size_column(df) is None


def test_extract_input_size_mb_from_mb():
    """Test extraction from MB column."""
    df = pd.DataFrame(
        {
            "input_size_mb": [100.0, 200.0, 50.0],
        }
    )
    result = extract_input_size_mb(df)
    assert result.tolist() == [100.0, 200.0, 50.0]


def test_extract_input_size_mb_from_bytes():
    """Test extraction and conversion from bytes column."""
    df = pd.DataFrame(
        {
            "input_bytes": [
                100 * 1024 * 1024,  # 100 MB
                200 * 1024 * 1024,  # 200 MB
            ],
        }
    )
    result = extract_input_size_mb(df)
    assert abs(result.iloc[0] - 100.0) < 0.01
    assert abs(result.iloc[1] - 200.0) < 0.01


def test_extract_input_size_mb_no_column():
    """Test that missing column returns NaN."""
    df = pd.DataFrame(
        {
            "runtime_sec": [10.0],
        }
    )
    result = extract_input_size_mb(df)
    assert pd.isna(result.iloc[0])


def test_add_size_bins_small():
    """Test that add_size_bins creates small bin correctly."""
    df = pd.DataFrame(
        {
            "input_size_mb": [50.0],
        }
    )
    result = add_size_bins(df)
    assert result.loc[0, "input_size_bin"] == "small"


def test_add_size_bins_medium():
    """Test that add_size_bins creates medium bin correctly."""
    df = pd.DataFrame(
        {
            "input_size_mb": [500.0],
        }
    )
    result = add_size_bins(df)
    assert result.loc[0, "input_size_bin"] == "medium"


def test_add_size_bins_large():
    """Test that add_size_bins creates large bin correctly."""
    df = pd.DataFrame(
        {
            "input_size_mb": [5000.0],
        }
    )
    result = add_size_bins(df)
    assert result.loc[0, "input_size_bin"] == "large"


def test_add_size_bins_xlarge():
    """Test that add_size_bins creates xlarge bin correctly."""
    df = pd.DataFrame(
        {
            "input_size_mb": [50000.0],
        }
    )
    result = add_size_bins(df)
    assert result.loc[0, "input_size_bin"] == "xlarge"


def test_add_size_bins_unknown():
    """Test that add_size_bins creates unknown bin for NaN."""
    df = pd.DataFrame(
        {
            "runtime_sec": [10.0],
        }
    )
    result = add_size_bins(df)
    assert result.loc[0, "input_size_bin"] == "unknown"


def test_suggest_resources_stratified_groups_by_tool_and_size():
    """Test that stratified suggestions groups by tool and input size."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a", "tool_a", "tool_b", "tool_b"],
            "input_size_mb": [50.0, 150.0, 50.0, 900.0],  # Changed to get 4 distinct groups
            "runtime_sec": [10.0, 20.0, 15.0, 30.0],
            "max_rss_mb": [100.0, 200.0, 150.0, 300.0],
        }
    )

    result = suggest_resources_stratified(df)

    # Should have 4 rows: tool_a/small, tool_a/medium, tool_b/small, tool_b/medium
    assert len(result) == 4
    assert "input_size_bin" in result.columns
    assert "tool" in result.columns


def test_suggest_resources_stratified_calculates_metrics():
    """Test that stratified suggestions calculate correct metrics."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"] * 10,
            "input_size_mb": [50.0] * 10,
            "runtime_sec": list(range(1, 11)),
            "max_rss_mb": list(range(100, 1100, 100)),
        }
    )

    result = suggest_resources_stratified(df)

    # Should have 1 row for tool_a/small
    assert len(result) == 1
    assert result.loc[0, "tool"] == "tool_a"
    assert result.loc[0, "input_size_bin"] == "small"
    assert result.loc[0, "observations"] == 10


def test_suggest_resources_stratified_unknown_size_has_reason():
    """Test that unknown input size appears in reason."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"] * 5,
            "runtime_sec": [10.0] * 5,
            "max_rss_mb": [100.0] * 5,
        }
    )

    result = suggest_resources_stratified(df)

    # Should have 1 row with unknown input size
    assert result.loc[0, "input_size_bin"] == "unknown"
    assert "input size unknown" in result.loc[0, "reason"]


def test_suggest_resources_stratified_with_threads():
    """Test that stratified suggestions can group by threads if requested."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"] * 6,
            "input_size_mb": [50.0] * 6,
            "threads": [1, 1, 2, 2, 4, 4],
            "runtime_sec": [10.0] * 6,
            "max_rss_mb": [100.0] * 6,
        }
    )

    result = suggest_resources_stratified(df, by=["tool", "input_size_bin", "threads"])

    # Should have 3 rows: tool_a/small/1, tool_a/small/2, tool_a/small/4
    assert len(result) == 3
    assert "threads" in result.columns
    assert set(result["threads"].values) == {1, 2, 4}


if __name__ == "__main__":
    test_detect_input_size_column_finds_mb()
    test_detect_input_size_column_finds_bytes()
    test_detect_input_size_column_returns_none()
    test_extract_input_size_mb_from_mb()
    test_extract_input_size_mb_from_bytes()
    test_extract_input_size_mb_no_column()
    test_add_size_bins_small()
    test_add_size_bins_medium()
    test_add_size_bins_large()
    test_add_size_bins_xlarge()
    test_add_size_bins_unknown()
    test_suggest_resources_stratified_groups_by_tool_and_size()
    test_suggest_resources_stratified_calculates_metrics()
    test_suggest_resources_stratified_unknown_size_has_reason()
    test_suggest_resources_stratified_with_threads()
    print("All v0.2 tests passed!")
