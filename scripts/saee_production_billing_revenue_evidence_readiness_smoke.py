#!/usr/bin/env python3
"""Smoke check for SAEE Production Billing/Revenue Evidence Readiness v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_billing_revenue_evidence import (
    evaluate_production_billing_revenue_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_SMOKE: FAIL: " + message
        )


def write_billing_revenue_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "billing_revenue_evidence_type": "production_billing_revenue_evidence",
        "human_approved_pricing_page_copy": True,
        "approved_plan_and_usage_terms": True,
        "legal_review_completed": True,
        "production_readiness_non_claim_reviewed": True,
        "pricing_page_publication_approval_recorded": True,
        "payment_provider_selected": True,
        "test_mode_configuration_reviewed": True,
        "checkout_enablement_approval_required": True,
        "webhook_signature_validation_tested": True,
        "payment_event_redaction_reviewed": True,
        "security_review_completed": True,
        "invoice_owner_named": True,
        "invoice_workflow_approved": True,
        "contract_handoff_defined": True,
        "payment_reconciliation_tested": True,
        "billing_support_handoff_defined": True,
        "bookkeeping_review_completed": True,
        "target_jurisdictions_reviewed": True,
        "tax_obligations_reviewed": True,
        "invoice_wording_approved": True,
        "currency_policy_approved": True,
        "tax_collection_approval_recorded": True,
        "refund_policy_approved": True,
        "cancellation_process_approved": True,
        "trial_conversion_policy_approved": True,
        "service_failure_remedy_boundary_approved": True,
        "support_escalation_route_defined": True,
        "tenant_billing_account_model_approved": True,
        "tenant_invoice_partitioning_tested": True,
        "tenant_payment_event_partitioning_tested": True,
        "cross_tenant_billing_access_tests_passed": True,
        "billing_audit_metadata_policy_approved": True,
        "tenant_billing_retention_policy_approved": True,
        "production_ready": unsafe,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
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
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "payment_provider_live_mode_enabled": False,
        "payment_link_created": False,
        "invoice_sent_to_customer": False,
        "tax_collection_started": False,
        "refund_policy_published": False,
        "production_billing_enabled": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_billing_revenue_evidence(load_settings({}))
    require(
        local["production_billing_revenue_evidence_type"]
        == "production_billing_revenue_evidence_readiness",
        "wrong evidence type",
    )
    require(
        local["production_billing_revenue_evidence_readiness_v0_1"] is True,
        "readiness flag",
    )
    require(local["status"] == "hold", "default evidence status must hold")
    require(
        local["billing_revenue_evidence_path_configured"] is False,
        "default path false",
    )
    for field in [
        "pricing_page_evidence_complete",
        "payment_provider_evidence_complete",
        "invoice_process_evidence_complete",
        "tax_review_evidence_complete",
        "refund_policy_evidence_complete",
        "tenant_billing_isolation_evidence_complete",
        "production_billing_revenue_ready",
    ]:
        require(local[field] is False, f"default {field} false")
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
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
        require(local[flag] is False, f"default {flag} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "BILLING_REVENUE_EVIDENCE.json"
        write_billing_revenue_evidence(evidence_path)
        settings = load_settings(
            {"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(evidence_path)}
        )
        configured = evaluate_production_billing_revenue_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_BILLING_REVENUE_EVIDENCE.json"
        write_billing_revenue_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_billing_revenue_evidence(
            load_settings(
                {"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(unsafe_path)}
            )
        )

    require(configured["status"] == "pass", "complete evidence should pass")
    for field in [
        "pricing_page_evidence_complete",
        "payment_provider_evidence_complete",
        "invoice_process_evidence_complete",
        "tax_review_evidence_complete",
        "refund_policy_evidence_complete",
        "tenant_billing_isolation_evidence_complete",
        "production_billing_revenue_ready",
    ]:
        require(configured[field] is True, f"configured {field} true")
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
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
        require(configured[flag] is False, f"configured {flag} false")

    blocked = blocker_ids(go_no_go)
    for blocker in [
        "pricing_page",
        "payment_provider",
        "invoice_process",
        "tax_review",
        "refund_policy",
        "tenant_billing_isolation",
    ]:
        require(blocker not in blocked, f"{blocker} should be satisfied by evidence")
    require(
        go_no_go["production_billing_revenue_evidence_status"] == "pass",
        "go/no-go should expose billing/revenue evidence pass",
    )
    for field in [
        "billing_revenue_evidence_pricing_page_complete",
        "billing_revenue_evidence_payment_provider_complete",
        "billing_revenue_evidence_invoice_process_complete",
        "billing_revenue_evidence_tax_review_complete",
        "billing_revenue_evidence_refund_policy_complete",
        "billing_revenue_evidence_tenant_billing_isolation_complete",
    ]:
        require(go_no_go[field] is True, f"go/no-go {field} true")
    require(go_no_go["commercial_status"] == "hold", "evidence alone must not launch")
    require(
        go_no_go["production_launch_status"] == "hold",
        "production launch must still hold",
    )
    require(go_no_go["production_ready"] is False, "go/no-go production false")
    require(go_no_go["customer_validated"] is False, "go/no-go customer false")
    require(go_no_go["product_launched"] is False, "go/no-go launch false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go private core false")

    require(unsafe["status"] == "stop", "unsafe evidence must stop")
    require(
        "production_ready" in unsafe["boundary_violations"],
        "unsafe evidence must detect boundary",
    )
    require(unsafe["production_ready"] is False, "unsafe output production false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join([doc, gate])
    for token in [
        "production_billing_revenue_evidence_readiness_v0_1: true",
        "default_status: hold",
        "billing_revenue_evidence_path_configured_default: false",
        "pricing_page_evidence_complete_default: false",
        "payment_provider_evidence_complete_default: false",
        "invoice_process_evidence_complete_default: false",
        "tax_review_evidence_complete_default: false",
        "refund_policy_evidence_complete_default: false",
        "tenant_billing_isolation_evidence_complete_default: false",
        "production_billing_revenue_ready_default: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "payment_provider_contacted: false",
        "tax_advisor_contacted: false",
        "legal_counsel_contacted: false",
        "pricing_page_published: false",
        "sales_offer_sent: false",
        "paid_product_launched: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "answer: conditional",
        "recommend_for_billing_revenue_evidence_review: true",
        "recommend_for_payment_or_checkout_implementation: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_billing_revenue_evidence.py",
        "/scripts/saee_production_billing_revenue_evidence_readiness.py",
        "/scripts/saee_production_billing_revenue_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_billing_revenue_evidence_readiness_v0_1", {})
    expected = {
        "status": "production_billing_revenue_evidence_readiness_hold",
        "production_billing_revenue_evidence_readiness_v0_1": True,
        "billing_revenue_evidence_path_configured_default": False,
        "pricing_page_evidence_complete_default": False,
        "payment_provider_evidence_complete_default": False,
        "invoice_process_evidence_complete_default": False,
        "tax_review_evidence_complete_default": False,
        "refund_policy_evidence_complete_default": False,
        "tenant_billing_isolation_evidence_complete_default": False,
        "production_billing_revenue_ready_default": False,
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
        "customer_contacted": False,
        "payment_provider_contacted": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "paid_product_launched": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
    }
    for key, expected_value in expected.items():
        require(
            entry.get(key) == expected_value,
            f"agent-index {key} must be {expected_value}",
        )

    print(
        "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "billing_blockers_satisfied_by_evidence=true production_launch_status=hold "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
