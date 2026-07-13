#!/usr/bin/env python3
"""Smoke test for the commercial sprint template-transfer request packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_template_transfer_execution_request_packet.py"

OUT_JSON = SPRINT_DIR / "commercial_sprint_template_transfer_execution_request_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_template_transfer_execution_request_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_template_transfer_execution_request_packet.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_template_transfer_execution_request_packet_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_TEMPLATE_TRANSFER_EXECUTION_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_TEMPLATE_TRANSFER_EXECUTION_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)

EXPECTED_FALSE = [
    "template_transfer_performed",
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
    "raw_human_values_recorded",
]

REQUIRED_DOC_TOKENS = [
    "commercial_sprint_template_transfer_execution_request_packet_v0_1: true",
    "status: ready_for_template_transfer_execution",
    "packet_scope: template_transfer_execution_request_only_no_transfer_no_validator_no_evidence",
    "source_import_applied_status: workbook_import_applied_pending_template_transfer_request",
    "execution_request_count: 1",
    "ready_execution_request_count: 1",
    "approved_execution_count: 1",
    "template_transfer_authorized_count: 1",
    "missing_condition_count: 0",
    "workbook_row_count: 65",
    "mapping_row_count: 65",
    "required_transfer_row_count: 64",
    "required_value_present_count: 64",
    "required_transfer_ready_count: 64",
    "optional_row_count: 1",
    "optional_value_present_count: 0",
    "target_template_count: 5",
    "pointer_issue_count: 0",
    "ready_for_template_transfer_request: true",
    "ready_for_separate_human_template_transfer_execution_request: true",
    "ready_for_template_transfer_execution: true",
    "human_execution_request_required: true",
    "separate_template_transfer_execution_request_required: false",
    "separate_validator_execution_request_required: true",
    "human_execution_request_recorded: true",
    "human_execution_authorized: true",
    "template_transfer_authorized: true",
    "template_transfer_performed: false",
    "values_transferred: false",
    "human_filled_templates_written: false",
    "validators_run_on_real_input: false",
    "evidence_collection_authorized: false",
    "execution_authorized: false",
    "evidence_builder_executed: false",
    "blocker_closure_authorized: false",
    "boundary_violation_count: 0",
    "raw_human_values_recorded: false",
    "production_ready: false",
    "customer_validated: false",
    "product_launched: false",
    "private_core_exposed: false",
]

REQUIRED_GATE_TOKENS = [
    "answer: conditional",
    "recommend_for_template_transfer_execution_request_packet: true",
    "recommend_for_human_execution_request_collection: true",
    "recommend_for_template_transfer_execution: true",
    "recommend_for_auto_execution: false",
    "recommend_for_validator_execution: false",
    "recommend_for_evidence_collection: false",
    "recommend_for_evidence_builder_execution: false",
    "recommend_for_blocker_closure: false",
    "recommend_for_product_launch: false",
    "recommend_for_production_readiness_claim: false",
]

FORBIDDEN_DOC_TOKENS = [
    "template_transfer_performed: true",
    '"template_transfer_performed": true',
    "values_transferred: true",
    '"values_transferred": true',
    "human_filled_templates_written: true",
    '"human_filled_templates_written": true',
    "validators_run_on_real_input: true",
    '"validators_run_on_real_input": true',
    "evidence_collection_authorized: true",
    '"evidence_collection_authorized": true',
    "\nexecution_authorized: true",
    '"execution_authorized": true',
    "blocker_closure_authorized: true",
    '"blocker_closure_authorized": true',
    "production_ready: true",
    '"production_ready": true',
    "product_launched: true",
    '"product_launched": true',
    "customer_validated: true",
    '"customer_validated": true',
    "private_core_exposed: true",
    '"private_core_exposed": true',
    "raw_human_values_recorded: true",
    '"raw_human_values_recorded": true',
    "recommend_for_auto_execution: true",
    "recommend_for_validator_execution: true",
    "recommend_for_evidence_collection: true",
    "recommend_for_evidence_builder_execution: true",
    "recommend_for_blocker_closure: true",
    "recommend_for_product_launch: true",
    "recommend_for_production_readiness_claim: true",
]


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_TEMPLATE_TRANSFER_EXECUTION_REQUEST_PACKET_SMOKE: "
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

    expected_payload = {
        "commercial_sprint_template_transfer_execution_request_packet_v0_1": True,
        "packet_type": "controlled_template_transfer_execution_request_packet",
        "packet_scope": "template_transfer_execution_request_only_no_transfer_no_validator_no_evidence",
        "status": "ready_for_template_transfer_execution",
        "source_import_applied_status": "workbook_import_applied_pending_template_transfer_request",
        "execution_request_count": 1,
        "ready_execution_request_count": 1,
        "approved_execution_count": 1,
        "template_transfer_authorized_count": 1,
        "workbook_row_count": 65,
        "mapping_row_count": 65,
        "required_transfer_row_count": 64,
        "required_value_present_count": 64,
        "required_transfer_ready_count": 64,
        "optional_row_count": 1,
        "optional_value_present_count": 0,
        "target_template_count": 5,
        "pointer_issue_count": 0,
        "ready_for_template_transfer_request": True,
        "ready_for_separate_human_template_transfer_execution_request": True,
        "ready_for_template_transfer_execution": True,
        "human_execution_request_required": True,
        "separate_template_transfer_execution_request_required": False,
        "separate_validator_execution_request_required": True,
        "human_execution_request_recorded": True,
        "human_execution_authorized": True,
        "template_transfer_authorized": True,
        "recommended_human_decision": "approve",
        "boundary_violation_count": 0,
    }
    for flag, expected in expected_payload.items():
        if payload.get(flag) != expected:
            fail(f"{flag} must be {expected!r}")
    for flag in EXPECTED_FALSE:
        if payload.get(flag) is not False:
            fail(f"{flag} must be false")
    if payload.get("missing_conditions") != []:
        fail("missing_conditions must be empty")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")
    if payload.get("source_conditions") != {
        "workbook_import_applied_ready": True,
        "imported_workbook_ready": True,
        "transfer_map_ready": True,
        "transfer_resolver_ready": True,
        "template_pointer_check_ready": True,
        "template_transfer_rows_ready": True,
    }:
        fail("source_conditions do not match ready sources")

    requests = payload.get("execution_requests", [])
    if len(requests) != 1:
        fail("execution_requests must contain exactly one request")
    request = requests[0]
    for flag, expected in {
        "request_id": "TTE-001",
        "request_type": "template_transfer_execution_request",
        "expected_required_transfer_row_count": 64,
        "target_template_count": 5,
        "ready_for_separate_human_template_transfer_execution_request": True,
        "human_execution_request_recorded": True,
        "human_execution_authorized": True,
        "template_transfer_authorized": True,
        "template_transfer_performed": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "recommended_human_decision": "approve",
    }.items():
        if request.get(flag) != expected:
            fail(f"request {flag} must be {expected!r}")
    if "--confirm-human-approved-transfer" not in request.get("target_command", ""):
        fail("target command must require explicit human-approved transfer")
    if request.get("missing_conditions") != []:
        fail("request missing_conditions must be empty")
    if payload.get("source_template_transfer_execution_approval") != (
        "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
        "commercial_sprint_template_transfer_execution_approval.local.json"
    ):
        fail("payload must point to the template transfer execution approval record")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        fail("CSV must contain one request row")
    if rows[0].get("request_id") != "TTE-001":
        fail("CSV request_id must be TTE-001")
    if rows[0].get("recommended_human_decision") != "approve":
        fail("CSV recommended decision must be approve")

    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC]:
        text = path.read_text(encoding="utf-8")
        for token in REQUIRED_DOC_TOKENS:
            require_token(text, token, str(path))
    gate = GATE.read_text(encoding="utf-8")
    for token in REQUIRED_GATE_TOKENS:
        require_token(gate, token, str(GATE))
    for token in REQUIRED_DOC_TOKENS:
        require_token(gate, token, str(GATE))

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    found = [token for token in FORBIDDEN_DOC_TOKENS if token in combined_docs]
    if found:
        fail("found forbidden claims: " + ", ".join(found))
    for raw_value_token in ["joy7758", "张斌"]:
        if raw_value_token in combined_docs:
            fail(f"raw human value leaked in docs: {raw_value_token}")

    runner = RUNNER.read_text(encoding="utf-8")
    if "--apply --confirm-human-approved-transfer" not in runner:
        fail("runner must record explicit transfer command")
    if "subprocess" in runner:
        fail("runner must not execute subprocess commands")

    print(
        "SAEE_COMMERCIAL_SPRINT_TEMPLATE_TRANSFER_EXECUTION_REQUEST_PACKET_SMOKE: PASS "
        "required_transfer_ready_count=64 template_transfer_authorized=true "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
