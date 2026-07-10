"""Minimal Snakemake resource audit mode."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from math import ceil
from pathlib import Path
from typing import Any

import pandas as pd

from .advise import _format_seconds_to_hms


@dataclass
class RuleResource:
    rule_name: str
    threads: int | None = None
    mem_mb: float | None = None
    runtime: str | None = None
    psb_tool: str | None = None
    psb_primary_cmd: str | None = None
    benchmark: str | None = None


@dataclass
class AuditRow:
    rule_name: str
    match_key: str
    match_type: str
    observations: int
    declared_threads: int | None
    declared_mem_mb: float | None
    declared_runtime: str | None
    observed_p95_memory_mb: float | None
    observed_p90_runtime_sec: float | None
    suggested_mem_mb: float | None
    suggested_runtime: str
    status: str
    reason: str


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for idx, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:idx]
    return line


def _clean_value(value: str) -> str:
    cleaned = _strip_comment(value).strip().rstrip(",")
    if (
        len(cleaned) >= 2
        and cleaned[0] == cleaned[-1]
        and cleaned[0] in {"'", '"'}
    ):
        return cleaned[1:-1]
    return cleaned


def _parse_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip().strip("'\""))
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any) -> int | None:
    number = _parse_number(value)
    if number is None:
        return None
    return int(number)


def _parse_runtime_seconds(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip().strip("'\"")
    if not text:
        return None

    if re.fullmatch(r"\d+(\.\d+)?", text):
        return float(text)

    if re.fullmatch(r"\d{1,3}:\d{2}:\d{2}", text):
        hours, minutes, seconds = [int(part) for part in text.split(":")]
        return float(hours * 3600 + minutes * 60 + seconds)

    if re.fullmatch(r"\d{1,3}:\d{2}", text):
        minutes, seconds = [int(part) for part in text.split(":")]
        return float(minutes * 60 + seconds)

    match = re.fullmatch(r"(\d+(\.\d+)?)(s|m|h)", text.lower())
    if match:
        value_float = float(match.group(1))
        unit = match.group(3)
        if unit == "s":
            return value_float
        if unit == "m":
            return value_float * 60
        if unit == "h":
            return value_float * 3600

    return None


def _split_assignments(text: str) -> list[tuple[str, str]]:
    assignments = []
    pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)(?=,\s*[A-Za-z_][A-Za-z0-9_]*\s*=|$)")
    for match in pattern.finditer(text.strip().rstrip(",")):
        assignments.append((match.group(1), _clean_value(match.group(2))))
    return assignments


def _parse_assignment(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    key = key.strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
        return None
    return key, _clean_value(value)


def _is_section_header(stripped: str) -> bool:
    return bool(re.match(r"^(threads|benchmark|resources|params|input|output|shell|run|script|log)\s*:", stripped))


def _apply_resource(rule: RuleResource, key: str, value: str) -> None:
    if key == "mem_mb":
        rule.mem_mb = _parse_number(value)
    elif key in {"runtime", "time"}:
        rule.runtime = _clean_value(value)


def _apply_param(rule: RuleResource, key: str, value: str) -> None:
    if key == "_psb_tool":
        rule.psb_tool = _clean_value(value)
    elif key == "_psb_primary_cmd":
        rule.psb_primary_cmd = _clean_value(value)


def parse_snakefile(path: str | Path) -> list[dict]:
    """Parse common static Snakefile rule resource declarations."""
    path = Path(path)
    rules: list[RuleResource] = []
    current: RuleResource | None = None
    section: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw_line)
        stripped = line.strip()
        if not stripped:
            continue

        rule_match = re.match(r"^rule\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", stripped)
        if rule_match:
            current = RuleResource(rule_name=rule_match.group(1))
            rules.append(current)
            section = None
            continue

        if current is None:
            continue

        section_match = re.match(r"^(threads|benchmark|resources|params)\s*:\s*(.*)$", stripped)
        if section_match:
            section = section_match.group(1)
            rest = section_match.group(2).strip()

            if section == "threads" and rest:
                current.threads = _parse_int(rest)
            elif section == "benchmark" and rest:
                current.benchmark = _clean_value(rest)
            elif section == "resources" and rest:
                for key, value in _split_assignments(rest):
                    _apply_resource(current, key, value)
            elif section == "params" and rest:
                for key, value in _split_assignments(rest):
                    _apply_param(current, key, value)
            continue

        if _is_section_header(stripped):
            section = None
            continue

        if section == "threads":
            current.threads = _parse_int(stripped)
        elif section == "benchmark":
            current.benchmark = _clean_value(stripped)
        elif section == "resources":
            assignment = _parse_assignment(stripped)
            if assignment:
                _apply_resource(current, assignment[0], assignment[1])
        elif section == "params":
            assignment = _parse_assignment(stripped)
            if assignment:
                _apply_param(current, assignment[0], assignment[1])

    return [asdict(rule) for rule in rules]


def _match_rule(rule: dict, telemetry_df: pd.DataFrame) -> tuple[pd.DataFrame, str, str]:
    rule_name = rule.get("rule_name")
    psb_tool = rule.get("psb_tool")
    psb_primary_cmd = rule.get("psb_primary_cmd")

    if rule_name and "rule_name" in telemetry_df.columns:
        matched = telemetry_df[telemetry_df["rule_name"] == rule_name]
        if len(matched) > 0:
            return matched, str(rule_name), "rule_name"

    if psb_tool and "tool" in telemetry_df.columns:
        matched = telemetry_df[telemetry_df["tool"] == psb_tool]
        if len(matched) > 0:
            return matched, str(psb_tool), "psb_tool"

    if psb_primary_cmd and "command" in telemetry_df.columns:
        matched = telemetry_df[telemetry_df["command"] == psb_primary_cmd]
        if len(matched) > 0:
            return matched, str(psb_primary_cmd), "psb_primary_cmd"

    return telemetry_df.iloc[0:0], "", "unmatched"


def _audit_statuses(
    observations: int,
    declared_mem_mb: float | None,
    declared_runtime: str | None,
    suggested_mem_mb: float | None,
    suggested_runtime_sec: float | None,
) -> tuple[str, str]:
    statuses = []
    reasons = []

    if observations == 0:
        return "unmatched", "No telemetry matched this rule."

    if observations < 3:
        statuses.append("insufficient_data")
        reasons.append("Fewer than 3 matching observations.")

    if declared_mem_mb is None or pd.isna(declared_mem_mb):
        statuses.append("missing_mem")
        reasons.append("No parsed mem_mb declaration.")
    elif suggested_mem_mb is not None and pd.notna(suggested_mem_mb):
        if suggested_mem_mb > declared_mem_mb * 1.10:
            statuses.append("underrequested_mem")
            reasons.append("Suggested memory is more than 10% above declared mem_mb.")
        elif declared_mem_mb > suggested_mem_mb * 2.0:
            statuses.append("overrequested_mem")
            reasons.append("Declared mem_mb is more than 2x suggested memory.")

    declared_runtime_sec = _parse_runtime_seconds(declared_runtime)
    if declared_runtime_sec is None:
        statuses.append("missing_runtime")
        reasons.append("No parsed runtime declaration.")
    elif suggested_runtime_sec is not None and pd.notna(suggested_runtime_sec):
        if suggested_runtime_sec > declared_runtime_sec * 1.10:
            statuses.append("underrequested_runtime")
            reasons.append("Suggested runtime is more than 10% above declared runtime.")
        elif declared_runtime_sec > suggested_runtime_sec * 2.0:
            statuses.append("overrequested_runtime")
            reasons.append("Declared runtime is more than 2x suggested runtime.")

    if not statuses:
        return "ok", "Declared resources are broadly aligned with telemetry suggestions."
    return "; ".join(statuses), " ".join(reasons)


def _suggest_for_group(group_df: pd.DataFrame) -> tuple[float | None, float | None, float | None, str, float | None]:
    if len(group_df) == 0:
        return None, None, None, "N/A", None

    observed_p95_memory = None
    observed_p90_runtime = None
    suggested_mem = None
    suggested_runtime = "N/A"
    suggested_runtime_sec = None

    if "max_rss_mb" in group_df.columns:
        observed_p95_memory = float(group_df["max_rss_mb"].quantile(0.95))
        if pd.notna(observed_p95_memory) and observed_p95_memory > 0:
            suggested_mem = ceil((observed_p95_memory * 1.25) / 256) * 256

    if "runtime_sec" in group_df.columns:
        observed_p90_runtime = float(group_df["runtime_sec"].quantile(0.90))
        if pd.notna(observed_p90_runtime) and observed_p90_runtime > 0:
            suggested_runtime_sec = ceil(observed_p90_runtime * 1.5)
            suggested_runtime = _format_seconds_to_hms(suggested_runtime_sec)

    return (
        observed_p95_memory,
        observed_p90_runtime,
        suggested_mem,
        suggested_runtime,
        suggested_runtime_sec,
    )


def audit_rules(rules: list[dict], telemetry_df: pd.DataFrame) -> pd.DataFrame:
    """Compare parsed Snakefile rules against observed telemetry suggestions."""
    rows = []

    for rule in rules:
        matched, match_key, match_type = _match_rule(rule, telemetry_df)
        observations = int(len(matched))
        (
            observed_p95_memory,
            observed_p90_runtime,
            suggested_mem,
            suggested_runtime,
            suggested_runtime_sec,
        ) = _suggest_for_group(matched)

        declared_mem = rule.get("mem_mb")
        declared_runtime = rule.get("runtime")
        status, reason = _audit_statuses(
            observations,
            declared_mem,
            declared_runtime,
            suggested_mem,
            suggested_runtime_sec,
        )

        row = AuditRow(
            rule_name=rule.get("rule_name", ""),
            match_key=match_key,
            match_type=match_type,
            observations=observations,
            declared_threads=rule.get("threads"),
            declared_mem_mb=declared_mem,
            declared_runtime=declared_runtime,
            observed_p95_memory_mb=observed_p95_memory,
            observed_p90_runtime_sec=observed_p90_runtime,
            suggested_mem_mb=suggested_mem,
            suggested_runtime=suggested_runtime,
            status=status,
            reason=reason,
        )
        rows.append(asdict(row))

    return pd.DataFrame(rows)


def _markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    if len(df) == 0:
        return "- None.\n"

    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for _, row in df.iterrows():
        values = []
        for column in columns:
            value = row.get(column)
            if isinstance(value, float):
                if pd.isna(value):
                    values.append("N/A")
                else:
                    values.append(f"{value:.2f}")
            elif pd.isna(value):
                values.append("N/A")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def build_audit_markdown(audit_df: pd.DataFrame) -> str:
    """Build a markdown report for Snakebench audit results."""
    total = len(audit_df)
    unmatched = int(audit_df["status"].str.contains("unmatched", na=False).sum()) if total else 0
    missing = int(audit_df["status"].str.contains("missing_", na=False).sum()) if total else 0
    under = int(audit_df["status"].str.contains("underrequested_", na=False).sum()) if total else 0
    over = int(audit_df["status"].str.contains("overrequested_", na=False).sum()) if total else 0
    ok = int((audit_df["status"] == "ok").sum()) if total else 0

    table_columns = [
        "rule_name",
        "match_type",
        "match_key",
        "observations",
        "declared_mem_mb",
        "declared_runtime",
        "suggested_mem_mb",
        "suggested_runtime",
        "status",
    ]

    missing_df = audit_df[audit_df["status"].str.contains("missing_", na=False)] if total else audit_df
    under_df = audit_df[audit_df["status"].str.contains("underrequested_", na=False)] if total else audit_df
    over_df = audit_df[audit_df["status"].str.contains("overrequested_", na=False)] if total else audit_df
    unmatched_df = audit_df[audit_df["status"].str.contains("unmatched", na=False)] if total else audit_df

    return f"""# Snakebench Audit Report

## Summary

- **Rules audited:** {total}
- **OK:** {ok}
- **Missing resources:** {missing}
- **Underrequested resources:** {under}
- **Overrequested resources:** {over}
- **Unmatched rules:** {unmatched}

## Rule audit table

{_markdown_table(audit_df, table_columns)}

## Missing resources

{_markdown_table(missing_df, table_columns)}

## Underrequested resources

{_markdown_table(under_df, table_columns)}

## Overrequested resources

{_markdown_table(over_df, table_columns)}

## Unmatched rules

{_markdown_table(unmatched_df, table_columns)}

## Limitations

- Audit mode uses simple static Snakefile parsing.
- Dynamic Python/Snakemake expressions may not be parsed.
- Matching is best-effort and works best with PSB annotations such as `_psb_tool`.
- Recommendations are heuristic, not ML.
"""
