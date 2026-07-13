#!/usr/bin/env python3
"""Smoke check for the ERD-001 support-contact evidence-builder execution request."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_contact_evidence_builder_execution_request.py"
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
REQUEST_OUTPUT = SUPPORT_DIR / "support_contact_evidence_builder_execution_request.local.json"
REQUEST_REPORT = SUPPORT_DIR / "support_contact_evidence_builder_execution_request.md"
BOUNDARY_AUDIT = SUPPORT_DIR / "support_contact_evidence_builder_execution_request_boundary_audit.md"
BUILDER_OUTPUT = SUPPORT_DIR / "support_contact_evidence_builder_output.human_filled.local.json"
SUPPORT_OUTPUT = SUPPORT_DIR / "production_support_sla_evidence.from_support_contact.human_filled.local.json"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST_SMOKE: FAIL: "
            + message
        )


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
    require(
        "SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST: PASS"
        in result.stdout,
        "runner did not print PASS",
    )
    for path in [REQUEST_OUTPUT, REQUEST_REPORT, BOUNDARY_AUDIT, BUILDER_OUTPUT, SUPPORT_OUTPUT, GATE]:
        require(path.exists(), f"{path} missing")

    payload = read_json(REQUEST_OUTPUT)
    expected = {
        "support_contact_evidence_builder_execution_request_v0_1": True,
        "request_id": "ERD-001-support-contact-evidence-builder-request-2026-07-09",
        "source_request_id": "ERD-001",
        "status": "local_evidence_builder_executed_pending_closure_review",
        "request_approved": True,
        "approval_input_validator_passed": True,
        "human_filled_input_available": True,
        "evidence_builder_execution_authorized": True,
        "evidence_builder_executed": True,
        "support_evidence_output_created_by_request": True,
        "builder_status": "pass",
        "builder_input_complete": True,
        "support_contact_available_for_review": True,
        "production_support_available": False,
        "blockers_closed_by_request": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required_for_closure": True,
        "separate_closure_approval_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "support_vendor_contacted": False,
        "support_vendor_contacted_by_codex": False,
        "support_contact_published": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_performed": False,
        "support_contact_test_sent_by_codex": False,
        "customer_facing_support_contact_configured": False,
        "customer_support_available": False,
        "support_process_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "production_ready": False,
        "customer_validated": False,
        "public_sdk_released": False,
        "external_calls_made_by_codex": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "blocker_closure_authorized": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    builder = read_json(BUILDER_OUTPUT)
    support = read_json(SUPPORT_OUTPUT)
    require(builder.get("status") == "pass", "human-filled builder output must pass")
    require(builder.get("input_complete") is True, "human-filled builder input must be complete")
    require(
        builder.get("support_contact_available_for_review") is True,
        "support contact should be available for review",
    )
    require(builder.get("production_support_available") is False, "production support remains false")
    require(builder.get("blockers_closed_by_builder") == 0, "builder closes no blockers")
    require(support.get("production_support_available") is not True, "support output must not assert production support")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [REQUEST_REPORT, BOUNDARY_AUDIT, GATE]
    )
    for token in [
        "local_evidence_builder_executed_pending_closure_review",
        "request_approved: true",
        "evidence_builder_execution_authorized: true",
        "evidence_builder_executed: true",
        "production_ready: false",
        "customer_contacted: false",
        "blockers_closed_by_request: 0",
    ]:
        require(token in combined, "missing token " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_execution_request.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_execution_request.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_execution_request_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST_GATE.md",
        "/scripts/saee_support_contact_evidence_builder_execution_request.py",
        "/scripts/saee_support_contact_evidence_builder_execution_request_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("support_contact_evidence_builder_execution_request_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print("SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_EXECUTION_REQUEST_SMOKE: PASS")


if __name__ == "__main__":
    main()
