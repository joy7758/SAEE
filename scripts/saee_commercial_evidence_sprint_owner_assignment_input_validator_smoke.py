#!/usr/bin/env python3
"""Smoke check for the owner assignment input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_evidence_sprint_owner_assignment_input_validator import (
    DEFAULT_INPUT_PATH,
    FORBIDDEN_TRUE_KEYS,
    GATE_PATH,
    OUTPUT_PATH,
    REPORT_PATH,
    SELECTED_BLOCKER_IDS,
    SOURCE_PACKET_PATH,
    TOP_DOC,
    build_template,
    build_validation,
)


VALIDATOR_SCRIPT = (
    ROOT / "scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py"
)
SMOKE_PASS_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR_SMOKE: PASS"
)
SMOKE_FAIL_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR_SMOKE: FAIL "
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(SMOKE_FAIL_PREFIX + message)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    packet = json.loads(SOURCE_PACKET_PATH.read_text(encoding="utf-8"))
    data = build_template(packet)
    data["input_status"] = "human_filled_fixture_for_validator_smoke_only"
    data["human_reviewer_name"] = "Fixture Reviewer"
    data["review_date"] = "2026-07-05"
    rows = data["assignment_inputs"]
    assert isinstance(rows, list)
    for row in rows:
        assert isinstance(row, dict)
        row["assigned_human_owner"] = "Fixture Owner"
        row["owner_contact_reference"] = "fixture-owner-reference"
        row["target_review_date"] = "2026-07-12"
        row["owner_acknowledged_scope"] = True
        row["human_approval_reference"] = "fixture-approval-reference"
        row["evidence_collection_request_reference"] = ""
    if unsafe:
        boundary = data["boundary_review"]
        assert isinstance(boundary, dict)
        boundary["production_ready"] = True
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
        "validator_type": "saee_commercial_evidence_sprint_owner_assignment_input_validator",
        "validation_status": "hold",
        "template_type_valid": True,
        "selected_blocker_ids_match": True,
        "selected_blocker_count": 5,
        "assigned_owner_count": 0,
        "unassigned_owner_count": 5,
        "owner_assignment_complete": False,
        "ready_for_separate_evidence_collection_request": False,
        "human_review_required": True,
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
    }
    for key, value in expected_default.items():
        require(default_summary.get(key) == value, f"default {key} must be {value}")
    require(DEFAULT_INPUT_PATH.is_file(), "default input template missing")
    require(OUTPUT_PATH.is_file(), "default validation output missing")
    require(set(default_summary["missing_assignment_fields"]) == set(SELECTED_BLOCKER_IDS), "default missing fields must cover all blockers")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_path = tmp / "complete_owner_assignment_input.json"
        unsafe_path = tmp / "unsafe_owner_assignment_input.json"
        write_json(complete_path, complete_input())
        write_json(unsafe_path, complete_input(unsafe=True))
        complete_summary = build_validation(complete_path)
        unsafe_summary = build_validation(unsafe_path)

    require(complete_summary["validation_status"] == "pass", "complete fixture must pass")
    require(complete_summary["owner_assignment_complete"] is True, "complete fixture must be complete")
    require(
        complete_summary["ready_for_separate_evidence_collection_request"] is True,
        "complete fixture should be ready for separate request",
    )
    for key in FORBIDDEN_TRUE_KEYS:
        require(complete_summary.get(key) is False, f"complete fixture {key} must remain false")
    require(complete_summary["blockers_closed_by_validator"] == 0, "complete fixture closes no blockers")
    require(unsafe_summary["validation_status"] == "stop", "unsafe fixture must stop")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe fixture needs boundary violation")
    require(unsafe_summary["ready_for_separate_evidence_collection_request"] is False, "unsafe fixture not ready")

    subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [TOP_DOC, GATE_PATH, REPORT_PATH]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in [TOP_DOC, GATE_PATH, REPORT_PATH])
    for token in [
        "commercial_evidence_sprint_owner_assignment_input_validator_v0_1: true",
        "validator_scope: local_human_filled_owner_assignment_pre_evidence_collection_check",
        "selected_blocker_count: 5",
        "assigned_owner_count: 0",
        "unassigned_owner_count: 5",
        "owner_assignment_complete: false",
        "ready_for_separate_evidence_collection_request: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_owner_assignment_input_validation: true",
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
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.template.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_validation.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_validation.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py",
        "/scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator_smoke.py",
    ]:
        require(token in llms, "llms.txt missing " + token)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_sprint_owner_assignment_input_validator_v0_1", {})
    for key, value in {
        "commercial_evidence_sprint_owner_assignment_input_validator_v0_1": True,
        "status": "hold",
        "validator_type": "saee_commercial_evidence_sprint_owner_assignment_input_validator",
        "validation_scope": "local_human_filled_owner_assignment_pre_evidence_collection_check",
        "selected_blocker_count": 5,
        "assigned_owner_count": 0,
        "unassigned_owner_count": 5,
        "owner_assignment_complete": False,
        "ready_for_separate_evidence_collection_request": False,
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
        + " status=hold owner_assignment_complete=false "
        + "ready_for_separate_evidence_collection_request=false "
        + "blockers_closed_by_validator=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
