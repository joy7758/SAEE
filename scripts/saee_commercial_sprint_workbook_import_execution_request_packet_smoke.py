#!/usr/bin/env python3
"""Smoke test for the commercial sprint workbook import execution request packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_workbook_import_execution_request_packet.py"

OUT_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)

EXPECTED_FALSE = [
    "human_execution_request_recorded",
    "human_execution_authorized",
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
    "commercial_sprint_workbook_import_execution_request_packet_v0_1: true",
    "status: ready_for_separate_human_execution_request",
    "packet_scope: execution_request_only_no_import_no_transfer_no_evidence",
    "source_approval_packet_status: ready_for_human_workbook_import_approval",
    "source_importer_status: ready_for_apply_pending_explicit_human_command",
    "execution_request_count: 1",
    "ready_execution_request_count: 1",
    "approved_execution_count: 0",
    "workbook_import_authorized_count: 0",
    "missing_condition_count: 0",
    "ready_for_workbook_import_approval: true",
    "ready_for_separate_human_execution_request: true",
    "ready_for_workbook_import_execution: false",
    "human_execution_request_required: true",
    "separate_workbook_import_execution_request_required: true",
    "human_execution_request_recorded: false",
    "human_execution_authorized: false",
    "workbook_import_authorized: false",
    "workbook_import_performed: false",
    "workbook_written: false",
    "validators_run_on_real_input: false",
    "evidence_collection_authorized: false",
    "execution_authorized: false",
    "blocker_closure_authorized: false",
    "boundary_violation_count: 0",
    "production_ready: false",
    "customer_validated: false",
    "product_launched: false",
    "private_core_exposed: false",
]

REQUIRED_GATE_TOKENS = [
    "answer: conditional",
    "recommend_for_workbook_import_execution_request_packet: true",
    "recommend_for_human_execution_request_collection: true",
    "recommend_for_workbook_import_execution: false",
    "recommend_for_auto_execution: false",
    "recommend_for_template_transfer: false",
    "recommend_for_validator_execution: false",
    "recommend_for_evidence_collection: false",
    "recommend_for_evidence_builder_execution: false",
    "recommend_for_blocker_closure: false",
    "recommend_for_product_launch: false",
    "recommend_for_production_readiness_claim: false",
]

FORBIDDEN_DOC_TOKENS = [
    "human_execution_authorized: true",
    "\"human_execution_authorized\": true",
    "workbook_import_authorized: true",
    "\"workbook_import_authorized\": true",
    "workbook_import_performed: true",
    "\"workbook_import_performed\": true",
    "workbook_written: true",
    "\"workbook_written\": true",
    "validators_run_on_real_input: true",
    "\"validators_run_on_real_input\": true",
    "evidence_collection_authorized: true",
    "\"evidence_collection_authorized\": true",
    "execution_authorized: true",
    "\"execution_authorized\": true",
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
    "recommend_for_auto_execution: true",
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
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_SMOKE: "
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
        "commercial_sprint_workbook_import_execution_request_packet_v0_1": True,
        "packet_type": "controlled_workbook_import_execution_request_packet",
        "packet_scope": "execution_request_only_no_import_no_transfer_no_evidence",
        "status": "ready_for_separate_human_execution_request",
        "source_approval_packet_status": "ready_for_human_workbook_import_approval",
        "source_importer_status": "ready_for_apply_pending_explicit_human_command",
        "execution_request_count": 1,
        "ready_execution_request_count": 1,
        "approved_execution_count": 0,
        "workbook_import_authorized_count": 0,
        "missing_condition_count": 0,
        "ready_for_workbook_import_approval": True,
        "ready_for_separate_human_execution_request": True,
        "ready_for_workbook_import_execution": False,
        "human_execution_request_required": True,
        "separate_workbook_import_execution_request_required": True,
        "separate_template_transfer_request_required": True,
        "separate_validator_execution_request_required": True,
        "target_command": (
            "python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py "
            "--apply --confirm-human-approved-import"
        ),
        "expected_import_row_count": 64,
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
    if payload.get("source_conditions") != {
        "approval_packet_ready": True,
        "importer_ready": True,
    }:
        fail("source_conditions do not match ready sources")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")

    requests = payload.get("execution_requests", [])
    if len(requests) != 1:
        fail("execution_requests must contain exactly one request")
    request = requests[0]
    expected_request = {
        "request_id": "WIE-001",
        "request_type": "workbook_import_execution_request",
        "expected_import_row_count": 64,
        "ready_for_separate_human_execution_request": True,
        "human_execution_request_recorded": False,
        "human_execution_authorized": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "recommended_human_decision": "approve",
    }
    for flag, expected in expected_request.items():
        if request.get(flag) != expected:
            fail(f"request {flag} must be {expected!r}")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        fail("CSV must contain one request row")
    if rows[0].get("request_id") != "WIE-001":
        fail("CSV request_id must be WIE-001")
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

    runner = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser"]
    found_runner_tokens = [token for token in forbidden_runner_tokens if token in runner]
    if found_runner_tokens:
        fail("runner suggests external access: " + ", ".join(found_runner_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms_paths = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_execution_request_packet.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_execution_request_packet.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_execution_request_packet.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_execution_request_packet_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_workbook_import_execution_request_packet.py",
        "/scripts/saee_commercial_sprint_workbook_import_execution_request_packet_smoke.py",
    ]
    missing_llms = [path for path in required_llms_paths if path not in llms]
    if missing_llms:
        fail("llms.txt missing execution request paths: " + ", ".join(missing_llms))

    for required_file in [
        "README.md",
        "PROJECT_STATUS.md",
        "ROADMAP.md",
        "CHANGELOG.md",
        "agent-readable.md",
    ]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        if "commercial_sprint_workbook_import_execution_request_packet_v0_1" not in text:
            fail(f"{required_file} missing execution request packet reference")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    if "check-commercial-sprint-workbook-import-execution-request-packet" not in makefile:
        fail("Makefile missing check-commercial-sprint-workbook-import-execution-request-packet")
    if (
        "scripts/saee_commercial_sprint_workbook_import_execution_request_packet_smoke.py"
        not in makefile
    ):
        fail("Makefile missing execution request packet smoke")

    agent_index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = agent_index.get(
        "commercial_sprint_workbook_import_execution_request_packet_v0_1", {}
    )
    for flag, expected in {
        **expected_payload,
        **{flag: False for flag in EXPECTED_FALSE},
    }.items():
        if entry.get(flag) != expected:
            fail(f"agent-index entry {flag} must be {expected!r}")

    print("SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
