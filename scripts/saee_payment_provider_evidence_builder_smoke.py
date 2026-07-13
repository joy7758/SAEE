#!/usr/bin/env python3
"""Smoke check for the SAEE payment-provider evidence builder."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
INPUT_TEMPLATE = OUTPUT_DIR / "payment_provider_evidence_input.template.json"
BUILDER_OUTPUT = OUTPUT_DIR / "payment_provider_evidence_builder_output.local.json"
EVIDENCE_OUTPUT = OUTPUT_DIR / "production_billing_revenue_evidence.from_payment_provider.local.json"
REPORT = OUTPUT_DIR / "payment_provider_evidence_builder_report.md"
DOC = ROOT / "phase_b_product/commercial_readiness/PAYMENT_PROVIDER_EVIDENCE_BUILDER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PAYMENT_PROVIDER_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PAYMENT_PROVIDER_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    require(INPUT_TEMPLATE.exists(), "input template missing")
    require(BUILDER_OUTPUT.exists(), "builder output missing")
    require(EVIDENCE_OUTPUT.exists(), "billing/revenue evidence output missing")
    require(REPORT.exists(), "builder report missing")
    require(DOC.exists(), "top doc missing")
    require(GATE.exists(), "recommendation gate missing")

    summary = read_json(BUILDER_OUTPUT)
    evidence = read_json(EVIDENCE_OUTPUT)
    template = read_json(INPUT_TEMPLATE)

    expected_summary = {
        "payment_provider_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_payment_provider_to_production_billing_revenue_evidence",
        "status": "hold",
        "input_complete": False,
        "required_evidence_item_count": 6,
        "provided_evidence_item_count": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "payment_provider_evidence_complete_for_review": False,
        "production_billing_revenue_ready": False,
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
        "payment_provider_contacted": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "payment_link_created": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_selected_payment_provider": False,
        "codex_contacted_payment_provider": False,
        "codex_configured_payment_provider": False,
        "codex_enabled_checkout": False,
        "codex_processed_payment": False,
        "payment_provider_claim_published": False,
    }
    for key, expected in expected_summary.items():
        require(summary.get(key) == expected, f"summary {key} must be {expected}")

    require(
        evidence.get("billing_revenue_evidence_type")
        == "production_billing_revenue_evidence",
        "evidence type mismatch",
    )
    for key in [
        "payment_provider_selected",
        "test_mode_configuration_reviewed",
        "checkout_enablement_approval_required",
        "webhook_signature_validation_tested",
        "payment_event_redaction_reviewed",
        "security_review_completed",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "payment_provider_contacted",
        "payment_provider_configured",
        "checkout_enabled",
        "payment_link_created",
        "customer_payment_collected",
        "revenue_validated",
    ]:
        require(evidence.get(key) is False, f"default evidence {key} must be false")

    require(
        template.get("template_type") == "saee_payment_provider_evidence_input",
        "template type mismatch",
    )
    require(
        template.get("codex_configured_payment_provider") is False,
        "template must not claim Codex configured payment provider",
    )

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [REPORT, DOC, GATE]
    )
    for token in [
        "payment_provider_evidence_builder_v0_1: true",
        "builder_scope: human_filled_payment_provider_to_production_billing_revenue_evidence",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "payment_provider_evidence_complete_for_review: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "payment_provider_contacted: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "codex_configured_payment_provider: false",
        "codex_enabled_checkout: false",
        "blockers_closed_by_builder: 0",
    ]:
        require(token in combined_docs, "missing doc token: " + token)
    for token in [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "payment_provider_configured: true",
        "checkout_enabled: true",
        "customer_payment_collected: true",
        "revenue_validated: true",
        "codex_configured_payment_provider: true",
        "codex_enabled_checkout: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]:
        require(token not in combined_docs, "forbidden true claim present: " + token)

    from saee_payment_provider_evidence_builder import (
        TARGET_KEYS,
        build_from_input,
        default_input_template,
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete_input = default_input_template()
        complete_input.update(
            {
                "human_reviewer_name": "human-payment-reviewer",
                "review_date": "2026-07-04",
                "commercial_owner": "commercial-owner",
                "payment_owner": "payment-owner",
                "security_owner": "security-owner",
                "review_record_reference": "internal-payment-provider-review-reference",
                "decision_summary": "Human payment-provider evidence supplied for smoke fixture.",
            }
        )
        complete_input["evidence_review"] = {key: True for key in TARGET_KEYS}
        complete_input["source_notes_by_key"] = {
            key: f"source note for {key}" for key in TARGET_KEYS
        }
        complete_input["review_artifacts"] = [
            {
                "evidence_key": key,
                "artifact_reference": f"artifact-{key}",
                "reviewed_by_human": True,
                "owner_named": True,
                "human_source_note": f"artifact note for {key}",
            }
            for key in TARGET_KEYS
        ]
        complete_path = tmp / "complete.json"
        complete_path.write_text(json.dumps(complete_input), encoding="utf-8")
        complete_summary = build_from_input(
            complete_path,
            tmp / "complete_output.json",
            tmp / "complete_evidence.json",
            write_documentation=False,
        )
        require(complete_summary["status"] == "pass", "complete fixture must pass")
        require(
            complete_summary["payment_provider_evidence_complete_for_review"] is True,
            "complete fixture payment-provider evidence must be true",
        )
        require(
            complete_summary["production_billing_revenue_ready"] is False,
            "complete payment-provider fixture must not make all billing/revenue ready",
        )
        require(
            complete_summary["blockers_closed_by_builder"] == 0,
            "complete fixture still closes zero blockers",
        )

        unsafe_input = default_input_template()
        unsafe_input["payment_provider_configured"] = True
        unsafe_path = tmp / "unsafe.json"
        unsafe_path.write_text(json.dumps(unsafe_input), encoding="utf-8")
        unsafe_summary = build_from_input(
            unsafe_path,
            tmp / "unsafe_output.json",
            tmp / "unsafe_evidence.json",
            write_documentation=False,
        )
        require(unsafe_summary["status"] == "stop", "unsafe fixture must stop")
        require(
            "payment_provider_configured" in unsafe_summary["input_boundary_violations"],
            "unsafe fixture must report payment_provider_configured",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PAYMENT_PROVIDER_EVIDENCE_BUILDER_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_payment_provider.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_evidence_builder_report.md",
        "/docs/strategy/SAEE_PAYMENT_PROVIDER_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_payment_provider_evidence_builder.py",
        "/scripts/saee_payment_provider_evidence_builder_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("payment_provider_evidence_builder_v0_1", {})
    for key, expected in {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_payment_provider_to_production_billing_revenue_evidence",
        "target_blocker": "payment_provider",
        "human_review_required": True,
        "payment_provider_evidence_complete_for_review": False,
        "production_billing_revenue_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "payment_provider_contacted": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_configured_payment_provider": False,
        "codex_enabled_checkout": False,
        "blockers_closed_by_builder": 0,
    }.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Payment provider evidence builder v0.1 is implemented",
        "payment_provider_evidence_builder_status=local_builder_available_default_hold",
        "payment_provider_evidence_complete_for_review=false",
        "payment provider evidence builder blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_PAYMENT_PROVIDER_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
