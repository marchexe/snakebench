"""Telemetry matching helpers for Snakefile audit rows."""

from __future__ import annotations

import pandas as pd


def match_by_rule_name(rule: dict, telemetry_df: pd.DataFrame) -> tuple[pd.DataFrame, str, str] | None:
    rule_name = rule.get("rule_name")
    if not rule_name or "rule_name" not in telemetry_df.columns:
        return None
    matched = telemetry_df[telemetry_df["rule_name"] == rule_name]
    if len(matched) == 0:
        return None
    return matched, str(rule_name), "rule_name"


def match_by_psb_tool(rule: dict, telemetry_df: pd.DataFrame) -> tuple[pd.DataFrame, str, str] | None:
    psb_tool = rule.get("psb_tool")
    if not psb_tool or "tool" not in telemetry_df.columns:
        return None
    matched = telemetry_df[telemetry_df["tool"] == psb_tool]
    if len(matched) == 0:
        return None
    return matched, str(psb_tool), "psb_tool"


def match_by_primary_cmd(rule: dict, telemetry_df: pd.DataFrame) -> tuple[pd.DataFrame, str, str] | None:
    psb_primary_cmd = rule.get("psb_primary_cmd")
    if not psb_primary_cmd or "command" not in telemetry_df.columns:
        return None
    matched = telemetry_df[telemetry_df["command"] == psb_primary_cmd]
    if len(matched) == 0:
        return None
    return matched, str(psb_primary_cmd), "psb_primary_cmd"


def match_rule_to_telemetry(rule: dict, telemetry_df: pd.DataFrame) -> tuple[pd.DataFrame, str, str]:
    """Match a Snakefile rule to telemetry using the documented audit priority."""
    for matcher in (match_by_rule_name, match_by_psb_tool, match_by_primary_cmd):
        result = matcher(rule, telemetry_df)
        if result is not None:
            return result
    return telemetry_df.iloc[0:0], "", "unmatched"
