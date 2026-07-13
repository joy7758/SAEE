#!/usr/bin/env python3
"""Smoke check for the billing/revenue human-filled evidence run."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
SUMMARY_PATH = EVIDENCE_DIR / "billing_revenue_human_filled_evidence_run_summary.local.json"
PROFILE_PATH = (
    EVIDENCE_DIR
    / "billing_revenue_evidence_profile.from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json"
)
COMBINED_EVIDENCE_PATH = (
    EVIDENCE_DIR
    / "production_billing_revenue_evidence.combined_from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json"
)
DEFAULT_EVIDENCE_PATH = EVIDENCE_DIR / "billing_revenue_evidence.local.json"

FALSE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "customer_contacted",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
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
)

TARGET_BLOCKERS = [
    "pricing_page",
    "payment_provider",
    "invoice_process",
    "tax_review",
    "refund_policy",
    "tenant_billing_isolation",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_BILLING_REVENUE_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: FAIL "
            + message
        )


def read_json(path: Path) -> dict[str, object]:
    require(path.exists(), f"missing {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "SAEE_BILLING_REVENUE_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: FAIL "
            f"invalid JSON {path.relative_to(ROOT)}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must be object")
    return data


def main() -> None:
    summary = read_json(SUMMARY_PATH)
    profile = read_json(PROFILE_PATH)
    combined_evidence = read_json(COMBINED_EVIDENCE_PATH)
    default_evidence = read_json(DEFAULT_EVIDENCE_PATH)

    require(summary["run_status"] == "pass", "run_status must be pass")
    require(summary["validation_status"] == "pass", "validation_status must be pass")
    require(
        summary["billing_revenue_profile_status"] == "pass",
        "billing/revenue profile status must be pass",
    )
    require(
        summary["billing_revenue_readiness_status"] == "pass",
        "billing/revenue readiness status must be pass",
    )
    require(
        summary["production_billing_revenue_ready"] is True,
        "billing/revenue evidence must be ready for go/no-go review",
    )
    require(
        summary["billing_revenue_satisfied_blockers"] == TARGET_BLOCKERS,
        "billing/revenue satisfied blockers must match target blockers",
    )
    require(
        summary["billing_revenue_satisfied_blocker_count"] == 6,
        "six billing/revenue blockers must be satisfied for go/no-go input",
    )
    require(
        summary[
            "support_data_ops_operations_privacy_security_legal_billing_revenue_production_blocker_count"
        ]
        == 6,
        "combined blocker count must be 6 after billing/revenue evidence",
    )
    require(
        summary["commercial_status_after_profile"] == "hold",
        "commercial status must remain hold",
    )
    require(
        summary["production_launch_status_after_profile"] == "hold",
        "production launch status must remain hold",
    )
    default_ready = all(
        default_evidence.get(key) is True
        for key in (
            "human_approved_pricing_page_copy",
            "approved_plan_and_usage_terms",
            "legal_review_completed",
            "production_readiness_non_claim_reviewed",
            "pricing_page_publication_approval_recorded",
            "payment_provider_selected",
            "test_mode_configuration_reviewed",
            "checkout_enablement_approval_required",
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
        )
    )
    require(
        default_ready is False,
        "default billing/revenue evidence must remain unpromoted",
    )
    require(
        combined_evidence["source_boundary_violation_count"] == 0,
        "combined evidence must have no source boundary violations",
    )
    require(
        profile["source_boundary_violation_count"] == 0,
        "profile must have no source boundary violations",
    )

    for component in summary["components"]:
        require(component["validation_status"] == "pass", "component validation must pass")
        require(component["builder_status"] == "pass", "component builder must pass")
        require(
            component["builder_boundary_violation_count"] == 0,
            "component builder boundary violations must be zero",
        )

    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")
        require(profile.get(key) is False, f"profile {key} must be false")
        require(combined_evidence.get(key) is False, f"combined evidence {key} must be false")

    for path_text in summary["input_files"] + summary["output_files"]:
        path = Path(str(path_text))
        require(path.exists(), f"referenced evidence file missing: {path}")

    print(
        "SAEE_BILLING_REVENUE_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: PASS "
        "billing_revenue_profile_status=pass production_blockers=6 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
