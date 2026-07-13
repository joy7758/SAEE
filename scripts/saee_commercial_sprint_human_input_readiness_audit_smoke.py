#!/usr/bin/env python3
"""Smoke check for commercial sprint human input readiness audit."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "commercial_sprint_human_input_readiness_audit_v0_1": True,
        "audit_type": "local_human_input_surface_readiness_audit",
        "audit_scope": "quick_fill_context_completeness_only_no_values_no_import",
        "status": "pass_human_input_surfaces_ready_hold_values_missing",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "quick_fill_row_count": 64,
        "expected_quick_fill_row_count": 64,
        "ready_for_human_input_row_count": 64,
        "missing_context_row_count": 0,
        "value_prefilled_count": 0,
        "blank_value_row_count": 64,
        "selected_blocker_count": 5,
        "human_input_required": True,
        "human_review_required": True,
        "ready_for_human_fill": True,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "blockers_closed_by_audit": 0,
    }
    for key, expected in expected_values.items():
        require(payload.get(key) == expected, f"{key} must be {expected}")

    false_flags = [
        "human_values_filled_by_codex",
        "quick_fill_values_entered_by_codex",
        "workbook_import_authorized",
        "workbook_import_performed",
        "workbook_written",
        "validators_run_on_real_input",
        "values_transferred",
        "human_filled_templates_written",
        "evidence_collection_authorized",
        "execution_authorized",
        "evidence_builder_executed",
        "blocker_closure_authorized",
        "blockers_closed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "vendor_contacted",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "development_permission_granted",
        "task_candidates_executed",
        "payment_collected",
        "revenue_validated",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for key in false_flags:
        require(payload.get(key) is False, f"{key} must be false")

    expected_blockers = [
        "formal_security_review",
        "pricing_page",
        "production_monitoring",
        "production_restore_policy",
        "support_contact",
    ]
    require(payload.get("selected_blocker_ids") == expected_blockers, "selected_blocker_ids drifted")
    rows = payload.get("rows", [])
    require(len(rows) == 64, "rows must contain 64 entries")
    for row in rows:
        row_id = row.get("quick_fill_row_id")
        for flag in [
            "required_fields_present",
            "human_value_blank",
            "prompt_path_exists",
            "guidance_row_present",
            "worksheet_row_present",
            "target_mapping_present",
            "ready_for_human_input",
        ]:
            require(row.get(flag) is True, f"{row_id} {flag} must be true")

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 64, "audit CSV must contain 64 rows")

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "commercial_sprint_human_input_readiness_audit_v0_1: true",
        "audit_scope: quick_fill_context_completeness_only_no_values_no_import",
        "status: pass_human_input_surfaces_ready_hold_values_missing",
        "commercial_status: hold",
        "production_launch_status: hold",
        "quick_fill_row_count: 64",
        "ready_for_human_input_row_count: 64",
        "missing_context_row_count: 0",
        "value_prefilled_count: 0",
        "blank_value_row_count: 64",
        "blockers_closed_by_audit: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_human_quick_fill_readiness: true",
        "recommend_for_workbook_import: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "blockers_closed_by_audit: 1",
        '"blockers_closed_by_audit": 1',
        "recommend_for_workbook_import: true",
        "recommend_for_validator_execution: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_readiness_audit.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_readiness_audit.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_readiness_audit.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_readiness_audit_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_readiness_audit.py",
        "/scripts/saee_commercial_sprint_human_input_readiness_audit_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_sprint_human_input_readiness_audit_v0_1", {})
    for key, expected in expected_values.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")
    for key in false_flags:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_SMOKE: PASS "
        "ready_rows=64 values_filled_by_codex=false production_ready=false"
    )


if __name__ == "__main__":
    main()
