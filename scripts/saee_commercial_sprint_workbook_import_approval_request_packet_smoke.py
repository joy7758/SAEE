#!/usr/bin/env python3
"""Smoke test for the commercial sprint workbook import approval request packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py"

OUT_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_WORKBOOK_IMPORT_APPROVAL_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_APPROVAL_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)

EXPECTED_FALSE = [
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
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
    "payment_collected",
    "revenue_validated",
]

REQUIRED_DOC_TOKENS = [
    "commercial_sprint_workbook_import_approval_request_packet_v0_1: true",
    "packet_scope: pre_workbook_import_approval_request_only_no_import_no_transfer_no_evidence",
    "approval_request_count: 1",
    "approved_import_count: 0",
    "workbook_import_authorized_count: 0",
    "ready_for_workbook_import_execution: false",
    "human_import_approval_required: true",
    "separate_workbook_import_execution_request_required: true",
    "separate_template_transfer_request_required: true",
    "separate_validator_execution_request_required: true",
    "workbook_import_authorized: false",
    "workbook_import_performed: false",
    "workbook_written: false",
    "values_transferred: false",
    "human_filled_templates_written: false",
    "validators_run_on_real_input: false",
    "real_evidence_created: false",
    "evidence_collection_authorized: false",
    "execution_authorized: false",
    "evidence_builder_executed: false",
    "blocker_closure_authorized: false",
    "boundary_violation_count: 0",
    "production_ready: false",
    "customer_validated: false",
    "product_launched: false",
    "private_core_exposed: false",
]

REQUIRED_GATE_TOKENS = [
    "answer: conditional",
    "recommend_for_workbook_import_approval_request: true",
    "recommend_for_human_approval_collection: true",
    "recommend_for_workbook_import_execution: false",
    "recommend_for_auto_approval: false",
    "recommend_for_template_transfer: false",
    "recommend_for_validator_execution: false",
    "recommend_for_evidence_collection: false",
    "recommend_for_evidence_builder_execution: false",
    "recommend_for_blocker_closure: false",
    "recommend_for_product_launch: false",
    "recommend_for_production_readiness_claim: false",
]

FORBIDDEN_DOC_TOKENS = [
    "workbook_import_authorized: true",
    "\"workbook_import_authorized\": true",
    "workbook_import_performed: true",
    "\"workbook_import_performed\": true",
    "workbook_written: true",
    "\"workbook_written\": true",
    "values_transferred: true",
    "\"values_transferred\": true",
    "human_filled_templates_written: true",
    "\"human_filled_templates_written\": true",
    "validators_run_on_real_input: true",
    "\"validators_run_on_real_input\": true",
    "real_evidence_created: true",
    "\"real_evidence_created\": true",
    "evidence_collection_authorized: true",
    "\"evidence_collection_authorized\": true",
    "execution_authorized: true",
    "\"execution_authorized\": true",
    "evidence_builder_executed: true",
    "\"evidence_builder_executed\": true",
    "blocker_closure_authorized: true",
    "\"blocker_closure_authorized\": true",
    "production_ready: true",
    "\"production_ready\": true",
    "product_launched: true",
    "\"product_launched\": true",
    "customer_validated: true",
    "\"customer_validated\": true",
    "private_core_exposed: true",
    "\"private_core_exposed\": true",
    "recommend_for_workbook_import_execution: true",
    "recommend_for_auto_approval: true",
    "recommend_for_template_transfer: true",
    "recommend_for_validator_execution: true",
    "recommend_for_evidence_collection: true",
    "recommend_for_evidence_builder_execution: true",
    "recommend_for_blocker_closure: true",
    "recommend_for_product_launch: true",
    "recommend_for_production_readiness_claim: true",
]


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_APPROVAL_REQUEST_PACKET_SMOKE: "
        f"FAIL {message}"
    )


def read_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def require_token(text: str, token: str, label: str) -> None:
    if token not in text:
        fail(f"{label} missing token {token}")


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)
    payload = read_json(OUT_JSON)
    ready_mode = payload.get("status") == "ready_for_human_workbook_import_approval"
    expected_status = (
        "ready_for_human_workbook_import_approval"
        if ready_mode
        else "hold_human_input_required"
    )
    expected_source_statuses = (
        {
            "source_safety_preflight_status": "pass_no_sensitive_values_found_pending_import_approval",
            "source_quick_fill_validator_status": "ready_for_workbook_import_pending_human_approval",
            "source_import_dry_run_status": "ready_for_workbook_import_pending_human_approval",
            "source_importer_status": "ready_for_apply_pending_explicit_human_command",
        }
        if ready_mode
        else {
            "source_safety_preflight_status": "hold_human_input_required_no_values_to_scan",
            "source_quick_fill_validator_status": "hold_human_quick_fill_required",
            "source_import_dry_run_status": "hold_human_quick_fill_required",
            "source_importer_status": "hold_human_quick_fill_required",
        }
    )
    expected_missing_conditions = (
        []
        if ready_mode
        else [
            "safety_preflight_passed",
            "quick_fill_validator_ready",
            "import_dry_run_ready",
            "importer_ready",
        ]
    )
    expected_source_conditions = (
        {
            "safety_preflight_passed": True,
            "quick_fill_validator_ready": True,
            "import_dry_run_ready": True,
            "importer_ready": True,
        }
        if ready_mode
        else {
            "safety_preflight_passed": False,
            "quick_fill_validator_ready": False,
            "import_dry_run_ready": False,
            "importer_ready": False,
        }
    )

    expected_payload = {
        "commercial_sprint_workbook_import_approval_request_packet_v0_1": True,
        "packet_type": "controlled_workbook_import_approval_request_packet",
        "packet_scope": "pre_workbook_import_approval_request_only_no_import_no_transfer_no_evidence",
        "status": expected_status,
        **expected_source_statuses,
        "approval_request_count": 1,
        "ready_import_approval_count": 1 if ready_mode else 0,
        "approved_import_count": 0,
        "workbook_import_authorized_count": 0,
        "missing_condition_count": 0 if ready_mode else 4,
        "ready_for_workbook_import_approval": ready_mode,
        "ready_for_workbook_import_execution": False,
        "human_import_approval_required": True,
        "separate_workbook_import_execution_request_required": True,
        "separate_template_transfer_request_required": True,
        "separate_validator_execution_request_required": True,
        "boundary_violation_count": 0,
    }
    for flag, expected in expected_payload.items():
        if payload.get(flag) != expected:
            fail(f"{flag} must be {expected}")
    if payload.get("missing_conditions") != expected_missing_conditions:
        fail("missing_conditions do not match source readiness")
    if payload.get("source_conditions") != expected_source_conditions:
        fail("source_conditions do not match source readiness")
    for flag in EXPECTED_FALSE:
        if payload.get(flag) is not False:
            fail(f"{flag} must be false")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")

    requests = payload.get("approval_requests", [])
    if len(requests) != 1:
        fail("approval_requests must contain exactly one request")
    request = requests[0]
    expected_request = {
        "request_id": "WIA-001",
        "request_type": "workbook_import_approval_request",
        "expected_import_row_count": 64,
        "ready_for_human_approval": ready_mode,
        "human_import_approval_recorded": False,
        "workbook_import_authorized": False,
        "import_execution_allowed": False,
        "recommended_human_decision": "approve" if ready_mode else "hold",
    }
    for flag, expected in expected_request.items():
        if request.get(flag) != expected:
            fail(f"request {flag} must be {expected}")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        fail("approval request CSV must contain one request row")
    if rows[0].get("request_id") != "WIA-001":
        fail("approval request CSV missing WIA-001")

    docs = {
        "top_doc": TOP_DOC.read_text(encoding="utf-8"),
        "report": OUT_MD.read_text(encoding="utf-8"),
        "boundary": OUT_BOUNDARY.read_text(encoding="utf-8"),
        "gate": GATE.read_text(encoding="utf-8"),
    }
    for label, text in docs.items():
        tokens = REQUIRED_GATE_TOKENS if label == "gate" else REQUIRED_DOC_TOKENS
        for token in tokens:
            require_token(text, token, label)
        if label != "gate":
            for token in [
                f"status: {expected_status}",
                f"source_safety_preflight_status: {expected_source_statuses['source_safety_preflight_status']}",
                f"source_quick_fill_validator_status: {expected_source_statuses['source_quick_fill_validator_status']}",
                f"source_import_dry_run_status: {expected_source_statuses['source_import_dry_run_status']}",
                f"source_importer_status: {expected_source_statuses['source_importer_status']}",
                f"ready_import_approval_count: {1 if ready_mode else 0}",
                f"missing_condition_count: {0 if ready_mode else 4}",
                f"ready_for_workbook_import_approval: {str(ready_mode).lower()}",
            ]:
                require_token(text, token, label)
    combined = "\n".join(docs.values())
    found = [token for token in FORBIDDEN_DOC_TOKENS if token in combined]
    if found:
        fail("forbidden doc tokens found: " + ", ".join(found))

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]
    found_runner = [token for token in forbidden_runner_tokens if token in runner_text]
    if found_runner:
        fail("runner suggests external access or execution: " + ", ".join(found_runner))

    print(
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_APPROVAL_REQUEST_PACKET_SMOKE: PASS "
        f"status={expected_status} ready_import_approval_count={1 if ready_mode else 0} "
        "workbook_import_authorized=false production_ready=false"
    )


if __name__ == "__main__":
    main()
