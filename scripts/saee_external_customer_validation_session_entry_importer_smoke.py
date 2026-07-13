#!/usr/bin/env python3
"""Smoke test the external customer-validation session entry importer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
ENTRY_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
IMPORT_SUMMARY = EVIDENCE_DIR / "external_customer_validation_session_entry_import_summary.local.json"
IMPORT_REPORT = EVIDENCE_DIR / "external_customer_validation_session_entry_import_report.md"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_session_entry_import_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORT_GATE.md"
RUNNER = ROOT / "scripts/saee_external_customer_validation_session_entry_importer.py"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORTER_SMOKE: FAIL "
        + message
    )


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
    for path in [ENTRY_TEMPLATE, IMPORT_SUMMARY, IMPORT_REPORT, BOUNDARY_AUDIT, GATE, RUNNER]:
        require(path.is_file(), f"missing required file {path.relative_to(ROOT)}")

    template = read_json(ENTRY_TEMPLATE)
    summary = read_json(IMPORT_SUMMARY)
    require(
        template.get("external_customer_validation_session_entry_template_v0_1") is True,
        "entry template flag must be true",
    )
    require(template.get("human_entry_confirmed") is False, "blank template must not be confirmed")
    review = template.get("evidence_review", {})
    require(isinstance(review, dict), "template evidence_review must be object")
    require(len(review) == 25, "template evidence_review must contain 25 keys")
    require(all(value is False for value in review.values()), "template review keys must start false")

    expected = {
        "external_customer_validation_session_entry_importer_v0_1": True,
        "status": "hold_human_session_entry_required",
        "importer_type": "manual_external_customer_validation_session_entry_importer",
        "entry_input_exists": False,
        "apply_requested": False,
        "human_filled_output_written": False,
        "ready_for_existing_customer_validation_validator": False,
        "human_entry_template_ready": True,
        "human_action_required": True,
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        "session_complete": False,
        "evidence_review_complete": False,
        "missing_evidence_review_count": 25,
        "boundary_violation_count": 0,
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
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
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_importer": 0,
    }
    for key, value in expected.items():
        require(summary.get(key) == value, f"{key} must be {value}")

    combined = (
        IMPORT_REPORT.read_text(encoding="utf-8")
        + "\n"
        + BOUNDARY_AUDIT.read_text(encoding="utf-8")
        + "\n"
        + GATE.read_text(encoding="utf-8")
    )
    for token in [
        "external_customer_validation_session_entry_importer_v0_1: true",
        "status: hold_human_session_entry_required",
        "human_filled_output_written: false",
        "ready_for_existing_customer_validation_validator: false",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_importer: 0",
        "answer: hold_human_session_entry_required",
    ]:
        require(token in combined, "missing report/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.template.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_import_summary.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_import_report.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_import_boundary_audit.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORT_GATE.md",
        "/scripts/saee_external_customer_validation_session_entry_importer.py",
        "/scripts/saee_external_customer_validation_session_entry_importer_smoke.py",
    ]:
        require(token in llms, "llms.txt missing token: " + token)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "external-customer-validation-session-entry-importer-smoke:",
        "check-external-customer-validation-session-entry-importer:",
        "scripts/saee_external_customer_validation_session_entry_importer_smoke.py",
    ]:
        require(token in makefile, "Makefile missing token: " + token)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("external_customer_validation_session_entry_importer_v0_1", {})
    require(isinstance(entry, dict), "agent-index entry must be object")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORTER_SMOKE: PASS "
        "status=hold_human_session_entry_required customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
