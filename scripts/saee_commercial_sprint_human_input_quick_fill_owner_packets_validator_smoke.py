#!/usr/bin/env python3
"""Smoke check for quick-fill owner packet completion validator."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "quick_fill_owner_packets"
)
OUT_JSON = (
    PACKET_DIR
    / "commercial_sprint_human_input_quick_fill_owner_packets_validation.local.json"
)
OUT_MD = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_validation.md"
OUT_CSV = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_validation.csv"
OUT_BOUNDARY = (
    PACKET_DIR
    / "commercial_sprint_human_input_quick_fill_owner_packets_validation_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_RECOMMENDATION_GATE.md"
)
COMPLETED_STATUS = "completed_owner_packet_values_pending_workbook_import_approval_review"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_SMOKE: "
        f"FAIL: {message}"
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator.py",
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))

    expected = {
        "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1": True,
        "validator_type": "local_owner_packet_completion_validator",
        "validator_scope": "owner_packet_human_value_completion_only_no_merge_no_import",
        "status": COMPLETED_STATUS,
        "owner_packet_count": 5,
        "quick_fill_row_count": 64,
        "required_owner_packet_row_count": 64,
        "completed_owner_packet_row_count": 64,
        "missing_owner_packet_row_count": 0,
        "all_owner_packets_complete": True,
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_workbook_import_approval_review": True,
        "local_owner_packet_validator_run": True,
        "raw_values_recorded": False,
        "unsafe_value_pattern_hit_count": 0,
        "forbidden_claim_pattern_hit_count": 0,
        "ready_for_quick_fill_merge": False,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_owner_packet_validator": 0,
        "boundary_violation_count": 0,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "vendor_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "task_candidates_executed": False,
        "payment_collected": False,
        "revenue_validated": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must remain empty")
    if payload.get("duplicate_quick_fill_row_ids") != []:
        fail("duplicate_quick_fill_row_ids must remain empty")

    expected_counts = {
        "formal_security_review": 12,
        "pricing_page": 14,
        "production_monitoring": 10,
        "production_restore_policy": 13,
        "support_contact": 15,
    }
    if payload.get("owner_packet_rows_by_blocker") != expected_counts:
        fail("owner packet blocker counts changed")

    rows = payload.get("validation_rows", [])
    if len(rows) != 64:
        fail("validation_rows must contain 64 rows")
    if sum(1 for row in rows if row.get("human_value_present")) != 64:
        fail("current owner packets must contain 64 human-confirmed values")
    if sum(1 for row in rows if row.get("notes_present")) != 64:
        fail("current owner packets must contain 64 human-confirmed notes")
    if sum(1 for row in rows if row.get("row_complete")) != 64:
        fail("current owner packet rows must be complete")
    if any(row.get("status") != "present_unvalidated_human_value" for row in rows):
        fail("current owner packet rows must be present_unvalidated_human_value")
    if any(row.get("raw_value_recorded") for row in rows):
        fail("raw values must not be recorded")
    for flag in [
        "value_merged_to_quick_fill",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
    ]:
        if any(row.get(flag) for row in rows):
            fail(f"{flag} must remain false for every row")

    csv_rows = read_csv(OUT_CSV)
    if len(csv_rows) != 64:
        fail("validation CSV must contain 64 rows")

    required_tokens = [
        "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1: true",
        f"status: {COMPLETED_STATUS}",
        "validator_scope: owner_packet_human_value_completion_only_no_merge_no_import",
        "owner_packet_count: 5",
        "quick_fill_row_count: 64",
        "required_owner_packet_row_count: 64",
        "completed_owner_packet_row_count: 64",
        "missing_owner_packet_row_count: 0",
        "all_owner_packets_complete: true",
        "ready_for_workbook_import_approval_review: true",
        "raw_values_recorded: false",
        "unsafe_value_pattern_hit_count: 0",
        "forbidden_claim_pattern_hit_count: 0",
        "ready_for_quick_fill_merge: false",
        "ready_for_workbook_import: false",
        "workbook_import_authorized: false",
        "workbook_import_performed: false",
        "validators_run_on_real_input: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_owner_packet_validator: 0",
        "boundary_violation_count: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")

    gate = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: recommend",
        "recommend_for_owner_packet_completion_validation: true",
        "recommend_for_human_fill_coordination: true",
        "recommend_for_raw_value_storage: false",
        "recommend_for_value_merge: false",
        "recommend_for_value_import: false",
        "recommend_for_value_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        if token not in gate:
            fail(f"gate missing token {token}")

    runner = (
        ROOT
        / "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    forbidden_tokens = [
        "production_ready: true",
        "\"production_ready\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "vendor_contacted: true",
        "\"vendor_contacted\": true",
        "development_permission_granted: true",
        "\"development_permission_granted\": true",
        "execution_authorized: true",
        "\"execution_authorized\": true",
        "evidence_collection_authorized: true",
        "\"evidence_collection_authorized\": true",
        "evidence_builder_executed: true",
        "\"evidence_builder_executed\": true",
        "blocker_closure_authorized: true",
        "\"blocker_closure_authorized\": true",
        "workbook_import_authorized: true",
        "\"workbook_import_authorized\": true",
        "workbook_import_performed: true",
        "\"workbook_import_performed\": true",
        "workbook_written: true",
        "\"workbook_written\": true",
        "validators_run_on_real_input: true",
        "\"validators_run_on_real_input\": true",
        "values_transferred: true",
        "\"values_transferred\": true",
        "human_filled_templates_written: true",
        "\"human_filled_templates_written\": true",
        "recommend_for_raw_value_storage: true",
        "recommend_for_value_merge: true",
        "recommend_for_value_import: true",
        "recommend_for_value_transfer: true",
        "recommend_for_real_evidence: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
        "recommend_for_production_readiness_claim: true",
    ]
    combined_docs = "\n".join(
        [
            OUT_MD.read_text(encoding="utf-8"),
            OUT_BOUNDARY.read_text(encoding="utf-8"),
            TOP_DOC.read_text(encoding="utf-8"),
            gate,
        ]
    )
    found = [token for token in forbidden_tokens if token in combined_docs]
    if found:
        fail("forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms_paths = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/quick_fill_owner_packets/commercial_sprint_human_input_quick_fill_owner_packets_validation.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/quick_fill_owner_packets/commercial_sprint_human_input_quick_fill_owner_packets_validation.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/quick_fill_owner_packets/commercial_sprint_human_input_quick_fill_owner_packets_validation.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/quick_fill_owner_packets/commercial_sprint_human_input_quick_fill_owner_packets_validation_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator.py",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator_smoke.py",
    ]
    missing_llms = [path for path in required_llms_paths if path not in llms]
    if missing_llms:
        fail("llms.txt missing paths: " + ", ".join(missing_llms))

    for required_file in [
        "README.md",
        "PROJECT_STATUS.md",
        "ROADMAP.md",
        "CHANGELOG.md",
        "agent-readable.md",
    ]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        if (
            "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1"
            not in text
        ):
            fail(f"{required_file} missing owner packets validator token")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    if (
        "check-commercial-sprint-human-input-quick-fill-owner-packets-validator"
        not in makefile
    ):
        fail("Makefile missing owner packets validator check")
    if (
        "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator_smoke.py"
        not in makefile
    ):
        fail("Makefile missing owner packets validator smoke")

    agent_index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = agent_index.get(
        "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1", {}
    )
    expected_entry = {
        "status": COMPLETED_STATUS,
        "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1": True,
        "validator_type": "local_owner_packet_completion_validator",
        "validator_scope": "owner_packet_human_value_completion_only_no_merge_no_import",
        "owner_packet_count": 5,
        "quick_fill_row_count": 64,
        "required_owner_packet_row_count": 64,
        "completed_owner_packet_row_count": 64,
        "missing_owner_packet_row_count": 0,
        "all_owner_packets_complete": True,
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_workbook_import_approval_review": True,
        "local_owner_packet_validator_run": True,
        "raw_values_recorded": False,
        "unsafe_value_pattern_hit_count": 0,
        "forbidden_claim_pattern_hit_count": 0,
        "ready_for_quick_fill_merge": False,
        "ready_for_workbook_import": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "vendor_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_owner_packet_validator": 0,
        "payment_collected": False,
        "revenue_validated": False,
    }
    for flag, expected_value in expected_entry.items():
        if entry.get(flag) != expected_value:
            fail(f"agent-index owner packets validator {flag} must be {expected_value}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_SMOKE: PASS "
        f"status={payload['status']} "
        f"owner_packet_count={payload['owner_packet_count']} "
        f"completed_owner_packet_row_count={payload['completed_owner_packet_row_count']} "
        f"missing_owner_packet_row_count={payload['missing_owner_packet_row_count']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
