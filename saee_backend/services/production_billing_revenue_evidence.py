"""Production billing/revenue evidence readiness checks.

This module validates a local evidence JSON file for future production
billing and revenue review. It does not publish pricing, configure payment
providers, enable checkout, create invoices, contact tax/legal/payment vendors,
collect payment, launch product, change API schema, modify runtime behavior, or
inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionBillingRevenueEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionBillingRevenueEvidenceSeverity = Literal["info", "blocker"]

PRICING_PAGE_KEYS = (
    "human_approved_pricing_page_copy",
    "approved_plan_and_usage_terms",
    "legal_review_completed",
    "production_readiness_non_claim_reviewed",
    "pricing_page_publication_approval_recorded",
)
PAYMENT_PROVIDER_KEYS = (
    "payment_provider_selected",
    "test_mode_configuration_reviewed",
    "checkout_enablement_approval_required",
    "webhook_signature_validation_tested",
    "payment_event_redaction_reviewed",
    "security_review_completed",
)
INVOICE_PROCESS_KEYS = (
    "invoice_owner_named",
    "invoice_workflow_approved",
    "contract_handoff_defined",
    "payment_reconciliation_tested",
    "billing_support_handoff_defined",
    "bookkeeping_review_completed",
)
TAX_REVIEW_KEYS = (
    "target_jurisdictions_reviewed",
    "tax_obligations_reviewed",
    "invoice_wording_approved",
    "currency_policy_approved",
    "tax_collection_approval_recorded",
)
REFUND_POLICY_KEYS = (
    "refund_policy_approved",
    "cancellation_process_approved",
    "trial_conversion_policy_approved",
    "service_failure_remedy_boundary_approved",
    "support_escalation_route_defined",
)
TENANT_BILLING_ISOLATION_KEYS = (
    "tenant_billing_account_model_approved",
    "tenant_invoice_partitioning_tested",
    "tenant_payment_event_partitioning_tested",
    "cross_tenant_billing_access_tests_passed",
    "billing_audit_metadata_policy_approved",
    "tenant_billing_retention_policy_approved",
)
FORBIDDEN_TRUE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
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
)


@dataclass(frozen=True)
class ProductionBillingRevenueEvidenceFinding:
    check_id: str
    severity: ProductionBillingRevenueEvidenceSeverity
    passed: bool
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "passed": self.passed,
            "message": self.message,
        }


def _finding(
    check_id: str,
    severity: ProductionBillingRevenueEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionBillingRevenueEvidenceFinding:
    return ProductionBillingRevenueEvidenceFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def _all_true(data: dict[str, object], keys: tuple[str, ...]) -> bool:
    return all(data.get(key) is True for key in keys)


def _missing_true_keys(data: dict[str, object], keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if data.get(key) is not True]


def _read_evidence(path_value: str) -> tuple[bool, bool, dict[str, object]]:
    if not path_value:
        return False, False, {}
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        return False, False, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, False, {}
    if not isinstance(data, dict):
        return True, False, {}
    return True, True, data


def evaluate_production_billing_revenue_evidence(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic production billing/revenue evidence readiness.

    A `pass` means the local evidence file is internally complete enough for
    human production launch review. It is not published pricing, a payment
    provider integration, checkout enablement, invoice operation, tax approval,
    refund policy publication, tenant billing isolation in production, revenue
    validation, or production-readiness approval.
    """

    path_configured = bool(settings.production_billing_revenue_evidence_path)
    file_exists, file_parseable, data = _read_evidence(
        settings.production_billing_revenue_evidence_path
    )
    correct_type = (
        data.get("billing_revenue_evidence_type")
        == "production_billing_revenue_evidence"
    )
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    pricing_page_evidence_complete = _all_true(data, PRICING_PAGE_KEYS)
    payment_provider_evidence_complete = _all_true(data, PAYMENT_PROVIDER_KEYS)
    invoice_process_evidence_complete = _all_true(data, INVOICE_PROCESS_KEYS)
    tax_review_evidence_complete = _all_true(data, TAX_REVIEW_KEYS)
    refund_policy_evidence_complete = _all_true(data, REFUND_POLICY_KEYS)
    tenant_billing_isolation_evidence_complete = _all_true(
        data, TENANT_BILLING_ISOLATION_KEYS
    )
    production_billing_revenue_ready = (
        pricing_page_evidence_complete
        and payment_provider_evidence_complete
        and invoice_process_evidence_complete
        and tax_review_evidence_complete
        and refund_policy_evidence_complete
        and tenant_billing_isolation_evidence_complete
        and not forbidden_true
    )

    findings = [
        _finding(
            "billing_revenue_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH must point to local billing/revenue evidence",
        ),
        _finding(
            "billing_revenue_evidence_file_exists",
            "blocker",
            file_exists,
            "billing/revenue evidence file must exist locally",
        ),
        _finding(
            "billing_revenue_evidence_file_parseable",
            "blocker",
            file_parseable,
            "billing/revenue evidence file must be parseable JSON",
        ),
        _finding(
            "billing_revenue_evidence_type_valid",
            "blocker",
            correct_type,
            "billing_revenue_evidence_type must be production_billing_revenue_evidence",
        ),
        _finding(
            "pricing_page_evidence_complete",
            "blocker",
            pricing_page_evidence_complete,
            "pricing-page evidence must be complete",
        ),
        _finding(
            "payment_provider_evidence_complete",
            "blocker",
            payment_provider_evidence_complete,
            "payment-provider evidence must be complete",
        ),
        _finding(
            "invoice_process_evidence_complete",
            "blocker",
            invoice_process_evidence_complete,
            "invoice-process evidence must be complete",
        ),
        _finding(
            "tax_review_evidence_complete",
            "blocker",
            tax_review_evidence_complete,
            "tax-review evidence must be complete",
        ),
        _finding(
            "refund_policy_evidence_complete",
            "blocker",
            refund_policy_evidence_complete,
            "refund-policy evidence must be complete",
        ),
        _finding(
            "tenant_billing_isolation_evidence_complete",
            "blocker",
            tenant_billing_isolation_evidence_complete,
            "tenant billing isolation evidence must be complete",
        ),
        _finding(
            "boundary_non_claims",
            "blocker",
            not forbidden_true,
            "billing/revenue evidence must not claim pricing publication, payment provider configuration, checkout, invoices, tax collection, customer payment, revenue validation, launch, production readiness, customer validation, private-core exposure, or code modification",
        ),
        _finding(
            "no_external_actions",
            "info",
            True,
            "readiness check only reads a local evidence file and performs no external action",
        ),
    ]

    blocking_failures = [
        finding
        for finding in findings
        if finding.severity == "blocker" and not finding.passed
    ]
    if forbidden_true:
        status: ProductionBillingRevenueEvidenceStatus = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_billing_revenue_evidence_type": "production_billing_revenue_evidence_readiness",
        "production_billing_revenue_evidence_readiness_v0_1": True,
        "status": status,
        "billing_revenue_evidence_path_configured": path_configured,
        "billing_revenue_evidence_file_exists": file_exists,
        "billing_revenue_evidence_file_parseable": file_parseable,
        "billing_revenue_evidence_type_valid": correct_type,
        "pricing_page_evidence_complete": pricing_page_evidence_complete,
        "payment_provider_evidence_complete": payment_provider_evidence_complete,
        "invoice_process_evidence_complete": invoice_process_evidence_complete,
        "tax_review_evidence_complete": tax_review_evidence_complete,
        "refund_policy_evidence_complete": refund_policy_evidence_complete,
        "tenant_billing_isolation_evidence_complete": tenant_billing_isolation_evidence_complete,
        "production_billing_revenue_ready": production_billing_revenue_ready,
        "pricing_page_missing_evidence": _missing_true_keys(data, PRICING_PAGE_KEYS),
        "payment_provider_missing_evidence": _missing_true_keys(
            data, PAYMENT_PROVIDER_KEYS
        ),
        "invoice_process_missing_evidence": _missing_true_keys(
            data, INVOICE_PROCESS_KEYS
        ),
        "tax_review_missing_evidence": _missing_true_keys(data, TAX_REVIEW_KEYS),
        "refund_policy_missing_evidence": _missing_true_keys(
            data, REFUND_POLICY_KEYS
        ),
        "tenant_billing_isolation_missing_evidence": _missing_true_keys(
            data, TENANT_BILLING_ISOLATION_KEYS
        ),
        "boundary_violation_count": len(forbidden_true),
        "boundary_violations": forbidden_true,
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
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human launch review may use this evidence only after all other production blockers are resolved"
        if status == "pass"
        else "complete production pricing, payment, invoice, tax, refund, and tenant-billing evidence before launch review",
    }
