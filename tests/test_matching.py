"""Tests for audit matching priority."""

import pandas as pd

from snakebench.matching import match_rule_to_telemetry


def test_matching_prefers_rule_name_over_psb_tool_and_command():
    telemetry = pd.DataFrame(
        {
            "rule_name": ["align_reads", "other_rule"],
            "tool": ["other-tool", "bwa-mem2"],
            "command": ["other", "bwa-mem2 mem"],
        }
    )
    rule = {
        "rule_name": "align_reads",
        "psb_tool": "bwa-mem2",
        "psb_primary_cmd": "bwa-mem2 mem",
    }

    matched, match_key, match_type = match_rule_to_telemetry(rule, telemetry)

    assert len(matched) == 1
    assert match_key == "align_reads"
    assert match_type == "rule_name"


def test_matching_uses_psb_tool_before_primary_command():
    telemetry = pd.DataFrame(
        {
            "tool": ["samtools", "other-tool"],
            "command": ["other", "samtools sort"],
        }
    )
    rule = {"psb_tool": "samtools", "psb_primary_cmd": "samtools sort"}

    matched, match_key, match_type = match_rule_to_telemetry(rule, telemetry)

    assert len(matched) == 1
    assert match_key == "samtools"
    assert match_type == "psb_tool"


def test_matching_uses_primary_command_after_missing_tool_match():
    telemetry = pd.DataFrame(
        {
            "tool": ["other-tool"],
            "command": ["gzip"],
        }
    )
    rule = {"psb_tool": "gzip-tool", "psb_primary_cmd": "gzip"}

    matched, match_key, match_type = match_rule_to_telemetry(rule, telemetry)

    assert len(matched) == 1
    assert match_key == "gzip"
    assert match_type == "psb_primary_cmd"


def test_matching_returns_unmatched_when_no_priority_matches():
    telemetry = pd.DataFrame({"tool": ["awk"], "command": ["awk"]})
    rule = {"rule_name": "missing", "psb_tool": "samtools", "psb_primary_cmd": "sort"}

    matched, match_key, match_type = match_rule_to_telemetry(rule, telemetry)

    assert len(matched) == 0
    assert match_key == ""
    assert match_type == "unmatched"
