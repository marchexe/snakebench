"""Tests for shared resource estimation helpers."""

from snakebench.resources import (
    required_memory_mb,
    required_runtime_sec,
    safe_gap,
    safe_ratio,
    suggested_memory_mb,
    suggested_runtime_string,
)


def test_required_memory_and_scheduler_rounding_are_separate():
    required = required_memory_mb(8.0)

    assert required == 10.0
    assert suggested_memory_mb(required) == 256


def test_suggested_memory_rounding_remains_unchanged():
    assert suggested_memory_mb(required_memory_mb(1024.0)) == 1280


def test_runtime_estimation_and_formatting_remain_unchanged():
    required = required_runtime_sec(120.0)

    assert required == 180
    assert suggested_runtime_string(required) == "00:03:00"


def test_gap_and_ratio_preserve_missing_values():
    assert safe_gap(None, 10.0) is None
    assert safe_ratio(64.0, 0.0) is None
    assert safe_gap(64.0, 10.0) == 54.0
    assert safe_ratio(64.0, 10.0) == 6.4
