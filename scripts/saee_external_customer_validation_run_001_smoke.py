#!/usr/bin/env python3
"""Smoke check for SAEE External Customer Validation Run 001."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_external_customer_validation_run_001.py"
RUN_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_run_001"
)
STATUS = RUN_DIR / "external_customer_validation_run_001_status.local.json"
README = RUN_DIR / "README.md"
HUMAN_STEPS = RUN_DIR / "HUMAN_EXECUTION_STEPS.md"
CHECKLIST = RUN_DIR / "RESULT_ENTRY_CHECKLIST.md"
BOUNDARY = RUN_DIR / "BOUNDARY_AUDIT.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001: PASS" in result.stdout, "runner did not print PASS")

    for path in [STATUS, README, HUMAN_STEPS, CHECKLIST, BOUNDARY, GATE]:
        require(path.exists(), f"{path} missing")

    status = read_json(STATUS)
    expected = {
        "external_customer_validation_run_001_v0_1": True,
        "run_id": "external_customer_validation_run_001",
        "run_type": "manual_external_customer_or_target_user_validation_run",
        "status": "prepared_pending_human_external_session",
        "current_goal_blocker": "customer_validated",
        "planned_external_sessions": 1,
        "required_real_external_sessions_min": 1,
        "human_session_required": True,
        "human_session_performed": False,
        "human_result_entry_required": True,
        "human_result_entered": False,
        "records_entered": 0,
        "ready_for_import_after_human_entry": False,
        "ready_for_validator_after_import": False,
        "codex_may_contact_customer": False,
        "codex_may_run_external_session": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_collect_customer_data": False,
        "human_must_select_external_customer_or_target_user": True,
        "validator_executed": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_run": 0,
    }
    for key, value in expected.items():
        require(status.get(key) == value, f"{key} must be {value!r}")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [README, HUMAN_STEPS, CHECKLIST, BOUNDARY, GATE]
    )
    for token in [
        "prepared_pending_human_external_session",
        "customer_validated: false",
        "production_ready: false",
        "blockers_closed_by_run: 0",
        "Codex does not contact customers",
        "The session must be real.",
        "Internal founder review does not satisfy",
        "No customer-validation claim made.",
        "answer: prepared_pending_human_external_session",
    ]:
        require(token in combined, "missing token " + token)
    for forbidden in [
        "customer_validated: true",
        '"customer_validated": true',
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
    ]:
        require(forbidden not in combined, "forbidden token found: " + forbidden)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_run_001/external_customer_validation_run_001_status.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_run_001/README.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_run_001/HUMAN_EXECUTION_STEPS.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_run_001/RESULT_ENTRY_CHECKLIST.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_run_001/BOUNDARY_AUDIT.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001_GATE.md",
        "/scripts/saee_external_customer_validation_run_001.py",
        "/scripts/saee_external_customer_validation_run_001_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    entry = read_json(ROOT / "agent-index.json").get("external_customer_validation_run_001_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key, value in expected.items():
        if key == "external_customer_validation_run_001_v0_1":
            continue
        require(entry.get(key) == value, f"agent-index {key} must be {value!r}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001_SMOKE: PASS")


if __name__ == "__main__":
    main()
