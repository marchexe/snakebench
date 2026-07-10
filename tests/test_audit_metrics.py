"""Tests for audit summary metrics."""

import pandas as pd

from snakebench.audit_metrics import build_audit_metrics


def test_build_audit_metrics_counts_multi_status_rows():
    audit_df = pd.DataFrame(
        {
            "match_type": ["psb_tool", "psb_tool", "psb_tool", "unmatched"],
            "status": [
                "underrequested_mem; underrequested_runtime",
                "missing_mem",
                "ok",
                "unmatched",
            ],
        }
    )

    metrics = build_audit_metrics(audit_df)

    assert metrics["rules_audited"] == 4
    assert metrics["matched_rules"] == 3
    assert metrics["unmatched_rules"] == 1
    assert metrics["missing_mem_count"] == 1
    assert metrics["missing_runtime_count"] == 0
    assert metrics["underrequested_mem_count"] == 1
    assert metrics["underrequested_runtime_count"] == 1
    assert metrics["overrequested_mem_count"] == 0
    assert metrics["overrequested_runtime_count"] == 0
    assert metrics["ok_count"] == 1
