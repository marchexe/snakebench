"""Tests for telemetry schema helpers."""

import pandas as pd
import pytest

from snakebench.schema import (
    MEMORY_COLUMNS,
    RUNTIME_COLUMNS,
    find_column,
    find_columns,
    has_column,
    require_column,
)


def test_find_column_returns_first_matching_candidate():
    df = pd.DataFrame({"runtime": [1.0], "runtime_sec": [2.0]})

    assert find_column(df, RUNTIME_COLUMNS) == "runtime_sec"


def test_find_column_returns_none_when_missing():
    df = pd.DataFrame({"tool": ["samtools"]})

    assert find_column(df, MEMORY_COLUMNS) is None
    assert not has_column(df, MEMORY_COLUMNS)


def test_find_columns_returns_all_matches_in_candidate_order():
    df = pd.DataFrame({"exit_code": [0], "status": ["ok"], "tool": ["awk"]})

    assert find_columns(df, ["status", "failed", "exit_code"]) == ["status", "exit_code"]


def test_require_column_raises_with_logical_name():
    df = pd.DataFrame({"tool": ["samtools"]})

    with pytest.raises(ValueError, match="runtime"):
        require_column(df, RUNTIME_COLUMNS, "runtime")
