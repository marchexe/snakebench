"""Tests for the advise module."""

import pandas as pd
import numpy as np
from snakebench.advise import confidence_level, suggest_resources


def test_confidence_level_low():
    """Test confidence_level returns 'low' for < 10 observations."""
    assert confidence_level(5) == "low"
    assert confidence_level(9) == "low"


def test_confidence_level_medium():
    """Test confidence_level returns 'medium' for 10-49 observations."""
    assert confidence_level(10) == "medium"
    assert confidence_level(30) == "medium"
    assert confidence_level(49) == "medium"


def test_confidence_level_high():
    """Test confidence_level returns 'high' for >= 50 observations."""
    assert confidence_level(50) == "high"
    assert confidence_level(100) == "high"


def test_confidence_level_downgrades_for_high_cv():
    """Test that high CV (>0.5) downgrades confidence."""
    # high CV with high obs -> medium
    assert confidence_level(100, cv=0.6) == "medium"
    # high CV with medium obs -> low
    assert confidence_level(30, cv=0.6) == "low"


def test_suggest_resources_returns_suggested_columns():
    """Test that suggest_resources returns expected columns."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"],
            "observations": [50],
            "median_runtime_sec": [100.0],
            "p90_runtime_sec": [120.0],
            "median_memory_mb": [1000.0],
            "p95_memory_mb": [1200.0],
        }
    )

    result = suggest_resources(df)

    expected_cols = [
        "tool",
        "observations",
        "suggested_runtime",
        "suggested_mem_mb",
        "confidence",
    ]
    for col in expected_cols:
        assert col in result.columns


def test_suggest_resources_memory_calculation():
    """Test that memory suggestion is ceil(p95 * 1.25 / 256) * 256."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"],
            "observations": [50],
            "median_runtime_sec": [100.0],
            "p90_runtime_sec": [120.0],
            "median_memory_mb": [1000.0],
            "p95_memory_mb": [1024.0],  # 1024 * 1.25 = 1280 / 256 = 5, 5 * 256 = 1280
        }
    )

    result = suggest_resources(df)

    assert result.loc[0, "suggested_mem_mb"] == 1280.0


def test_suggest_resources_runtime_format():
    """Test that runtime is formatted as HH:MM:SS."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"],
            "observations": [50],
            "median_runtime_sec": [100.0],
            "p90_runtime_sec": [120.0],  # 120 * 1.5 = 180 = 0h 3m 0s
            "median_memory_mb": [1000.0],
            "p95_memory_mb": [1024.0],
        }
    )

    result = suggest_resources(df)

    assert result.loc[0, "suggested_runtime"] == "00:03:00"


def test_suggest_resources_confidence_from_observations():
    """Test that confidence level is based on observations."""
    low_obs = pd.DataFrame(
        {
            "tool": ["a"],
            "observations": [5],
            "median_runtime_sec": [100.0],
            "p90_runtime_sec": [120.0],
            "median_memory_mb": [1000.0],
            "p95_memory_mb": [1024.0],
        }
    )

    high_obs = pd.DataFrame(
        {
            "tool": ["b"],
            "observations": [100],
            "median_runtime_sec": [100.0],
            "p90_runtime_sec": [120.0],
            "median_memory_mb": [1000.0],
            "p95_memory_mb": [1024.0],
        }
    )

    result_low = suggest_resources(low_obs)
    result_high = suggest_resources(high_obs)

    assert result_low.loc[0, "confidence"] == "low"
    assert result_high.loc[0, "confidence"] == "high"


def test_suggest_resources_handles_nan():
    """Test that NaN values don't cause crashes."""
    df = pd.DataFrame(
        {
            "tool": ["tool_a"],
            "observations": [50],
            "median_runtime_sec": [np.nan],
            "p90_runtime_sec": [np.nan],
            "median_memory_mb": [np.nan],
            "p95_memory_mb": [np.nan],
        }
    )

    result = suggest_resources(df)

    assert result.loc[0, "suggested_runtime"] == "N/A"
    assert pd.isna(result.loc[0, "suggested_mem_mb"])


if __name__ == "__main__":
    test_confidence_level_low()
    test_confidence_level_medium()
    test_confidence_level_high()
    test_confidence_level_downgrades_for_high_cv()
    test_suggest_resources_returns_suggested_columns()
    test_suggest_resources_memory_calculation()
    test_suggest_resources_runtime_format()
    test_suggest_resources_confidence_from_observations()
    test_suggest_resources_handles_nan()
    print("All tests passed!")
