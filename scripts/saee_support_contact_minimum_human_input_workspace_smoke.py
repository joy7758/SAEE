#!/usr/bin/env python3
"""Smoke test for support-contact minimum human-input workspace."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/"
    "support_contact_minimum_human_input_workspace"
)
OUT_JSON = OUT_DIR / "support_contact_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "support_contact_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "support_contact_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "support_contact_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "support_contact_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_SUPPORT_CONTACT_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: FAIL: " + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_support_contact_minimum_human_input_workspace.py"],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "support_contact_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_support_contact_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "support_contact",
        "minimum_required_field_count": 20,
        "minimum_required_human_value_count": 20,
        "filled_value_count": 0,
        "blank_value_count": 20,
        "first_owner_field_count": 5,
        "support_decision_field_count": 15,
        "candidate_contact_slot_count": 2,
        "minimum_completed_contact_slot_count": 1,
        "combined_bridge_input_row_count": 16,
        "human_review_required": True,
        "human_input_required": True,
        "boundary_violation_count": 0,
    }
    for key, value in expected_values.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    false_flags = [
        "production_ready",
        "product_launched",
        "customer_validated",
        "customer_contacted",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "workbook_import_authorized",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "development_permission_granted",
        "production_ready_claim",
        "customer_validation_claim",
        "support_contact_configured",
        "support_contact_published",
        "support_contact_test_performed",
        "support_contact_claim_published",
        "human_values_generated_by_codex",
        "human_input_filled_by_codex",
        "validator_inputs_exported",
        "validators_run",
        "values_saved_by_workspace",
        "form_submission_enabled",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")

    field_rows = payload.get("field_rows", [])
    require(len(field_rows) == 20, "field row count")
    require(
        any(row["field_id"] == "first_owner_input.assigned_human_owner" for row in field_rows),
        "missing first owner field",
    )
    require(
        any(
            row["field_id"]
            == "support_contact_decision_input.candidate_contact_slots[minimum_one_complete]"
            for row in field_rows
        ),
        "missing candidate contact slot field",
    )

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 20, "CSV must include 20 rows")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]
    )
    required_tokens = [
        "support_contact_minimum_human_input_workspace_v0_1",
        "status: hold_minimum_human_input_required",
        "minimum_required_field_count: 20",
        "blank_value_count: 20",
        "support_contact_published: false",
        "values_saved_by_workspace: false",
        "form_submission_enabled: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
    ]
    for token in required_tokens:
        require(token in combined, "missing token " + token)

    forbidden_tokens = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "support_contact_published: true",
        '"support_contact_published": true',
        "values_saved_by_workspace: true",
        '"values_saved_by_workspace": true',
        "form_submission_enabled: true",
        '"form_submission_enabled": true',
        "production_ready: true",
        '"production_ready": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
    ]
    for token in forbidden_tokens:
        require(token not in combined, "forbidden token " + token)

    print(
        "SAEE_SUPPORT_CONTACT_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: PASS "
        f"status={payload['status']} fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
