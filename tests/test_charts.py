"""Tests for audit chart exports."""

import importlib.util

import pandas as pd
import pytest

from snakebench.charts import write_audit_charts


def test_write_audit_charts_creates_png_files(tmp_path):
    if importlib.util.find_spec("matplotlib") is None:
        pytest.skip("matplotlib is not installed")

    audit_df = pd.DataFrame(
        {
            "rule_name": ["sort_bam", "gzip_reads"],
            "match_type": ["psb_tool", "psb_tool"],
            "declared_mem_mb": [256.0, 512.0],
            "required_mem_mb": [512.0, 128.0],
            "declared_runtime_sec": [1.0, 30.0],
            "required_runtime_sec": [2.0, 20.0],
            "status": ["underrequested_mem; underrequested_runtime", "ok"],
        }
    )

    write_audit_charts(audit_df, tmp_path)

    assert (tmp_path / "status_counts.png").exists()
    assert (tmp_path / "declared_vs_required_memory_mb.png").exists()
    assert (tmp_path / "declared_vs_required_runtime_sec.png").exists()
