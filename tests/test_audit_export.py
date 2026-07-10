"""Tests for audit CSV and Markdown exports."""

import pandas as pd

from snakebench.audit import audit_rules
from snakebench.audit_export import build_audit_markdown, write_audit_csv


def test_write_audit_csv_writes_expected_columns(tmp_path):
    rules = [{"rule_name": "sort_bam", "psb_tool": "samtools", "mem_mb": 1024, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["samtools", "samtools", "samtools"],
            "runtime_sec": [10.0, 20.0, 30.0],
            "max_rss_mb": [100.0, 200.0, 300.0],
        }
    )
    audit_df = audit_rules(rules, telemetry)
    output_path = tmp_path / "audit_table.csv"

    write_audit_csv(audit_df, output_path)
    result = pd.read_csv(output_path)

    assert len(result) == 1
    for column in [
        "rule_name",
        "declared_runtime_sec",
        "required_runtime_sec",
        "memory_gap_mb",
        "runtime_gap_sec",
        "memory_ratio",
        "runtime_ratio",
        "status",
    ]:
        assert column in result.columns


def test_build_audit_markdown_contains_key_sections():
    audit_df = pd.DataFrame(
        {
            "rule_name": ["sort_bam"],
            "match_type": ["psb_tool"],
            "match_key": ["samtools"],
            "observations": [3],
            "declared_mem_mb": [128],
            "declared_runtime": ["00:10:00"],
            "observed_p95_memory_mb": [800],
            "required_mem_mb": [1000],
            "observed_p90_runtime_sec": [30],
            "suggested_mem_mb": [1024],
            "suggested_runtime": ["00:00:45"],
            "status": ["underrequested_mem"],
            "reason": ["Suggested memory is more than 10% above declared mem_mb."],
        }
    )

    markdown = build_audit_markdown(audit_df)

    assert "Snakebench Audit Report" in markdown
    assert "Rule audit table" in markdown
    assert "Missing resources" in markdown
    assert "Underrequested resources" in markdown
    assert "Unmatched rules" in markdown
