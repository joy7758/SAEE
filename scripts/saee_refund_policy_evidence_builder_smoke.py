#!/usr/bin/env python3
"""Smoke check for the SAEE refund-policy evidence builder."""

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
INPUT_TEMPLATE = OUTPUT_DIR / "refund_policy_evidence_input.template.json"
BUILDER_OUTPUT = OUTPUT_DIR / "refund_policy_evidence_builder_output.local.json"
EVIDENCE_OUTPUT = OUTPUT_DIR / "production_billing_revenue_evidence.from_refund_policy.local.json"
REPORT = OUTPUT_DIR / "refund_policy_evidence_builder_report.md"
DOC = ROOT / "phase_b_product/commercial_readiness/REFUND_POLICY_EVIDENCE_BUILDER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_REFUND_POLICY_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_REFUND_POLICY_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


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
        "refund_policy_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_refund_policy_to_production_billing_revenue_evidence",
        "status": "hold",
        "input_complete": False,
        "required_evidence_item_count": 5,
        "provided_evidence_item_count": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "refund_policy_evidence_complete_for_review": False,
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
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "refund_policy_available": False,
        "refund_policy_published": False,
        "refund_processed": False,
        "refund_issued_to_customer": False,
        "cancellation_process_available": False,
        "trial_conversion_policy_available": False,
        "service_failure_remedy_available": False,
        "refund_request_workflow_available": False,
        "payment_provider_refund_configured": False,
        "tax_collection_started": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_published_refund_policy": False,
        "codex_processed_refund": False,
        "codex_configured_refund_handling": False,
        "refund_policy_claim_published": False,
    }
    for key, expected in expected_summary.items():
        require(summary.get(key) == expected, f"summary {key} must be {expected}")

    require(
        evidence.get("billing_revenue_evidence_type")
        == "production_billing_revenue_evidence",
        "evidence type mismatch",
    )
    for key in [
        "refund_policy_approved",
        "cancellation_process_approved",
        "trial_conversion_policy_approved",
        "service_failure_remedy_boundary_approved",
        "support_escalation_route_defined",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "tax_advisor_contacted",
        "legal_counsel_contacted",
        "tax_collection_started",
        "refund_policy_available",
        "refund_policy_published",
        "refund_processed",
        "refund_issued_to_customer",
        "cancellation_process_available",
        "trial_conversion_policy_available",
        "service_failure_remedy_available",
        "refund_request_workflow_available",
        "payment_provider_refund_configured",
        "payment_provider_configured",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
        "codex_published_refund_policy",
        "codex_processed_refund",
        "codex_configured_refund_handling",
    ]:
        require(evidence.get(key) is False, f"default evidence {key} must be false")

    require(
        template.get("template_type") == "saee_refund_policy_evidence_input",
        "template type mismatch",
    )
    require(
        template.get("codex_published_refund_policy") is False,
        "template must not claim Codex published refund policy",
    )

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [REPORT, DOC, GATE]
    )
    for token in [
        "refund_policy_evidence_builder_v0_1: true",
        "builder_scope: human_filled_refund_policy_to_production_billing_revenue_evidence",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "refund_policy_evidence_complete_for_review: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "refund_policy_available: false",
        "refund_policy_published: false",
        "refund_processed: false",
        "refund_issued_to_customer: false",
        "cancellation_process_available: false",
        "trial_conversion_policy_available: false",
        "service_failure_remedy_available: false",
        "refund_request_workflow_available: false",
        "payment_provider_refund_configured: false",
        "tax_advisor_contacted: false",
        "legal_counsel_contacted: false",
        "tax_collection_started: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "codex_published_refund_policy: false",
        "codex_processed_refund: false",
        "codex_configured_refund_handling: false",
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
        "refund_policy_available: true",
        "refund_policy_published: true",
        "refund_processed: true",
        "refund_issued_to_customer: true",
        "payment_provider_refund_configured: true",
        "tax_advisor_contacted: true",
        "legal_counsel_contacted: true",
        "tax_collection_started: true",
        "customer_payment_collected: true",
        "revenue_validated: true",
        "codex_published_refund_policy: true",
        "codex_processed_refund: true",
        "codex_configured_refund_handling: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]:
        require(token not in combined_docs, "forbidden true claim present: " + token)

    from saee_refund_policy_evidence_builder import (
        TARGET_KEYS,
        build_from_input,
        default_input_template,
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete_input = default_input_template()
        complete_input.update(
            {
                "human_reviewer_name": "human-refund-policy-reviewer",
                "review_date": "2026-07-04",
                "commercial_owner": "commercial-owner",
                "accounting_owner": "accounting-owner",
                "legal_owner": "legal-owner",
                "support_owner": "support-owner",
                "billing_owner": "billing-owner",
                "payment_owner": "payment-owner",
                "tenant_boundary_owner": "tenant-boundary-owner",
                "review_record_reference": "internal-refund-policy-reference",
                "decision_summary": "Human refund-policy evidence supplied for smoke fixture.",
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
            complete_summary["refund_policy_evidence_complete_for_review"] is True,
            "complete fixture refund-policy evidence must be true",
        )
        require(
            complete_summary["production_billing_revenue_ready"] is False,
            "complete refund-policy fixture must not make all billing/revenue ready",
        )
        require(
            complete_summary["blockers_closed_by_builder"] == 0,
            "complete fixture still closes zero blockers",
        )

        unsafe_input = default_input_template()
        unsafe_input["refund_processed"] = True
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
            "refund_processed" in unsafe_summary["input_boundary_violations"],
            "unsafe fixture must report refund_processed",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/REFUND_POLICY_EVIDENCE_BUILDER_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_refund_policy.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_evidence_builder_report.md",
        "/docs/strategy/SAEE_REFUND_POLICY_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_refund_policy_evidence_builder.py",
        "/scripts/saee_refund_policy_evidence_builder_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("refund_policy_evidence_builder_v0_1", {})
    for key, expected in {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_refund_policy_to_production_billing_revenue_evidence",
        "target_blocker": "refund_policy",
        "human_review_required": True,
        "refund_policy_evidence_complete_for_review": False,
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
        "refund_policy_available": False,
        "refund_policy_published": False,
        "refund_processed": False,
        "refund_issued_to_customer": False,
        "cancellation_process_available": False,
        "trial_conversion_policy_available": False,
        "service_failure_remedy_available": False,
        "refund_request_workflow_available": False,
        "payment_provider_refund_configured": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "tax_collection_started": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_published_refund_policy": False,
        "codex_processed_refund": False,
        "codex_configured_refund_handling": False,
        "blockers_closed_by_builder": 0,
    }.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Refund policy evidence builder v0.1 is implemented",
        "refund_policy_evidence_builder_status=local_builder_available_default_hold",
        "refund_policy_evidence_complete_for_review=false",
        "refund policy evidence builder blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_REFUND_POLICY_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
