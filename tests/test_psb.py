"""Tests for PSB compatibility normalization."""

import pandas as pd

from snakebench.psb import (
    is_psb_like_row,
    normalize_psb_dataframe,
    parse_resources,
)
from snakebench.readiness import inspect_dataset


def test_normalize_psb_dataframe_derives_input_size_mb_from_bytes():
    df = pd.DataFrame({"input_size": [1048576]})

    result = normalize_psb_dataframe(df)

    assert result.loc[0, "input_size_bytes"] == 1048576
    assert result.loc[0, "input_size_mb"] == 1.0


def test_normalize_psb_dataframe_derives_output_size_mb_from_bytes():
    df = pd.DataFrame({"output_size": [2 * 1048576]})

    result = normalize_psb_dataframe(df)

    assert result.loc[0, "output_size_bytes"] == 2 * 1048576
    assert result.loc[0, "output_size_mb"] == 2.0


def test_normalize_psb_dataframe_preserves_original_columns():
    df = pd.DataFrame({"tool": ["samtools"], "input_size": [1048576]})

    result = normalize_psb_dataframe(df)

    assert "tool" in result.columns
    assert result.loc[0, "tool"] == "samtools"


def test_normalize_psb_dataframe_is_idempotent():
    df = pd.DataFrame(
        {
            "input_size": [1048576],
            "output_size": [2048],
            "resources": ['{"_cores": 4, "mem_mb": 8000}'],
        }
    )

    once = normalize_psb_dataframe(df)
    twice = normalize_psb_dataframe(once)

    pd.testing.assert_frame_equal(once, twice)


def test_parse_resources_handles_json_string_with_cores_and_mem():
    result = parse_resources('{"_cores": 4, "mem_mb": 8000}')

    assert result["_cores"] == 4
    assert result["mem_mb"] == 8000


def test_parse_resources_handles_dict_with_cores_and_mem():
    result = parse_resources({"cores": 8, "mem_mb": 16000})

    assert result["cores"] == 8
    assert result["mem_mb"] == 16000


def test_parse_resources_handles_empty_and_invalid_values():
    assert parse_resources("") == {}
    assert parse_resources("not json") == {}
    assert parse_resources(None) == {}


def test_is_psb_like_row_detects_core_psb_style_row():
    row = pd.Series(
        {
            "session_id": "s",
            "record_id": "r",
            "tool": "samtools",
            "runtime_sec": 1.0,
            "max_rss_mb": 10.0,
        }
    )

    assert is_psb_like_row(row)


def test_is_psb_like_row_detects_psb_specific_row():
    row = pd.Series({"input_size": 1048576})

    assert is_psb_like_row(row)


def test_readiness_detects_psb_input_size():
    report = inspect_dataset(pd.DataFrame({"input_size": [1048576]}))

    assert report["has_input_size"]
    assert report["has_psb_input_size"]


def test_readiness_detects_psb_resources():
    report = inspect_dataset(pd.DataFrame({"resources": ['{"mem_mb": 8000}']}))

    assert report["has_declared_resources"]
    assert report["has_psb_resources"]


def test_readiness_detects_psb_environment_fields():
    report = inspect_dataset(
        pd.DataFrame(
            {
                "host_hash": ["abc"],
                "kernel_version": ["1.0"],
                "sm_version": ["9.0"],
                "cpu_cores": [8],
            }
        )
    )

    assert report["has_environment_metadata"]
    assert report["has_psb_environment"]
