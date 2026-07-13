#!/usr/bin/env python3
"""Smoke test for the commercial review-batch safe-prefill audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SUMMARY = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit.local.json"
MARKDOWN = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit.md"
CSV_PATH = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit.csv"
BOUNDARY = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT_SMOKE: FAIL {message}")


def require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    for path in [SUMMARY, MARKDOWN, CSV_PATH, BOUNDARY, TOP_DOC, GATE]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = {
        "commercial_review_batch_safe_prefill_audit_v0_1": True,
        "audit_type": "safe_prefill_audit_no_value_generation",
        "status": "hold_no_safe_codex_prefill",
        "target_blocker_id": "support_contact",
        "template_row_count": 10,
        "expected_template_row_count": 10,
        "human_required_row_count": 10,
        "codex_safe_prefill_count": 0,
        "existing_human_value_row_count": 0,
        "placeholder_or_hold_prefill_allowed_count": 0,
        "safe_to_prefill_by_codex": False,
        "recommended_next_action": "human_fill_required",
        "boundary_violation_count": 0,
        "blockers_closed_by_audit": 0,
    }
    for key, expected_value in expected.items():
        if data.get(key) != expected_value:
            fail(f"{key} must be {expected_value!r}")

    for key in [
        "human_values_generated_by_codex",
        "human_input_filled_by_codex",
        "codex_prefill_performed",
        "source_template_modified",
        "raw_values_recorded",
        "workbook_import_authorized",
        "workbook_import_performed",
        "values_transferred",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "customer_contacted",
        "product_launched",
        "production_ready",
        "production_ready_claim",
        "customer_validated",
        "customer_validation_claim",
    ]:
        require_false(data, key)

    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 10:
        fail("rows must contain 10 audit rows")
    for row in rows:
        if row.get("blocker_id") != "support_contact":
            fail(f"{row.get('review_batch_row_id')} blocker_id must be support_contact")
        if row.get("codex_prefill_allowed") is not False:
            fail(f"{row.get('review_batch_row_id')} codex_prefill_allowed must be false")
        if row.get("placeholder_or_hold_value_allowed_by_codex") is not False:
            fail(
                f"{row.get('review_batch_row_id')} placeholder_or_hold_value_allowed_by_codex "
                "must be false"
            )
        if row.get("safe_prefill_decision") != "human_required":
            fail(f"{row.get('review_batch_row_id')} safe_prefill_decision must be human_required")
        if row.get("requires_human_approval") is not True:
            fail(f"{row.get('review_batch_row_id')} requires_human_approval must be true")

    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 10:
        fail("CSV must contain 10 data rows")
    for row in csv_rows:
        if row.get("codex_prefill_allowed") != "False":
            fail("CSV codex_prefill_allowed must be False for every row")

    combined = "\n".join(
        [
            MARKDOWN.read_text(encoding="utf-8"),
            BOUNDARY.read_text(encoding="utf-8"),
            TOP_DOC.read_text(encoding="utf-8"),
            GATE.read_text(encoding="utf-8"),
        ]
    )
    required_text = [
        "no row is safe for Codex to",
        "safe_to_prefill_by_codex: false",
        "codex_safe_prefill_count: 0",
        "human_required_row_count: 10",
        "Do not prefill. Human input remains required.",
        "No `human_value_to_enter` cell modified.",
        "No blocker closed.",
        "No product launched.",
        "No production-ready or customer-validation claim added.",
    ]
    missing = [token for token in required_text if token not in combined]
    if missing:
        fail("missing required text: " + ", ".join(missing))

    forbidden_true = [
        "safe_to_prefill_by_codex: true",
        "codex_prefill_performed: true",
        "human_values_generated_by_codex: true",
        "human_input_filled_by_codex: true",
        "source_template_modified: true",
        "workbook_import_authorized: true",
        "evidence_collection_authorized: true",
        "blocker_closure_authorized: true",
        "product_launched: true",
        "production_ready: true",
    ]
    found = [token for token in forbidden_true if token in combined]
    if found:
        fail("forbidden true claim found: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT_SMOKE: PASS "
        "status=hold_no_safe_codex_prefill rows=10 codex_safe_prefill_count=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
