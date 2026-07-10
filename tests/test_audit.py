"""Tests for Snakefile resource audit core behavior."""

import pandas as pd

from snakebench.audit import (
    audit_rules,
    build_audit_metrics,
    build_audit_markdown,
    parse_snakefile,
    write_audit_csv,
)


def test_audit_compatibility_imports_remain_available():
    assert parse_snakefile is not None
    assert build_audit_metrics is not None
    assert build_audit_markdown is not None
    assert write_audit_csv is not None


def test_audit_rules_matches_rule_by_psb_tool():
    rules = [{"rule_name": "sort_bam", "psb_tool": "samtools", "mem_mb": 1024, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["samtools", "samtools", "samtools"],
            "runtime_sec": [10.0, 20.0, 30.0],
            "max_rss_mb": [100.0, 200.0, 300.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert result.loc[0, "match_type"] == "psb_tool"
    assert result.loc[0, "observations"] == 3


def test_audit_rules_returns_unmatched_when_no_telemetry_match_exists():
    rules = [{"rule_name": "sort_bam", "psb_tool": "samtools", "mem_mb": 1024, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["gzip"],
            "runtime_sec": [10.0],
            "max_rss_mb": [100.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert result.loc[0, "status"] == "unmatched"


def test_audit_rules_detects_missing_mem():
    rules = [{"rule_name": "sort_bam", "psb_tool": "samtools", "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["samtools", "samtools", "samtools"],
            "runtime_sec": [10.0, 20.0, 30.0],
            "max_rss_mb": [100.0, 200.0, 300.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert "missing_mem" in result.loc[0, "status"]


def test_audit_rules_detects_underrequested_mem():
    rules = [{"rule_name": "sort_bam", "psb_tool": "samtools", "mem_mb": 128, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["samtools", "samtools", "samtools"],
            "runtime_sec": [10.0, 20.0, 30.0],
            "max_rss_mb": [500.0, 600.0, 700.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert "underrequested_mem" in result.loc[0, "status"]


def test_audit_rules_uses_required_mem_not_rounded_suggestion_for_tiny_tool():
    rules = [{"rule_name": "summarize_table", "psb_tool": "awk", "mem_mb": 64, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["awk", "awk", "awk"],
            "runtime_sec": [1.0, 1.0, 1.0],
            "max_rss_mb": [7.8, 8.0, 8.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert result.loc[0, "required_mem_mb"] == 10.0
    assert result.loc[0, "suggested_mem_mb"] == 256
    assert "underrequested_mem" not in result.loc[0, "status"]


def test_audit_rules_detects_actually_underrequested_mem():
    rules = [{"rule_name": "align_reads", "psb_tool": "bwa-mem2", "mem_mb": 256, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["bwa-mem2", "bwa-mem2", "bwa-mem2"],
            "runtime_sec": [10.0, 20.0, 30.0],
            "max_rss_mb": [400.0, 400.0, 400.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert result.loc[0, "required_mem_mb"] == 500.0
    assert "underrequested_mem" in result.loc[0, "status"]


def test_audit_rules_includes_enriched_numeric_columns():
    rules = [{"rule_name": "sort_bam", "psb_tool": "samtools", "mem_mb": 1024, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["samtools", "samtools", "samtools"],
            "runtime_sec": [10.0, 20.0, 30.0],
            "max_rss_mb": [100.0, 200.0, 300.0],
        }
    )

    result = audit_rules(rules, telemetry)

    for column in [
        "required_mem_mb",
        "declared_runtime_sec",
        "required_runtime_sec",
        "memory_gap_mb",
        "runtime_gap_sec",
        "memory_ratio",
        "runtime_ratio",
    ]:
        assert column in result.columns


def test_audit_rules_memory_gap_and_ratio():
    rules = [{"rule_name": "summarize_table", "psb_tool": "awk", "mem_mb": 64, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["awk", "awk", "awk"],
            "runtime_sec": [1.0, 1.0, 1.0],
            "max_rss_mb": [8.0, 8.0, 8.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert result.loc[0, "required_mem_mb"] == 10.0
    assert result.loc[0, "memory_gap_mb"] == 54.0
    assert result.loc[0, "memory_ratio"] == 6.4
