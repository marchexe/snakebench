"""Audit-level summary metrics."""

from __future__ import annotations

import pandas as pd


def build_audit_metrics(audit_df: pd.DataFrame) -> dict:
    """Build compact counts from audit statuses."""
    if len(audit_df) == 0:
        return {
            "rules_audited": 0,
            "matched_rules": 0,
            "unmatched_rules": 0,
            "missing_mem_count": 0,
            "missing_runtime_count": 0,
            "underrequested_mem_count": 0,
            "underrequested_runtime_count": 0,
            "overrequested_mem_count": 0,
            "overrequested_runtime_count": 0,
            "ok_count": 0,
        }

    status = audit_df.get("status", pd.Series("", index=audit_df.index)).fillna("")
    match_type = audit_df.get("match_type", pd.Series("", index=audit_df.index)).fillna("")
    unmatched_mask = status.str.contains("unmatched", na=False) | (match_type == "unmatched")

    return {
        "rules_audited": int(len(audit_df)),
        "matched_rules": int((~unmatched_mask).sum()),
        "unmatched_rules": int(unmatched_mask.sum()),
        "missing_mem_count": int(status.str.contains("missing_mem", na=False).sum()),
        "missing_runtime_count": int(status.str.contains("missing_runtime", na=False).sum()),
        "underrequested_mem_count": int(status.str.contains("underrequested_mem", na=False).sum()),
        "underrequested_runtime_count": int(status.str.contains("underrequested_runtime", na=False).sum()),
        "overrequested_mem_count": int(status.str.contains("overrequested_mem", na=False).sum()),
        "overrequested_runtime_count": int(status.str.contains("overrequested_runtime", na=False).sum()),
        "ok_count": int((status == "ok").sum()),
    }
