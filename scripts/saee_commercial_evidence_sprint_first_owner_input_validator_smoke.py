#!/usr/bin/env python3
"""Smoke check for the first-owner input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_evidence_sprint_first_owner_input_validator import (
    DEFAULT_INPUT_PATH,
    FIRST_BLOCKER_ID,
    FORBIDDEN_TRUE_KEYS,
    GATE_PATH,
    OUTPUT_PATH,
    REPORT_PATH,
    REQUIRED_FIELDS,
    TOP_DOC,
    VALID_TEMPLATE_TYPE,
    build_template,
    build_validation,
)


VALIDATOR_SCRIPT = (
    ROOT / "scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py"
)
SMOKE_PASS_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR_SMOKE: PASS"
)
SMOKE_FAIL_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR_SMOKE: FAIL "
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(SMOKE_FAIL_PREFIX + message)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    data = build_template()
    data["input_status"] = "human_filled_first_owner_fixture_for_validator_smoke_only"
    data["human_reviewer_name"] = "Fixture Reviewer"
    data["review_date"] = "2026-07-05"
    row = data["first_owner_input"]
    assert isinstance(row, dict)
    row["assigned_human_owner"] = "Fixture Owner"
    row["owner_contact_reference"] = "fixture-owner-reference"
    row["target_review_date"] = "2026-07-12"
    row["owner_acknowledged_scope"] = True
    row["human_approval_reference"] = "fixture-approval-reference"
    row["notes"] = "fixture only; not execution approval"
    if unsafe:
        boundary = data["boundary_review"]
        assert isinstance(boundary, dict)
        boundary["production_ready"] = True
    return data


def assert_false_boundaries(payload: dict[str, object], prefix: str) -> None:
    for key in FORBIDDEN_TRUE_KEYS:
        require(payload.get(key) is False, f"{prefix} {key} must remain false")
    require(payload.get("blockers_closed_by_validator") == 0, f"{prefix} closes no blockers")
    require(payload.get("ready_for_evidence_collection") is False, f"{prefix} evidence not ready")
    require(
        payload.get("ready_for_separate_evidence_collection_request") is False,
        f"{prefix} separate evidence request not ready",
    )


def main() -> int:
    require(VALIDATOR_SCRIPT.is_file(), "validator script missing")
    default_summary = build_validation(DEFAULT_INPUT_PATH)
    expected_default = {
        "validator_type": "saee_commercial_evidence_sprint_first_owner_input_validator",
        "validation_scope": "local_first_owner_input_pre_evidence_collection_check",
        "status": "hold_first_owner_input_required",
        "validation_status": "hold",
        "template_type_valid": True,
        "sequence_step_id": "SEQ-001",
        "sequence_step_valid": True,
        "first_blocker_id": FIRST_BLOCKER_ID,
        "first_blocker_valid": True,
        "selected_blocker_count": 1,
        "assigned_owner_count": 0,
        "unassigned_owner_count": 1,
        "first_owner_assignment_complete": False,
        "ready_for_human_sequence_step_002": False,
        "ready_for_full_owner_assignment_validator": False,
        "ready_for_evidence_collection": False,
        "ready_for_separate_evidence_collection_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_validator": 0,
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
        require(default_summary.get(key) == value, f"default {key} must be {value}")
    require(DEFAULT_INPUT_PATH.is_file(), "default input template missing")
    require(OUTPUT_PATH.is_file(), "default validation output missing")
    require(REPORT_PATH.is_file(), "default validation report missing")
    require(set(default_summary["missing_assignment_fields"]) == set(REQUIRED_FIELDS), "default missing fields must match required fields")

    template = json.loads(DEFAULT_INPUT_PATH.read_text(encoding="utf-8"))
    require(template.get("template_type") == VALID_TEMPLATE_TYPE, "template type invalid")
    require(template.get("input_status") == "template_not_filled", "template must be blank")
    require(template.get("sequence_step_id") == "SEQ-001", "template sequence step invalid")
    require(template.get("first_blocker_id") == FIRST_BLOCKER_ID, "template first blocker invalid")
    row = template.get("first_owner_input", {})
    require(isinstance(row, dict), "first_owner_input must be object")
    for field in ["assigned_human_owner", "owner_contact_reference", "target_review_date", "human_approval_reference"]:
        require(row.get(field) == "", f"template {field} must be blank")
    require(row.get("owner_acknowledged_scope") is False, "template scope acknowledgement false")
    boundary = template.get("boundary_review", {})
    require(isinstance(boundary, dict), "template boundary_review missing")
    require(all(value is False for value in boundary.values()), "template boundary flags false")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_path = tmp / "complete_first_owner_input.json"
        unsafe_path = tmp / "unsafe_first_owner_input.json"
        write_json(complete_path, complete_input())
        write_json(unsafe_path, complete_input(unsafe=True))
        complete_summary = build_validation(complete_path)
        unsafe_summary = build_validation(unsafe_path)

    require(complete_summary["validation_status"] == "pass", "complete fixture must pass")
    require(complete_summary["status"] == "pass_first_owner_input_complete", "complete status invalid")
    require(complete_summary["first_owner_assignment_complete"] is True, "complete fixture must be complete")
    require(complete_summary["ready_for_human_sequence_step_002"] is True, "complete fixture can proceed to SEQ-002")
    require(complete_summary["ready_for_full_owner_assignment_validator"] is False, "complete fixture is not full assignment")
    assert_false_boundaries(complete_summary, "complete fixture")
    require(unsafe_summary["validation_status"] == "stop", "unsafe fixture must stop")
    require(unsafe_summary["status"] == "stop_boundary_violation", "unsafe status invalid")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe fixture needs boundary violation")
    require(unsafe_summary["ready_for_human_sequence_step_002"] is False, "unsafe fixture cannot proceed")

    for path in [TOP_DOC, GATE_PATH, REPORT_PATH]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [TOP_DOC, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "commercial_evidence_sprint_first_owner_input_validator_v0_1: true",
        "validator_scope: local_first_owner_input_pre_evidence_collection_check",
        "sequence_step_id: SEQ-001",
        "first_blocker_id: support_contact",
        "selected_blocker_count: 1",
        "assigned_owner_count: 0",
        "unassigned_owner_count: 1",
        "first_owner_assignment_complete: false",
        "ready_for_human_sequence_step_002: false",
        "ready_for_full_owner_assignment_validator: false",
        "ready_for_evidence_collection: false",
        "ready_for_separate_evidence_collection_request: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_first_owner_input_validation: true",
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
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_validation.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_validation.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py",
        "/scripts/saee_commercial_evidence_sprint_first_owner_input_validator_smoke.py",
    ]:
        require(token in llms, "llms.txt missing " + token)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_sprint_first_owner_input_validator_v0_1", {})
    for key, value in {
        "commercial_evidence_sprint_first_owner_input_validator_v0_1": True,
        "status": "pass_first_owner_input_complete",
        "validator_type": "saee_commercial_evidence_sprint_first_owner_input_validator",
        "validation_scope": "local_first_owner_input_pre_evidence_collection_check",
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": FIRST_BLOCKER_ID,
        "selected_blocker_count": 1,
        "assigned_owner_count": 1,
        "unassigned_owner_count": 0,
        "first_owner_assignment_complete": True,
        "ready_for_human_sequence_step_002": True,
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
        "blockers_closed_by_validator": 0,
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

    print(SMOKE_PASS_PREFIX)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
