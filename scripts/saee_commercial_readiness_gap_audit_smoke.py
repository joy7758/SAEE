#!/usr/bin/env python3
"""Smoke test for the commercial readiness gap audit."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "commercial_readiness_gap_audit"
OUT_JSON = OUT_DIR / "commercial_readiness_gap_audit.local.json"
OUT_MD = OUT_DIR / "commercial_readiness_gap_audit.md"
OUT_CSV = OUT_DIR / "commercial_readiness_gap_audit.csv"
OUT_BOUNDARY = OUT_DIR / "commercial_readiness_gap_audit_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_READINESS_GAP_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_GAP_AUDIT_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_READINESS_GAP_AUDIT_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_readiness_gap_audit.py"],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    require(payload["commercial_readiness_gap_audit_v0_1"] is True, "marker false")
    require(
        payload["audit_type"] == "formal_commercial_readiness_gap_audit",
        "wrong audit type",
    )
    require(
        payload["audit_scope"] == "local_evidence_gap_audit_no_execution_no_closure",
        "wrong audit scope",
    )
    require(payload["status"] == "hold_formal_commercial_requirements_unmet", "status")
    require(payload["commercial_status"] == "hold", "commercial status")
    require(payload["production_launch_status"] == "hold", "production launch status")
    require(payload["production_blocker_count"] == 24, "production blocker count")
    require(payload["open_blocker_count"] == 24, "open blocker count")
    require(payload["human_input_missing_value_row_count"] == 0, "missing value count")
    require(payload["preferred_template_missing_value_row_count"] == 0, "preferred missing")
    require(payload["review_batch_row_count"] == 0, "review batch row count")
    require(payload["review_batch_missing_value_row_count"] == 0, "review batch missing")
    require(payload["post_fill_quality_lint_enabled"] is True, "post-fill lint enabled")
    require(
        payload["post_fill_quality_lint_scope"] == "local_boundary_shape_lint_no_raw_values",
        "post-fill lint scope",
    )
    require(payload["post_fill_quality_lint_issue_count"] == 0, "post-fill lint issue count")
    require(
        payload["post_fill_forbidden_claim_lint_passed"] is True,
        "post-fill forbidden claim lint",
    )
    require(payload["post_fill_shape_lint_passed"] is True, "post-fill shape lint")
    require(
        payload["post_fill_ready_for_quality_safe_dry_run"] is False,
        "post-fill quality-safe dry run readiness",
    )
    require(payload["blockers_closed_by_audit"] == 0, "blockers closed")
    require(payload["accepted_for_blocker_closure_count"] == 0, "accepted closure")
    require(payload["boundary_violation_count"] == 0, "boundary violation count")
    require(payload["boundary_violations"] == [], "boundary violations")
    require(len(payload["blocker_rows"]) == 24, "blocker rows")

    false_flags = [
        "formal_commercial_ready",
        "ready_for_customer_push",
        "ready_for_paid_customer",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
        "workbook_import_authorized",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 24, "CSV must list 24 blockers")
    require(all(row["closure_allowed_by_audit"] == "False" for row in rows), "closure flag")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "SAEE 正式商用差距审计",
        "当前不能正式商用",
        "commercial_readiness_gap_audit_v0_1: true",
        "status: hold_formal_commercial_requirements_unmet",
        "formal_commercial_ready: false",
        "ready_for_customer_push: false",
        "post_fill_quality_lint_enabled: true",
        "post_fill_quality_lint_issue_count: 0",
        "post_fill_forbidden_claim_lint_passed: true",
        "post_fill_shape_lint_passed: true",
        "post_fill_ready_for_quality_safe_dry_run: false",
        "blockers_closed_by_audit: 0",
        "recommend_for_local_gap_audit: true",
        "recommend_for_product_launch: false",
        "production_ready: false",
    ]
    for token in required_tokens:
        require(token in combined, "missing token " + token)

    forbidden_tokens = [
        "formal_commercial_ready: true",
        '"formal_commercial_ready": true',
        "ready_for_customer_push: true",
        '"ready_for_customer_push": true',
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "blockers_closed_by_audit: 1",
    ]
    for token in forbidden_tokens:
        require(token not in combined, "forbidden token " + token)

    print(
        "SAEE_COMMERCIAL_READINESS_GAP_AUDIT_SMOKE: PASS "
        f"status={payload['status']} "
        f"open_blockers={payload['open_blocker_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
