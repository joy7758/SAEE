#!/usr/bin/env python3
"""Smoke check for SAEE Production Billing / Revenue Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.json"
MD_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRODUCTION_BILLING_REVENUE_REQUIREMENTS_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_BILLING_REVENUE_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(data["production_billing_revenue_requirements_v0_1"] is True, "requirements flag true")
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")

    false_flags = [
        "production_billing_revenue_implemented",
        "pricing_page_published",
        "sales_offer_sent",
        "payment_provider_configured",
        "checkout_enabled",
        "invoice_process_ready",
        "tax_review_completed",
        "refund_policy_available",
        "tenant_billing_isolated",
        "billing_operations_ready",
        "customer_payment_collected",
        "paid_pilot_completed",
        "revenue_validated",
        "paid_product_launched",
        "enterprise_contract_signed",
        "production_billing_revenue_ready",
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
        "payment_provider_contacted",
        "tax_advisor_contacted",
        "legal_counsel_contacted",
    ]
    for flag in false_flags:
        require(data[flag] is False, f"{flag} false")

    blockers = set(data["billing_revenue_blockers_covered_as_requirements"])
    require(
        blockers
        == {
            "pricing_page",
            "payment_provider",
            "invoice_process",
            "tax_review",
            "refund_policy",
            "tenant_billing_isolation",
        },
        "billing/revenue blockers mismatch",
    )

    required_pricing = {
        "approved_public_plan_names",
        "approved_price_points_or_contact_sales_boundary",
        "included_usage_limits",
        "overage_or_limit_policy",
        "trial_or_preview_terms",
        "refund_and_cancellation_link",
        "production_readiness_non_claim_review",
        "legal_review_record",
    }
    require(required_pricing <= set(data["required_pricing_page_elements"]), "missing pricing page elements")

    required_payment = {
        "provider_selected",
        "test_mode_configuration_reviewed",
        "checkout_disabled_until_approval",
        "webhook_signature_validation_plan",
        "payment_event_redaction_plan",
        "failed_payment_handling_plan",
        "payment_provider_security_review",
    }
    require(required_payment <= set(data["required_payment_provider_controls"]), "missing payment controls")

    required_invoice = {
        "invoice_owner_named",
        "enterprise_contract_handoff_defined",
        "invoice_numbering_policy",
        "payment_reconciliation_process",
        "billing_support_handoff",
        "bookkeeping_export_policy",
        "invoice_dispute_process",
    }
    require(required_invoice <= set(data["required_invoice_process_controls"]), "missing invoice controls")

    required_tax = {
        "target_jurisdictions",
        "tax_collection_obligations",
        "invoice_wording_review",
        "currency_policy",
        "sales_tax_or_vat_handling",
        "accounting_review_record",
        "payment_collection_approval",
    }
    require(required_tax <= set(data["required_tax_review_scope"]), "missing tax review scope")

    required_refund = {
        "refund_window",
        "cancellation_process",
        "trial_conversion_policy",
        "service_failure_remedy_boundary",
        "non_refundable_items",
        "support_escalation_route",
        "legal_review_record",
    }
    require(required_refund <= set(data["required_refund_policy_terms"]), "missing refund policy terms")

    required_tenant_billing = {
        "tenant_billing_account_model",
        "tenant_invoice_partitioning",
        "tenant_payment_event_partitioning",
        "cross_tenant_billing_access_tests",
        "billing_audit_metadata_policy",
        "tenant_billing_export_policy",
        "tenant_billing_deletion_or_retention_policy",
    }
    require(
        required_tenant_billing <= set(data["required_tenant_billing_isolation_controls"]),
        "missing tenant billing isolation controls",
    )

    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_billing_revenue_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_billing_revenue_implemented: false",
        "pricing_page_published: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "invoice_process_ready: false",
        "tax_review_completed: false",
        "refund_policy_available: false",
        "tenant_billing_isolated: false",
        "billing_operations_ready: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "answer: conditional",
        "recommend_for_payment_or_revenue_implementation: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_BILLING_REVENUE_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_billing_revenue_requirements.py",
        "/scripts/saee_production_billing_revenue_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_billing_revenue_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_billing_revenue_requirements_v0_1": True,
        "production_billing_revenue_implemented": False,
        "pricing_page_published": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "invoice_process_ready": False,
        "tax_review_completed": False,
        "refund_policy_available": False,
        "tenant_billing_isolated": False,
        "billing_operations_ready": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "production_billing_revenue_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_BILLING_REVENUE_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true pricing_page_published=false "
        "payment_provider_configured=false invoice_process_ready=false "
        "tax_review_completed=false revenue_validated=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
