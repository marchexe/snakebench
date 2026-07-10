"""Tests for minimal Snakefile audit mode."""

import pandas as pd

from snakebench.audit import (
    audit_rules,
    build_audit_markdown,
    parse_snakefile,
)


SNAKEFILE_TEXT = """
rule sort_bam:
    threads: 4
    benchmark:
        "benchmarks/sort_bam.tsv"
    resources:
        mem_mb=2000,
        runtime="00:30:00"
    params:
        _psb_tool="samtools",
        _psb_primary_cmd="sort",

rule gzip_reads:
    threads: 1
    resources:
        mem_mb=128,
        runtime="00:00:05"
    params:
        _psb_tool="gzip",
"""


def test_parse_snakefile_finds_rule_names(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert [rule["rule_name"] for rule in rules] == ["sort_bam", "gzip_reads"]


def test_parse_snakefile_extracts_threads(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["threads"] == 4


def test_parse_snakefile_extracts_resources_mem_mb(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["mem_mb"] == 2000


def test_parse_snakefile_extracts_runtime(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["runtime"] == "00:30:00"


def test_parse_snakefile_extracts_psb_tool(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["psb_tool"] == "samtools"


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


def test_audit_rules_includes_required_mem_column():
    rules = [{"rule_name": "sort_bam", "psb_tool": "samtools", "mem_mb": 1024, "runtime": "00:10:00"}]
    telemetry = pd.DataFrame(
        {
            "tool": ["samtools", "samtools", "samtools"],
            "runtime_sec": [10.0, 20.0, 30.0],
            "max_rss_mb": [100.0, 200.0, 300.0],
        }
    )

    result = audit_rules(rules, telemetry)

    assert "required_mem_mb" in result.columns


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
