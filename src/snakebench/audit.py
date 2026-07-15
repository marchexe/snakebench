"""Snakemake resource audit core."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from .audit_export import build_audit_markdown, write_audit_csv
from .audit_metrics import build_audit_metrics
from .matching import match_rule_to_telemetry
from .resources import (
    required_memory_mb,
    required_runtime_sec,
    safe_gap,
    safe_ratio,
    suggested_memory_mb,
    suggested_runtime_string,
)
from .snakefile import RuleResource, _parse_runtime_seconds, parse_snakefile


@dataclass
class AuditRow:
    rule_name: str
    match_key: str
    match_type: str
    observations: int
    declared_threads: int | None
    declared_mem_mb: float | None
    declared_runtime: str | None
    declared_runtime_sec: float | None
    observed_p95_memory_mb: float | None
    required_mem_mb: float | None
    observed_p90_runtime_sec: float | None
    required_runtime_sec: float | None
    suggested_mem_mb: float | None
    suggested_runtime: str
    memory_gap_mb: float | None
    memory_ratio: float | None
    runtime_gap_sec: float | None
    runtime_ratio: float | None
    status: str
    reason: str


def _safe_gap(declared: float | None, required: float | None) -> float | None:
    return safe_gap(declared, required)


def _safe_ratio(declared: float | None, required: float | None) -> float | None:
    return safe_ratio(declared, required)


def _match_rule(rule: dict, telemetry_df: pd.DataFrame) -> tuple[pd.DataFrame, str, str]:
    return match_rule_to_telemetry(rule, telemetry_df)


def _audit_statuses(
    observations: int,
    declared_mem_mb: float | None,
    declared_runtime: str | None,
    required_mem_mb: float | None,
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
    elif required_mem_mb is not None and pd.notna(required_mem_mb):
        if declared_mem_mb < required_mem_mb * 0.90:
            statuses.append("underrequested_mem")
            reasons.append("Declared mem_mb is more than 10% below required memory.")
        elif declared_mem_mb > required_mem_mb * 3.0 and declared_mem_mb > 256:
            statuses.append("overrequested_mem")
            reasons.append("Declared mem_mb is more than 3x required memory.")

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


def _suggest_for_group(group_df: pd.DataFrame) -> tuple[float | None, float | None, float | None, float | None, str, float | None]:
    if len(group_df) == 0:
        return None, None, None, None, "N/A", None

    observed_p95_memory = None
    required_mem = None
    observed_p90_runtime = None
    suggested_mem = None
    suggested_runtime = "N/A"
    suggested_runtime_sec = None

    if "max_rss_mb" in group_df.columns:
        observed_p95_memory = float(group_df["max_rss_mb"].quantile(0.95))
        if pd.notna(observed_p95_memory) and observed_p95_memory > 0:
            required_mem = required_memory_mb(observed_p95_memory)
            suggested_mem = suggested_memory_mb(required_mem)

    if "runtime_sec" in group_df.columns:
        observed_p90_runtime = float(group_df["runtime_sec"].quantile(0.90))
        if pd.notna(observed_p90_runtime) and observed_p90_runtime > 0:
            suggested_runtime_sec = required_runtime_sec(observed_p90_runtime)
            suggested_runtime = suggested_runtime_string(suggested_runtime_sec)

    return (
        observed_p95_memory,
        required_mem,
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
            required_mem,
            observed_p90_runtime,
            suggested_mem,
            suggested_runtime,
            suggested_runtime_sec,
        ) = _suggest_for_group(matched)

        declared_mem = rule.get("mem_mb")
        declared_runtime = rule.get("runtime")
        declared_runtime_sec = _parse_runtime_seconds(declared_runtime)
        status, reason = _audit_statuses(
            observations,
            declared_mem,
            declared_runtime,
            required_mem,
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
            declared_runtime_sec=declared_runtime_sec,
            observed_p95_memory_mb=observed_p95_memory,
            required_mem_mb=required_mem,
            observed_p90_runtime_sec=observed_p90_runtime,
            required_runtime_sec=suggested_runtime_sec,
            suggested_mem_mb=suggested_mem,
            suggested_runtime=suggested_runtime,
            memory_gap_mb=_safe_gap(declared_mem, required_mem),
            memory_ratio=_safe_ratio(declared_mem, required_mem),
            runtime_gap_sec=_safe_gap(declared_runtime_sec, suggested_runtime_sec),
            runtime_ratio=_safe_ratio(declared_runtime_sec, suggested_runtime_sec),
            status=status,
            reason=reason,
        )
        rows.append(asdict(row))

    return pd.DataFrame(rows)
