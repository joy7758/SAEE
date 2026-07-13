#!/usr/bin/env python3
"""Smoke check for the commercial evidence request approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_evidence_request_approval_input_validator import (
    DEFAULT_INPUT_PATH,
    DRAFT_PACKET_PATH,
    FORBIDDEN_TRUE_KEYS,
    GATE_PATH,
    OUTPUT_PATH,
    REPORT_PATH,
    SELECTED_BLOCKER_IDS,
    TOP_DOC,
    build_template,
    build_validation,
)


VALIDATOR_SCRIPT = (
    ROOT / "scripts/saee_commercial_evidence_request_approval_input_validator.py"
)
SMOKE_PASS_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS"
)
SMOKE_FAIL_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL "
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(SMOKE_FAIL_PREFIX + message)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False, invalid_decision: bool = False) -> dict[str, object]:
    packet = json.loads(DRAFT_PACKET_PATH.read_text(encoding="utf-8"))
    data = build_template(packet)
    data["input_status"] = "human_filled_fixture_for_validator_smoke_only"
    data["human_reviewer_name"] = "Fixture Reviewer"
    data["review_date"] = "2026-07-05"
    rows = data["approval_inputs"]
    assert isinstance(rows, list)
    first = rows[0]
    assert isinstance(first, dict)
    first["assigned_human_owner"] = "Fixture Owner"
    first["human_approval_reference"] = "fixture-human-approval-reference"
    first["approval_scope"] = "evidence_collection_only"
    first["approval_decision"] = "approved_for_separate_evidence_collection_request"
    first["evidence_collection_request_reference"] = "fixture-separate-evidence-request"
    first["owner_acknowledged_scope"] = True
    first["boundary_acknowledged"] = True
    if unsafe:
        boundary = data["boundary_review"]
        assert isinstance(boundary, dict)
        boundary["production_ready"] = True
    if invalid_decision:
        first["approval_decision"] = "execute_now"
    return data


def main() -> int:
    require(VALIDATOR_SCRIPT.is_file(), "validator script missing")
    default_run = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    expected_default = {
        "commercial_evidence_request_approval_input_validator_v0_1": True,
        "validator_type": "saee_commercial_evidence_request_approval_input_validator",
        "status": "pass",
        "template_type_valid": True,
        "selected_blocker_ids_match": True,
        "request_ids_match": True,
        "selected_blocker_count": 5,
        "draft_request_count": 5,
        "approved_request_count": 1,
        "held_request_count": 4,
        "approval_input_complete": True,
        "ready_for_separate_evidence_collection_request": False,
        "ready_for_separate_execution_request": True,
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
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
        "owner_contacted_by_codex": False,
        "customer_data_collected": False,
        "vendor_contacted": False,
    }
    for key, value in expected_default.items():
        require(default_summary.get(key) == value, f"default {key} must be {value}")
    require(DEFAULT_INPUT_PATH.is_file(), "default approval input template missing")
    require(OUTPUT_PATH.is_file(), "default validation output missing")
    require(default_summary["approved_request_ids"] == ["ERD-001"], "default must approve only ERD-001")
    require(default_summary["request_decision_review"], "request decision review missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_path = tmp / "complete_approval_input.json"
        unsafe_path = tmp / "unsafe_approval_input.json"
        invalid_path = tmp / "invalid_decision_approval_input.json"
        write_json(complete_path, complete_input())
        write_json(unsafe_path, complete_input(unsafe=True))
        write_json(invalid_path, complete_input(invalid_decision=True))
        complete_summary = build_validation(complete_path)
        unsafe_summary = build_validation(unsafe_path)
        invalid_summary = build_validation(invalid_path)

    require(complete_summary["status"] == "pass", "complete fixture must pass")
    require(complete_summary["approval_input_complete"] is True, "complete fixture must be complete")
    require(complete_summary["approved_request_count"] == 1, "complete fixture must approve one request")
    require(
        complete_summary["ready_for_separate_evidence_collection_request"] is True,
        "complete fixture should be ready for separate evidence request",
    )
    require(
        complete_summary["ready_for_separate_execution_request"] is False,
        "complete fixture must not be ready for separate execution request",
    )
    for key in FORBIDDEN_TRUE_KEYS:
        require(complete_summary.get(key) is False, f"complete fixture {key} must remain false")
    require(complete_summary["blockers_closed_by_validator"] == 0, "complete fixture closes no blockers")
    require(unsafe_summary["status"] == "stop", "unsafe fixture must stop")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe fixture needs boundary violation")
    require(
        unsafe_summary["ready_for_separate_evidence_collection_request"] is False,
        "unsafe fixture not ready",
    )
    require(invalid_summary["status"] == "stop", "invalid decision fixture must stop")
    require(invalid_summary["invalid_approval_decisions"], "invalid decision must be recorded")

    subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [TOP_DOC, GATE_PATH, REPORT_PATH]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [TOP_DOC, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "commercial_evidence_request_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_evidence_request_approval_pre_execution_check",
        "validation_scope: local_human_filled_evidence_request_approval_pre_execution_check",
        "selected_blocker_count: 5",
        "draft_request_count: 5",
        "approval_input_complete: true",
        "approved_request_count: 1",
        "ready_for_separate_evidence_collection_request: false",
        "ready_for_separate_execution_request: true",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_evidence_request_approval_input_validation: true",
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
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.template.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.human_filled.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_validation.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_request_approval_input_validator.py",
        "/scripts/saee_commercial_evidence_request_approval_input_validator_smoke.py",
    ]:
        require(token in llms, "llms.txt missing " + token)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_request_approval_input_validator_v0_1", {})
    for key, value in {
        "commercial_evidence_request_approval_input_validator_v0_1": True,
        "status": "pass",
        "validator_type": "saee_commercial_evidence_request_approval_input_validator",
        "validation_scope": "local_human_filled_evidence_request_approval_pre_execution_check",
        "selected_blocker_count": 5,
        "draft_request_count": 5,
        "approved_request_count": 1,
        "approval_input_complete": True,
        "ready_for_separate_evidence_collection_request": False,
        "ready_for_separate_execution_request": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "owner_contacted_by_codex": False,
        "blockers_closed_by_validator": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        SMOKE_PASS_PREFIX
        + " status=pass approval_input_complete=true approved_request_count=1 "
        + "ready_for_separate_evidence_collection_request=false "
        + "ready_for_separate_execution_request=true "
        + "blockers_closed_by_validator=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
