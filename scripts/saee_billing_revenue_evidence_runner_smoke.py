#!/usr/bin/env python3
"""Smoke check for the local billing/revenue evidence runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_billing_revenue_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_billing_revenue_evidence,
)
from scripts.saee_billing_revenue_evidence_runner import (
    OUTPUT_PATH,
    main as run_runner,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_BILLING_REVENUE_EVIDENCE_RUNNER_SMOKE: FAIL: " + message
        )


def main() -> None:
    run_runner()
    require(OUTPUT_PATH.exists(), "evidence file must exist")
    evidence = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    require(
        evidence.get("billing_revenue_evidence_type")
        == "production_billing_revenue_evidence",
        "wrong billing/revenue evidence type",
    )
    require(
        evidence.get("evidence_scope")
        == "local_public_shell_billing_revenue_review_packet",
        "wrong evidence scope",
    )
    for flag in [
        "production_readiness_non_claim_reviewed",
        "checkout_enablement_approval_required",
    ]:
        require(evidence.get(flag) is True, f"{flag} must be recorded")
    for flag in [
        "human_approved_pricing_page_copy",
        "approved_plan_and_usage_terms",
        "legal_review_completed",
        "pricing_page_publication_approval_recorded",
        "payment_provider_selected",
        "test_mode_configuration_reviewed",
        "webhook_signature_validation_tested",
        "payment_event_redaction_reviewed",
        "security_review_completed",
        "invoice_owner_named",
        "invoice_workflow_approved",
        "contract_handoff_defined",
        "payment_reconciliation_tested",
        "billing_support_handoff_defined",
        "bookkeeping_review_completed",
        "target_jurisdictions_reviewed",
        "tax_obligations_reviewed",
        "invoice_wording_approved",
        "currency_policy_approved",
        "tax_collection_approval_recorded",
        "refund_policy_approved",
        "cancellation_process_approved",
        "trial_conversion_policy_approved",
        "service_failure_remedy_boundary_approved",
        "support_escalation_route_defined",
        "tenant_billing_account_model_approved",
        "tenant_invoice_partitioning_tested",
        "tenant_payment_event_partitioning_tested",
        "cross_tenant_billing_access_tests_passed",
        "billing_audit_metadata_policy_approved",
        "tenant_billing_retention_policy_approved",
    ]:
        require(evidence.get(flag) is False, f"{flag} must remain false")

    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if evidence.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))

    readiness = evaluate_production_billing_revenue_evidence(
        load_settings(
            {"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(OUTPUT_PATH)}
        )
    )
    require(readiness["status"] == "hold", "partial local evidence must remain hold")
    for flag in [
        "pricing_page_evidence_complete",
        "payment_provider_evidence_complete",
        "invoice_process_evidence_complete",
        "tax_review_evidence_complete",
        "refund_policy_evidence_complete",
        "tenant_billing_isolation_evidence_complete",
        "production_billing_revenue_ready",
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
        "payment_provider_contacted",
        "tax_advisor_contacted",
        "legal_counsel_contacted",
        "pricing_page_published",
        "sales_offer_sent",
        "paid_product_launched",
        "enterprise_contract_signed",
        "payment_provider_configured",
        "checkout_enabled",
        "payment_provider_live_mode_enabled",
        "payment_link_created",
        "invoice_sent_to_customer",
        "tax_collection_started",
        "refund_policy_published",
        "production_billing_enabled",
        "customer_payment_collected",
        "paid_pilot_completed",
        "revenue_validated",
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_RUNNER_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_BILLING_REVENUE_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = doc + "\n" + gate
    for token in [
        "billing_revenue_evidence_runner_v0_1: true",
        "evidence_scope: local_public_shell_billing_revenue_review_packet",
        "pricing_page_evidence_complete: false",
        "payment_provider_evidence_complete: false",
        "invoice_process_evidence_complete: false",
        "tax_review_evidence_complete: false",
        "refund_policy_evidence_complete: false",
        "tenant_billing_isolation_evidence_complete: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_RUNNER_V0_1.md",
        "/docs/strategy/SAEE_BILLING_REVENUE_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/README.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json",
        "/scripts/saee_billing_revenue_evidence_runner.py",
        "/scripts/saee_billing_revenue_evidence_runner_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("billing_revenue_evidence_runner_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_generated_hold",
        "billing_revenue_evidence_runner_v0_1": True,
        "evidence_scope": "local_public_shell_billing_revenue_review_packet",
        "pricing_packaging_plan_available": True,
        "internal_price_bands_available": True,
        "billing_policy_draft_available": True,
        "production_readiness_non_claim_reviewed": True,
        "checkout_enablement_approval_required": True,
        "pricing_page_evidence_complete": False,
        "payment_provider_evidence_complete": False,
        "invoice_process_evidence_complete": False,
        "tax_review_evidence_complete": False,
        "refund_policy_evidence_complete": False,
        "tenant_billing_isolation_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "invoice_process_ready": False,
        "tax_review_completed": False,
        "refund_policy_available": False,
        "tenant_billing_isolated": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
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
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "blockers_closed_by_default": 0,
    }
    for flag, expected_value in expected.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index {flag} must be {expected_value}",
        )

    print(
        "SAEE_BILLING_REVENUE_EVIDENCE_RUNNER_SMOKE: PASS "
        "local_public_shell_evidence=true "
        "production_billing_revenue_ready=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
