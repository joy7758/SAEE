#!/usr/bin/env python3
"""Smoke check for the support contact approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.production_support_evidence import SUPPORT_CONTACT_KEYS
from scripts.saee_support_contact_evidence_builder import INPUT_FORBIDDEN_TRUE_KEYS
from scripts.saee_support_contact_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_validation,
)


VALIDATOR_SCRIPT = ROOT / "scripts/saee_support_contact_approval_input_validator.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: " + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["production_ready"] = True
    return {
        "template_type": "saee_support_contact_decision_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_validator_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-05",
        "selected_support_contact_channel": "support-fixture@example.invalid",
        "decision_summary": "Fixture-only support contact validator smoke input.",
        "evidence_review": {key: True for key in SUPPORT_CONTACT_KEYS},
        "source_notes_by_key": {
            key: f"Fixture source note for {key}." for key in SUPPORT_CONTACT_KEYS
        },
        "boundary_review": boundary_review,
        "candidate_contact_slots": [
            {
                "slot_id": "support_contact_candidate_a",
                "contact_channel": "support-fixture@example.invalid",
                "display_value_redacted": "support-fixture@example.invalid",
                "owner_named": True,
                "abuse_handling_reviewed": True,
                "customer_notice_route_reviewed": True,
                "test_plan_reviewed": True,
                "human_source_note": "Fixture-only human source note.",
            }
        ],
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "support_contact_available": False,
        "support_contact_configured": False,
        "customer_facing_support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "customer_support_available": False,
        "production_support_available": False,
        "support_process_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "codex_published_support_contact": False,
        "codex_sent_support_contact_test": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "blockers_closed_by_builder": False,
        "blockers_closed_by_packet": False,
        "execution_authorized": False,
        "development_permission_granted": False,
        "task_candidates_executed": False,
    }


def main() -> None:
    require(VALIDATOR_SCRIPT.exists(), "validator script missing")
    with tempfile.TemporaryDirectory() as tmpdir:
        default_output = Path(tmpdir) / "default_support_contact_validation.json"
        default_run = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_SCRIPT),
                "--json",
                "--no-docs",
                "--output",
                str(default_output),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    default_summary = json.loads(default_run.stdout)
    expected_default = {
        "validator_type": "saee_support_contact_approval_input_validator",
        "validation_status": "pass",
        "input_complete": True,
        "builder_ready": True,
        "target_blocker_id": "support_contact",
        "blockers_closed_by_validator": 0,
        "support_contact_approved_by_validator": False,
        "support_contact_available_by_validator": False,
        "support_contact_configured_by_validator": False,
        "support_contact_published_by_validator": False,
        "support_contact_tested_by_validator": False,
        "production_support_available_by_validator": False,
        "customer_support_available_by_validator": False,
        "sla_available_by_validator": False,
        "on_call_rotation_available_by_validator": False,
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
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
    }
    for key, value in expected_default.items():
        require(default_summary.get(key) == value, f"default {key} must be {value}")
    require(default_summary["missing_evidence_review"] == [], "default evidence review complete")
    require(
        default_summary["missing_contact_slot_requirements"] == [],
        "default contact slot requirements complete",
    )
    require(DEFAULT_OUTPUT_PATH.exists(), "default validation output missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_path = tmp / "complete_input.json"
        unsafe_path = tmp / "unsafe_input.json"
        write_json(complete_path, complete_input())
        write_json(unsafe_path, complete_input(unsafe=True))
        complete_summary = build_validation(complete_path)
        unsafe_summary = build_validation(unsafe_path)

    require(complete_summary["validation_status"] == "pass", "complete input must pass")
    require(complete_summary["input_complete"] is True, "complete input complete")
    require(complete_summary["builder_ready"] is True, "complete input builder ready")
    require(
        complete_summary["blockers_closed_by_validator"] == 0,
        "complete input closes no blockers",
    )
    require(complete_summary["support_contact_available_by_validator"] is False, "validator does not publish")
    require(unsafe_summary["validation_status"] == "stop", "unsafe input stops")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe violations")
    require(unsafe_summary["builder_ready"] is False, "unsafe input not builder ready")

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "support_contact_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_support_contact_input_pre_builder_check",
        "target_blocker_id: support_contact",
        "required_support_contact_evidence_item_count: 5",
        "blockers_closed_by_validator: 0",
        "support_contact_approved_by_validator: false",
        "support_contact_available_by_validator: false",
        "support_contact_configured_by_validator: false",
        "support_contact_published_by_validator: false",
        "support_contact_tested_by_validator: false",
        "production_support_available_by_validator: false",
        "customer_support_available_by_validator: false",
        "sla_available_by_validator: false",
        "on_call_rotation_available_by_validator: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_support_contact_approval: false",
        "recommend_for_support_contact_publication: false",
        "recommend_for_support_contact_configuration: false",
        "recommend_for_support_contact_test: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_customer_support_claim: false",
        "recommend_for_sla_claim: false",
        "recommend_for_on_call_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.template.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_validation.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_support_contact_approval_input_validator.py",
        "/scripts/saee_support_contact_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("support_contact_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "pass",
        "validator_type": "saee_support_contact_approval_input_validator",
        "target_blocker_id": "support_contact",
        "builder_ready": True,
        "input_complete": True,
        "metadata_complete": True,
        "evidence_review_complete": True,
        "source_notes_complete": True,
        "contact_slots_complete": True,
        "completed_contact_slot_count": 1,
        "blockers_closed_by_validator": 0,
        "support_contact_approved_by_validator": False,
        "support_contact_available_by_validator": False,
        "support_contact_configured_by_validator": False,
        "support_contact_published_by_validator": False,
        "support_contact_tested_by_validator": False,
        "production_support_available_by_validator": False,
        "customer_support_available_by_validator": False,
        "sla_available_by_validator": False,
        "on_call_rotation_available_by_validator": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=pass builder_ready=true blockers_closed_by_validator=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
