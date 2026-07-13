#!/usr/bin/env python3
"""Smoke test the support-group final closure decision validator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_group_final_closure_decision_validator.py"
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SUMMARY = SUPPORT_DIR / "support_group_final_closure_decision_validation.local.json"
REPORT = SUPPORT_DIR / "support_group_final_closure_decision_validation.md"
CSV = SUPPORT_DIR / "support_group_final_closure_decision_validation.csv"
BOUNDARY = SUPPORT_DIR / "support_group_final_closure_decision_validation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR: PASS" in result.stdout,
        "runner did not pass",
    )
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "support_group_final_closure_decision_validator_v0_1": True,
        "validator_type": "human_final_closure_decision_template_validator_no_execution",
        "validator_scope": "validate_template_only_no_matrix_change_no_closure",
        "status": "ready_for_separate_matrix_update_request_no_closure",
        "target_blocker_group": "support",
        "source_request_status": "ready_for_human_final_closure_decision_input",
        "request_recommended_human_decision": "approve_for_separate_matrix_update_request",
        "human_final_decision": "approve_for_separate_matrix_update_request",
        "human_reviewer_present": True,
        "decision_date_present": True,
        "reason_present": True,
        "decision_fields_complete": True,
        "decision_allowed": True,
        "authorize_separate_matrix_update_request": True,
        "authorize_blocker_closure_now": False,
        "authorize_product_launch": False,
        "confirm_no_customer_validation_claim": True,
        "confirm_no_production_ready_claim": True,
        "separate_matrix_update_request_ready": True,
        "final_hold_recorded": False,
        "final_reject_recorded": False,
        "final_human_decision_recorded": True,
        "boundary_violation_count": 0,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_validator": 0,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("target_blockers")
        == ["support_contact", "customer_support", "sla", "on_call_rotation"],
        "target blockers must be the support group",
    )
    require(payload.get("boundary_violations") == [], "default template must have no boundary violations")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "support_group_final_closure_decision_validator_v0_1: true",
        "ready_for_separate_matrix_update_request_no_closure",
        "matrix_update_executed=false",
        "canonical_gap_matrix_modified=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_validator=0",
        "answer: ready_for_separate_matrix_update_request_no_closure",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_validator=1",
        "blocker_closure_authorized=true",
        "matrix_update_executed=true",
        "canonical_gap_matrix_modified=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_GATE.md",
        "/scripts/saee_support_group_final_closure_decision_validator.py",
        "/scripts/saee_support_group_final_closure_decision_validator_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("support_group_final_closure_decision_validator_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "human_final_decision",
        "final_human_decision_recorded",
        "separate_matrix_update_request_ready",
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "blocker_closure_authorized",
        "blockers_closed_by_validator",
        "development_permission_granted",
        "execution_authorized",
        "customer_validated",
        "production_ready",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Support Group Final Closure Decision Validator v0.1",
        "support_group_final_closure_decision_validator_v0_1",
        "ready_for_separate_matrix_update_request_no_closure",
        "final_human_decision_recorded=true",
        "separate_matrix_update_request_ready=true",
        "matrix_update_executed=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_validator=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print("SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_SMOKE: PASS")


if __name__ == "__main__":
    main()
