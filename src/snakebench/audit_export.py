"""CSV and Markdown exports for audit results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .audit_metrics import build_audit_metrics


AUDIT_EXPORT_COLUMNS = [
    "rule_name",
    "match_key",
    "match_type",
    "observations",
    "declared_threads",
    "declared_mem_mb",
    "declared_runtime",
    "declared_runtime_sec",
    "observed_p95_memory_mb",
    "required_mem_mb",
    "suggested_mem_mb",
    "memory_gap_mb",
    "memory_ratio",
    "observed_p90_runtime_sec",
    "required_runtime_sec",
    "suggested_runtime",
    "runtime_gap_sec",
    "runtime_ratio",
    "status",
    "reason",
]


def write_audit_csv(audit_df: pd.DataFrame, path: str | Path) -> None:
    """Write audit results to CSV with a stable column order."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_df = audit_df.copy()
    for column in AUDIT_EXPORT_COLUMNS:
        if column not in export_df.columns:
            export_df[column] = pd.NA
    export_df[AUDIT_EXPORT_COLUMNS].to_csv(output_path, index=False)


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
    metrics = build_audit_metrics(audit_df)

    table_columns = AUDIT_EXPORT_COLUMNS

    missing_df = audit_df[audit_df["status"].str.contains("missing_", na=False)] if total else audit_df
    under_df = audit_df[audit_df["status"].str.contains("underrequested_", na=False)] if total else audit_df
    over_df = audit_df[audit_df["status"].str.contains("overrequested_", na=False)] if total else audit_df
    unmatched_df = audit_df[audit_df["status"].str.contains("unmatched", na=False)] if total else audit_df

    return f"""# Snakebench Audit Report

## Audit summary

- Rules audited: {metrics["rules_audited"]}
- Matched rules: {metrics["matched_rules"]}
- Unmatched rules: {metrics["unmatched_rules"]}
- Missing memory declarations: {metrics["missing_mem_count"]}
- Missing runtime declarations: {metrics["missing_runtime_count"]}
- Underrequested memory: {metrics["underrequested_mem_count"]}
- Underrequested runtime: {metrics["underrequested_runtime_count"]}
- Overrequested memory: {metrics["overrequested_mem_count"]}
- Overrequested runtime: {metrics["overrequested_runtime_count"]}
- OK: {metrics["ok_count"]}

Memory status uses `required_mem_mb = p95(max_rss_mb) Ã— 1.25`.
`suggested_mem_mb` is rounded up to the nearest 256 MB for scheduler-friendly declarations.

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
