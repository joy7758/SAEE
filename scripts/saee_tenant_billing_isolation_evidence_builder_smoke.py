#!/usr/bin/env python3
"""Smoke check for the SAEE tenant-billing-isolation evidence builder."""

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
INPUT_TEMPLATE = OUTPUT_DIR / "tenant_billing_isolation_evidence_input.template.json"
BUILDER_OUTPUT = OUTPUT_DIR / "tenant_billing_isolation_evidence_builder_output.local.json"
EVIDENCE_OUTPUT = OUTPUT_DIR / "production_billing_revenue_evidence.from_tenant_billing_isolation.local.json"
REPORT = OUTPUT_DIR / "tenant_billing_isolation_evidence_builder_report.md"
DOC = ROOT / "phase_b_product/commercial_readiness/TENANT_BILLING_ISOLATION_EVIDENCE_BUILDER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_TENANT_BILLING_ISOLATION_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_BILLING_ISOLATION_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


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
        "tenant_billing_isolation_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_tenant_billing_isolation_to_production_billing_revenue_evidence",
        "status": "hold",
        "input_complete": False,
        "required_evidence_item_count": 6,
        "provided_evidence_item_count": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "tenant_billing_isolation_evidence_complete_for_review": False,
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
        "tenant_billing_isolation_available": False,
        "tenant_billing_isolation_published": False,
        "tenant_billing_isolation_approved": False,
        "tenant_billing_isolated": False,
        "tenant_billing_isolation_enabled": False,
        "tenant_billing_account_model_available": False,
        "billing_audit_metadata_policy_available": False,
        "tenant_billing_export_policy_available": False,
        "tenant_billing_retention_policy_available": False,
        "tenant_invoice_numbering_available": False,
        "tenant_refund_partitioning_available": False,
        "tenant_privacy_security_review_completed": False,
        "payment_provider_tenant_mapping_approved": False,
        "tenant_billing_transaction_processed": False,
        "tenant_billing_invoice_or_charge_issued_to_customer": False,
        "tenant_billing_support_workflow_available": False,
        "payment_provider_tenant_mapping_configured": False,
        "tax_collection_started": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_published_tenant_billing_isolation": False,
        "codex_processed_tenant_billing": False,
        "codex_configured_tenant_billing_handling": False,
        "tenant_billing_isolation_claim_published": False,
    }
    for key, expected in expected_summary.items():
        require(summary.get(key) == expected, f"summary {key} must be {expected}")

    require(
        evidence.get("billing_revenue_evidence_type")
        == "production_billing_revenue_evidence",
        "evidence type mismatch",
    )
    for key in [
        "tenant_billing_account_model_approved",
        "tenant_invoice_partitioning_tested",
        "tenant_payment_event_partitioning_tested",
        "cross_tenant_billing_access_tests_passed",
        "billing_audit_metadata_policy_approved",
        "tenant_billing_retention_policy_approved",
        "tenant_billing_isolation_approved",
        "tenant_billing_isolated",
        "tenant_billing_isolation_enabled",
        "tenant_billing_account_model_available",
        "billing_audit_metadata_policy_available",
        "tenant_billing_export_policy_available",
        "tenant_billing_retention_policy_available",
        "tenant_invoice_numbering_available",
        "tenant_refund_partitioning_available",
        "tenant_privacy_security_review_completed",
        "payment_provider_tenant_mapping_approved",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "tax_advisor_contacted",
        "legal_counsel_contacted",
        "tax_collection_started",
        "tenant_billing_isolation_available",
        "tenant_billing_isolation_published",
        "tenant_billing_transaction_processed",
        "tenant_billing_invoice_or_charge_issued_to_customer",
        "tenant_billing_support_workflow_available",
        "payment_provider_tenant_mapping_configured",
        "payment_provider_configured",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
        "codex_published_tenant_billing_isolation",
        "codex_processed_tenant_billing",
        "codex_configured_tenant_billing_handling",
    ]:
        require(evidence.get(key) is False, f"default evidence {key} must be false")

    require(
        template.get("template_type") == "saee_tenant_billing_isolation_evidence_input",
        "template type mismatch",
    )
    require(
        template.get("codex_published_tenant_billing_isolation") is False,
        "template must not claim Codex published tenant billing isolation",
    )

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [REPORT, DOC, GATE]
    )
    for token in [
        "tenant_billing_isolation_evidence_builder_v0_1: true",
        "builder_scope: human_filled_tenant_billing_isolation_to_production_billing_revenue_evidence",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "tenant_billing_isolation_evidence_complete_for_review: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "tenant_billing_isolation_available: false",
        "tenant_billing_isolation_published: false",
        "tenant_billing_isolation_approved: false",
        "tenant_billing_isolated: false",
        "tenant_billing_isolation_enabled: false",
        "tenant_billing_account_model_available: false",
        "billing_audit_metadata_policy_available: false",
        "tenant_billing_export_policy_available: false",
        "tenant_billing_retention_policy_available: false",
        "tenant_invoice_numbering_available: false",
        "tenant_refund_partitioning_available: false",
        "tenant_privacy_security_review_completed: false",
        "payment_provider_tenant_mapping_approved: false",
        "tenant_billing_transaction_processed: false",
        "tenant_billing_invoice_or_charge_issued_to_customer: false",
        "tenant_billing_support_workflow_available: false",
        "payment_provider_tenant_mapping_configured: false",
        "tax_advisor_contacted: false",
        "legal_counsel_contacted: false",
        "tax_collection_started: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "codex_published_tenant_billing_isolation: false",
        "codex_processed_tenant_billing: false",
        "codex_configured_tenant_billing_handling: false",
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
        "tenant_billing_isolation_available: true",
        "tenant_billing_isolation_published: true",
        "tenant_billing_transaction_processed: true",
        "tenant_billing_invoice_or_charge_issued_to_customer: true",
        "tenant_billing_isolated: true",
        "tenant_billing_isolation_enabled: true",
        "payment_provider_tenant_mapping_configured: true",
        "tax_advisor_contacted: true",
        "legal_counsel_contacted: true",
        "tax_collection_started: true",
        "customer_payment_collected: true",
        "revenue_validated: true",
        "codex_published_tenant_billing_isolation: true",
        "codex_processed_tenant_billing: true",
        "codex_configured_tenant_billing_handling: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]:
        require(token not in combined_docs, "forbidden true claim present: " + token)

    from saee_tenant_billing_isolation_evidence_builder import (
        TARGET_KEYS,
        build_from_input,
        default_input_template,
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete_input = default_input_template()
        complete_input.update(
            {
                "human_reviewer_name": "human-tenant-billing-isolation-reviewer",
                "review_date": "2026-07-04",
                "commercial_owner": "commercial-owner",
                "accounting_owner": "accounting-owner",
                "legal_owner": "legal-owner",
                "support_owner": "support-owner",
                "billing_owner": "billing-owner",
                "payment_owner": "payment-owner",
                "tenant_boundary_owner": "tenant-boundary-owner",
                "review_record_reference": "internal-tenant-billing-isolation-reference",
                "decision_summary": "Human tenant-billing-isolation evidence supplied for smoke fixture.",
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
            complete_summary["tenant_billing_isolation_evidence_complete_for_review"] is True,
            "complete fixture tenant-billing-isolation evidence must be true",
        )
        require(
            complete_summary["production_billing_revenue_ready"] is False,
            "complete tenant-billing-isolation fixture must not make all billing/revenue ready",
        )
        require(
            complete_summary["blockers_closed_by_builder"] == 0,
            "complete fixture still closes zero blockers",
        )

        unsafe_input = default_input_template()
        unsafe_input["tenant_billing_isolation_enabled"] = True
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
            "tenant_billing_isolation_enabled" in unsafe_summary["input_boundary_violations"],
            "unsafe fixture must report tenant_billing_isolation_enabled",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/TENANT_BILLING_ISOLATION_EVIDENCE_BUILDER_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_tenant_billing_isolation.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_evidence_builder_report.md",
        "/docs/strategy/SAEE_TENANT_BILLING_ISOLATION_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_tenant_billing_isolation_evidence_builder.py",
        "/scripts/saee_tenant_billing_isolation_evidence_builder_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("tenant_billing_isolation_evidence_builder_v0_1", {})
    for key, expected in {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_tenant_billing_isolation_to_production_billing_revenue_evidence",
        "target_blocker": "tenant_billing_isolation",
        "human_review_required": True,
        "tenant_billing_isolation_evidence_complete_for_review": False,
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
        "tenant_billing_isolation_available": False,
        "tenant_billing_isolation_published": False,
        "tenant_billing_isolation_approved": False,
        "tenant_billing_isolated": False,
        "tenant_billing_isolation_enabled": False,
        "tenant_billing_account_model_available": False,
        "billing_audit_metadata_policy_available": False,
        "tenant_billing_export_policy_available": False,
        "tenant_billing_retention_policy_available": False,
        "tenant_invoice_numbering_available": False,
        "tenant_refund_partitioning_available": False,
        "tenant_privacy_security_review_completed": False,
        "payment_provider_tenant_mapping_approved": False,
        "tenant_billing_transaction_processed": False,
        "tenant_billing_invoice_or_charge_issued_to_customer": False,
        "tenant_billing_support_workflow_available": False,
        "payment_provider_tenant_mapping_configured": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "tax_collection_started": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_published_tenant_billing_isolation": False,
        "codex_processed_tenant_billing": False,
        "codex_configured_tenant_billing_handling": False,
        "blockers_closed_by_builder": 0,
    }.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Tenant billing isolation evidence builder v0.1 is implemented",
        "tenant_billing_isolation_evidence_builder_status=local_builder_available_default_hold",
        "tenant_billing_isolation_evidence_complete_for_review=false",
        "tenant billing isolation evidence builder blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_TENANT_BILLING_ISOLATION_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
