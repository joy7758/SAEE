#!/usr/bin/env python3
"""Smoke check for the commercial sprint validator execution run record."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_validator_execution_run.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_validator_execution_run.md"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_validator_execution_run_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN_SMOKE: FAIL: {message}")


def require_file(path: Path) -> str:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    payload = json.loads(require_file(OUT_JSON))
    report = require_file(OUT_MD)
    boundary = require_file(OUT_BOUNDARY)
    gate = require_file(GATE)
    agent_index = json.loads(require_file(ROOT / "agent-index.json"))
    llms = require_file(ROOT / "llms.txt")
    makefile = require_file(ROOT / "Makefile")

    expected = {
        "commercial_sprint_validator_execution_run_v0_1": True,
        "run_type": "human_approved_local_validator_execution_only",
        "human_validator_execution_authorized": True,
        "validator_execution_authorized": True,
        "validators_run_on_real_input": True,
        "planned_validator_count": 5,
        "validators_run_count": 5,
        "evidence_collection_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "development_permission_granted": False,
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
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("status") not in {
        "completed_all_validators_passed",
        "completed_with_validator_holds",
        "completed_with_validator_stop",
        "completed_with_mixed_validator_status",
    }:
        fail("unexpected validator execution status")
    results = payload.get("validation_results", [])
    if len(results) != 5:
        fail("validation_results must contain five validators")
    expected_runners = {
        "scripts/saee_support_contact_approval_input_validator.py",
        "scripts/saee_pricing_page_approval_input_validator.py",
        "scripts/saee_formal_security_review_approval_input_validator.py",
        "scripts/saee_production_restore_policy_approval_input_validator.py",
        "scripts/saee_production_monitoring_approval_input_validator.py",
    }
    if {row.get("runner") for row in results} != expected_runners:
        fail("validator execution results must reference the five expected validators")
    if any(row.get("return_code") != 0 for row in results):
        fail("all validator commands must exit 0")
    if any(row.get("blockers_closed_by_validator") != 0 for row in results):
        fail("validators must not close blockers")
    for token in [
        "commercial_sprint_validator_execution_run_v0_1: true",
        "validators_run_on_real_input: true",
        "evidence_collection_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
    ]:
        for name, text in [("report", report), ("boundary", boundary)]:
            if token not in text:
                fail(f"{name} missing token {token}")
    if "answer: local_validator_execution_recorded" not in gate:
        fail("gate missing local validator execution answer")
    for token in [
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_validator_execution_run.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_validator_execution_run.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_validator_execution_run_boundary_audit.md",
        "/scripts/saee_commercial_sprint_validator_execution_run.py",
        "/scripts/saee_commercial_sprint_validator_execution_run_smoke.py",
    ]:
        if token not in llms:
            fail("llms.txt missing validator execution path: " + token)
    for token in [
        "check-commercial-sprint-validator-execution-run:",
        "commercial-sprint-validator-execution-run-smoke:",
        "scripts/saee_commercial_sprint_validator_execution_run_smoke.py",
    ]:
        if token not in makefile:
            fail("Makefile missing validator execution token: " + token)
    entry = agent_index.get("commercial_sprint_validator_execution_run_v0_1", {})
    for key, value in {
        "human_validator_execution_authorized": True,
        "validator_execution_authorized": True,
        "validators_run_on_real_input": True,
        "validators_run_count": 5,
        "evidence_collection_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        if entry.get(key) != value:
            fail(f"agent-index validator execution {key} must be {value!r}")
    print(
        "SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN_SMOKE: PASS "
        f"status={payload['status']} validators_run_count=5 production_ready=false"
    )


if __name__ == "__main__":
    main()
