#!/usr/bin/env python3
"""Smoke check for the external alert delivery approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.production_operations_evidence import EXTERNAL_ALERT_DELIVERY_KEYS
from scripts.saee_external_alert_delivery_evidence_builder import INPUT_FORBIDDEN_TRUE_KEYS
from scripts.saee_external_alert_delivery_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_validation,
)


VALIDATOR_SCRIPT = ROOT / "scripts/saee_external_alert_delivery_approval_input_validator.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: "
            + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["external_alert_delivery_enabled"] = True
    return {
        "template_type": "saee_external_alert_delivery_evidence_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_validator_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-06",
        "alert_delivery_owner": "Fixture Alert Delivery Owner",
        "operations_reviewer_name": "Fixture Operations Reviewer",
        "decision_summary": "Fixture-only validator smoke input.",
        "evidence_review": {key: True for key in EXTERNAL_ALERT_DELIVERY_KEYS},
        "source_notes_by_key": {
            key: f"Fixture source note for {key}." for key in EXTERNAL_ALERT_DELIVERY_KEYS
        },
        "alert_delivery_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://external-alert-delivery/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture human source note for {key}.",
            }
            for key in EXTERNAL_ALERT_DELIVERY_KEYS
        ],
        "boundary_review": boundary_review,
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
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "external_alert_delivery_enabled": False,
        "external_alert_channel_configured_by_codex": False,
        "alert_routing_policy_published_by_codex": False,
        "alert_delivery_test_performed_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "external_alert_delivery_enabled_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_alert_delivery_claim_published": False,
    }


def main() -> None:
    require(VALIDATOR_SCRIPT.exists(), "validator script missing")
    default_run = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    expected_default = {
        "validator_type": "saee_external_alert_delivery_approval_input_validator",
        "validation_status": "hold",
        "input_complete": False,
        "builder_ready": False,
        "target_blocker_id": "external_alert_delivery",
        "blockers_closed_by_validator": 0,
        "external_alert_delivery_approved_by_validator": False,
        "external_alert_delivery_enabled_by_validator": False,
        "alert_channel_configured_by_validator": False,
        "alert_routing_policy_published_by_validator": False,
        "alert_delivery_test_performed_by_validator": False,
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
    require(default_summary["missing_alert_delivery_slots"], "default input must miss slots")
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
    require(unsafe_summary["validation_status"] == "stop", "unsafe input stops")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe violations")
    require(unsafe_summary["builder_ready"] is False, "unsafe input not builder ready")

    subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "external_alert_delivery_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_external_alert_delivery_input_pre_builder_check",
        "target_blocker_id: external_alert_delivery",
        "required_alert_delivery_evidence_item_count: 6",
        "blockers_closed_by_validator: 0",
        "external_alert_delivery_approved_by_validator: false",
        "external_alert_delivery_enabled_by_validator: false",
        "alert_channel_configured_by_validator: false",
        "alert_routing_policy_published_by_validator: false",
        "alert_delivery_test_performed_by_validator: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_external_alert_delivery_approval: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_alert_channel_configuration: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_validation.md",
        "/docs/strategy/SAEE_EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_external_alert_delivery_approval_input_validator.py",
        "/scripts/saee_external_alert_delivery_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("external_alert_delivery_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "hold",
        "validator_type": "saee_external_alert_delivery_approval_input_validator",
        "target_blocker_id": "external_alert_delivery",
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "external_alert_delivery_approved_by_validator": False,
        "external_alert_delivery_enabled_by_validator": False,
        "alert_channel_configured_by_validator": False,
        "alert_routing_policy_published_by_validator": False,
        "alert_delivery_test_performed_by_validator": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=hold builder_ready=false blockers_closed_by_validator=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
