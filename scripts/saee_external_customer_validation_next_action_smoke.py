#!/usr/bin/env python3
"""Smoke test the external customer-validation next-action packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "external_customer_validation_next_action.local.json"
OUTPUT_MD = EVIDENCE_DIR / "external_customer_validation_next_action.md"
OUTPUT_CSV = EVIDENCE_DIR / "external_customer_validation_next_action_checklist.csv"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_next_action_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION_GATE.md"
RUNNER = ROOT / "scripts/saee_external_customer_validation_next_action.py"


def fail(message: str) -> None:
    raise SystemExit("SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, BOUNDARY_AUDIT, GATE, RUNNER]:
        require(path.is_file(), f"missing required file {path.relative_to(ROOT)}")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "external_customer_validation_next_action_v0_1": True,
        "status": "hold_external_customer_validation_input_required",
        "record_type": "external_customer_validation_next_action_packet",
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        "local_evidence_lanes_passed": True,
        "human_external_customer_validation_path_ready": True,
        "human_session_entry_exists": False,
        "ready_for_post_session_processor": False,
        "human_action_required": True,
        "codex_may_contact_customer": False,
        "codex_may_run_external_pilot": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_run_validator_after_human_filled_input": True,
        "separate_evidence_builder_request_required": True,
        "separate_commercial_go_no_go_update_required": True,
        "customer_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "public_sdk_released": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized_by_codex": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_next_action": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(
        payload.get("result_entry_workbench")
        == "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html",
        "result_entry_workbench path changed",
    )
    require(
        payload.get("required_human_output")
        == "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json",
        "required_human_output path changed",
    )
    require(
        payload.get("post_session_processor_command")
        == "python3 scripts/saee_external_customer_validation_post_session_processor.py",
        "post session processor command changed",
    )

    checklist = payload.get("checklist", [])
    require(isinstance(checklist, list), "checklist must be list")
    require(len(checklist) == 7, "checklist must contain seven rows")
    require(
        [row.get("step_id") for row in checklist]
        == ["CV-001", "CV-002", "CV-003", "CV-004", "CV-005", "CV-006", "CV-007"],
        "checklist step ids changed",
    )
    codex_allowed = {row.get("step_id"): row.get("codex_allowed") for row in checklist}
    require(codex_allowed.get("CV-006") is True, "only validator step may allow Codex")
    require(
        all(value is False for step, value in codex_allowed.items() if step != "CV-006"),
        "Codex must not be allowed to perform human evidence steps",
    )

    combined = (
        OUTPUT_MD.read_text(encoding="utf-8")
        + "\n"
        + BOUNDARY_AUDIT.read_text(encoding="utf-8")
        + "\n"
        + GATE.read_text(encoding="utf-8")
    )
    for token in [
        "external_customer_validation_next_action_v0_1: true",
        "status: hold_external_customer_validation_input_required",
        "current_goal_blocker: customer_validated",
        "human_external_customer_validation_path_ready: true",
        "external_customer_validation_session_entry_workbench.html",
        "external_customer_validation_session_entry.human_filled.local.json",
        "human_session_entry_exists: false",
        "codex_may_contact_customer: false",
        "codex_may_run_external_pilot: false",
        "codex_may_infer_customer_feedback: false",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_next_action: 0",
        "answer: hold_external_customer_validation_input_required",
    ]:
        require(token in combined, "missing report/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_next_action.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_next_action.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_next_action_boundary_audit.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION_GATE.md",
        "/scripts/saee_external_customer_validation_next_action.py",
        "/scripts/saee_external_customer_validation_next_action_smoke.py",
    ]:
        require(token in llms, "llms.txt missing token: " + token)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "external-customer-validation-next-action-smoke:",
        "check-external-customer-validation-next-action:",
        "scripts/saee_external_customer_validation_next_action_smoke.py",
    ]:
        require(token in makefile, "Makefile missing token: " + token)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("external_customer_validation_next_action_v0_1", {})
    require(isinstance(entry, dict), "agent-index entry must be object")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION_SMOKE: PASS "
        "remaining_blocker=customer_validated production_ready=false"
    )


if __name__ == "__main__":
    main()
