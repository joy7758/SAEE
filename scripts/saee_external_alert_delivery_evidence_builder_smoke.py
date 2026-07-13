#!/usr/bin/env python3
"""Smoke check for the SAEE external-alert-delivery evidence builder."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    ON_CALL_KEYS,
    PRODUCTION_MONITORING_KEYS,
    evaluate_production_operations_evidence,
)
from scripts.saee_external_alert_delivery_evidence_builder import (
    DEFAULT_INPUT_PATH,
    DEFAULT_OPERATIONS_OUTPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    INPUT_FORBIDDEN_TRUE_KEYS,
    REPORT_PATH,
    build_from_input,
)


BUILDER_SCRIPT = ROOT / "scripts/saee_external_alert_delivery_evidence_builder.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_EXTERNAL_ALERT_DELIVERY_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    evidence_review = {key: True for key in EXTERNAL_ALERT_DELIVERY_KEYS}
    source_notes = {
        key: f"Human-reviewed external-alert-delivery source note for {key}."
        for key in EXTERNAL_ALERT_DELIVERY_KEYS
    }
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["production_ready"] = True
    return {
        "template_type": "saee_external_alert_delivery_evidence_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-04",
        "alert_delivery_owner": "Fixture Alert Delivery Owner",
        "operations_reviewer_name": "Fixture Operations Reviewer",
        "decision_summary": "Fixture-only alert delivery evidence for deterministic smoke validation.",
        "evidence_review": evidence_review,
        "source_notes_by_key": source_notes,
        "boundary_review": boundary_review,
        "alert_delivery_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://external-alert-delivery/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in EXTERNAL_ALERT_DELIVERY_KEYS
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


def operations_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_operations_evidence(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(BUILDER_SCRIPT.exists(), "builder script missing")

    default_run = subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    require(default_summary["status"] == "hold", "default builder status must hold")
    require(default_summary["input_complete"] is False, "default input must be incomplete")
    require(
        default_summary["external_alert_delivery_available_for_review"] is False,
        "default external alert delivery must not be available",
    )
    require(
        default_summary["production_operations_ready"] is False,
        "default production operations must be false",
    )
    require(default_summary["blockers_closed_by_builder"] == 0, "no default closure")
    require(DEFAULT_INPUT_PATH.exists(), "default input template missing")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    require(DEFAULT_OPERATIONS_OUTPUT_PATH.exists(), "default operations evidence missing")

    default_evidence = json.loads(DEFAULT_OPERATIONS_OUTPUT_PATH.read_text(encoding="utf-8"))
    for key in PRODUCTION_MONITORING_KEYS + EXTERNAL_ALERT_DELIVERY_KEYS + ON_CALL_KEYS:
        require(default_evidence.get(key) is False, f"default evidence {key} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_input_path = tmp / "complete_alert_delivery_input.json"
        complete_output_path = tmp / "complete_builder_output.json"
        complete_operations_path = tmp / "complete_operations_evidence.json"
        unsafe_input_path = tmp / "unsafe_alert_delivery_input.json"
        unsafe_output_path = tmp / "unsafe_builder_output.json"
        unsafe_operations_path = tmp / "unsafe_operations_evidence.json"

        write_json(complete_input_path, complete_input())
        write_json(unsafe_input_path, complete_input(unsafe=True))

        complete_summary = build_from_input(
            complete_input_path,
            complete_output_path,
            complete_operations_path,
            write_documentation=False,
        )
        unsafe_summary = build_from_input(
            unsafe_input_path,
            unsafe_output_path,
            unsafe_operations_path,
            write_documentation=False,
        )
        complete_readiness = operations_readiness(complete_operations_path)
        unsafe_readiness = operations_readiness(unsafe_operations_path)

    require(complete_summary["status"] == "pass", "complete fixture summary pass")
    require(complete_summary["input_complete"] is True, "complete fixture input complete")
    require(
        complete_summary["external_alert_delivery_available_for_review"] is True,
        "complete fixture production external alert delivery available",
    )
    require(
        complete_summary["production_operations_ready"] is False,
        "complete fixture still not production operations",
    )
    require(
        complete_readiness["external_alert_delivery_available"] is True,
        "complete readiness production external alert delivery available",
    )
    require(complete_readiness["status"] == "hold", "complete operations readiness still hold")
    require(
        complete_readiness["production_monitoring_available"] is False,
        "production monitoring false",
    )
    require(complete_readiness["on_call_rotation_available"] is False, "on-call false")
    require(
        complete_summary["blockers_closed_by_builder"] == 0,
        "complete fixture closes no blockers",
    )
    require(unsafe_summary["status"] == "stop", "unsafe fixture stops")
    require(unsafe_summary["input_boundary_violation_count"] > 0, "unsafe violations")
    require(
        unsafe_readiness["external_alert_delivery_available"] is False,
        "unsafe external alert delivery remains unavailable",
    )

    subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "external_alert_delivery_evidence_builder_v0_1: true",
        "builder_scope: human_filled_external_alert_delivery_to_production_operations_evidence",
        "required_evidence_item_count: 6",
        "blockers_closed_by_builder: 0",
        "production_operations_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/EXTERNAL_ALERT_DELIVERY_EVIDENCE_BUILDER_V0_1.md",
        "/docs/strategy/SAEE_EXTERNAL_ALERT_DELIVERY_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.from_external_alert_delivery.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_evidence_builder_report.md",
        "/scripts/saee_external_alert_delivery_evidence_builder.py",
        "/scripts/saee_external_alert_delivery_evidence_builder_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("external_alert_delivery_evidence_builder_v0_1", {})
    expected = {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_external_alert_delivery_to_production_operations_evidence",
        "external_alert_delivery_available_for_review": False,
        "production_operations_ready": False,
        "external_alert_delivery_available": False,
        "on_call_rotation_available": False,
        "blockers_closed_by_builder": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "external_alert_delivery_enabled": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_EXTERNAL_ALERT_DELIVERY_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_external_alert_delivery_available=true "
        "production_operations_ready=false blockers_closed_by_builder=0"
    )


if __name__ == "__main__":
    main()
