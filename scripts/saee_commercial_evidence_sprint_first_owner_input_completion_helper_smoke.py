#!/usr/bin/env python3
"""Smoke check for the first-owner input completion helper."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_evidence_sprint_first_owner_input_completion_helper import (
    COMPLETION_CSV_PATH,
    CSV_FIELDS,
    GATE_PATH,
    GUIDE_PATH,
    STATUS_JSON_PATH,
    STATUS_MD_PATH,
    TOP_DOC_PATH,
)
from scripts.saee_commercial_evidence_sprint_first_owner_input_validator import (
    build_validation,
)


HELPER_SCRIPT = (
    ROOT / "scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper.py"
)
SMOKE_PASS_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER_SMOKE: PASS"
)
SMOKE_FAIL_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER_SMOKE: FAIL "
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(SMOKE_FAIL_PREFIX + message)


def main() -> int:
    require(HELPER_SCRIPT.is_file(), "helper script missing")
    default_run = subprocess.run(
        [sys.executable, str(HELPER_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_status = json.loads(default_run.stdout)
    expected_default = {
        "helper_type": "saee_commercial_evidence_sprint_first_owner_input_completion_helper",
        "helper_scope": "local_first_owner_input_completion_sheet_and_generation_helper",
        "status": "hold_human_first_owner_input_required",
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": "support_contact",
        "completion_sheet_ready": True,
        "selected_blocker_count": 1,
        "human_first_owner_input_required": True,
        "assigned_owner_count": 0,
        "unassigned_owner_count": 1,
        "first_owner_assignment_complete": False,
        "ready_for_first_owner_input_validator": False,
        "ready_for_full_owner_assignment_validator": False,
        "ready_for_evidence_collection": False,
        "ready_for_separate_evidence_collection_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_helper": 0,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "owner_contacted_by_codex": False,
        "owner_assigned_by_codex": False,
    }
    for key, value in expected_default.items():
        require(default_status.get(key) == value, f"default {key} must be {value}")
    require(STATUS_JSON_PATH.is_file(), "status JSON missing")
    require(STATUS_MD_PATH.is_file(), "status report missing")
    require(COMPLETION_CSV_PATH.is_file(), "completion CSV missing")
    with COMPLETION_CSV_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == CSV_FIELDS, "CSV header changed")
        rows = list(reader)
    require(len(rows) == 1, "CSV must contain one data row")
    row = rows[0]
    require(row.get("blocker_id") == "support_contact", "CSV blocker must be support_contact")
    for field in [
        "assigned_human_owner",
        "owner_contact_reference",
        "target_review_date",
        "owner_acknowledged_scope",
        "human_approval_reference",
    ]:
        require(row.get(field) == "", f"CSV {field} must be blank")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_input = Path(tmpdir) / "first_owner_input.human_filled.local.json"
        filled_run = subprocess.run(
            [
                sys.executable,
                str(HELPER_SCRIPT),
                "--assigned-human-owner",
                "Fixture Owner",
                "--owner-contact-reference",
                "fixture-owner-reference",
                "--target-review-date",
                "2026-07-12",
                "--owner-acknowledged-scope",
                "true",
                "--human-approval-reference",
                "fixture-approval-reference",
                "--output-input-json",
                str(output_input),
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        filled_status = json.loads(filled_run.stdout)
        require(output_input.is_file(), "human-filled input not generated")
        validation = build_validation(output_input)

    require(
        filled_status["status"] == "ready_for_first_owner_input_validator",
        "filled status invalid",
    )
    require(filled_status["assigned_owner_count"] == 1, "filled assigned count invalid")
    require(
        filled_status["ready_for_first_owner_input_validator"] is True,
        "filled status should be validator-ready",
    )
    require(filled_status["ready_for_evidence_collection"] is False, "filled status cannot collect evidence")
    require(filled_status["blockers_closed_by_helper"] == 0, "filled status closes no blockers")
    require(validation["validation_status"] == "pass", "generated input must pass validator")
    require(
        validation["ready_for_human_sequence_step_002"] is True,
        "generated input can proceed only to SEQ-002",
    )
    require(validation["ready_for_evidence_collection"] is False, "validator does not allow evidence collection")
    require(validation["blockers_closed_by_validator"] == 0, "validator closes no blockers")

    restore_run = subprocess.run(
        [sys.executable, str(HELPER_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    restored_status = json.loads(restore_run.stdout)
    require(
        restored_status["status"] == "hold_human_first_owner_input_required",
        "default status was not restored after fixture generation",
    )

    for path in [TOP_DOC_PATH, GATE_PATH, STATUS_MD_PATH, GUIDE_PATH]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [TOP_DOC_PATH, GATE_PATH, STATUS_MD_PATH, GUIDE_PATH]
    )
    for token in [
        "commercial_evidence_sprint_first_owner_input_completion_helper_v0_1: true",
        "helper_scope: local_first_owner_input_completion_sheet_and_generation_helper",
        "sequence_step_id: SEQ-001",
        "first_blocker_id: support_contact",
        "completion_sheet_ready: true",
        "assigned_owner_count: 0",
        "unassigned_owner_count: 1",
        "first_owner_assignment_complete: false",
        "ready_for_first_owner_input_validator: false",
        "ready_for_evidence_collection: false",
        "ready_for_separate_evidence_collection_request: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_helper: 0",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_first_owner_input_completion_support: true",
        "recommend_for_first_owner_input_generation: true",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
    ]:
        require(token in combined, "missing doc/gate/report token " + token)

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "owner_contacted_by_codex: true",
        '"owner_contacted_by_codex": true',
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_guide.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_status.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_status.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper.py",
        "/scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper_smoke.py",
    ]:
        require(token in llms, "llms.txt missing " + token)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_sprint_first_owner_input_completion_helper_v0_1", {})
    for key, value in {
        "commercial_evidence_sprint_first_owner_input_completion_helper_v0_1": True,
        "status": "hold_human_first_owner_input_required",
        "helper_type": "saee_commercial_evidence_sprint_first_owner_input_completion_helper",
        "helper_scope": "local_first_owner_input_completion_sheet_and_generation_helper",
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": "support_contact",
        "completion_sheet_ready": True,
        "selected_blocker_count": 1,
        "assigned_owner_count": 0,
        "unassigned_owner_count": 1,
        "first_owner_assignment_complete": False,
        "ready_for_first_owner_input_validator": False,
        "ready_for_full_owner_assignment_validator": False,
        "ready_for_evidence_collection": False,
        "ready_for_separate_evidence_collection_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "owner_contacted_by_codex": False,
        "owner_assigned_by_codex": False,
        "task_candidates_executed": False,
        "blockers_closed_by_helper": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        SMOKE_PASS_PREFIX
        + " status=hold_human_first_owner_input_required completion_sheet_ready=true "
        + "assigned_owner_count=0 blockers_closed_by_helper=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
