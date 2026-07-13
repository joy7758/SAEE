"""Billing and pricing readiness for the SAEE public API shell.

This module records whether pricing and billing materials are ready for human
review. It does not configure payment providers, collect payment, send offers,
create invoices, contact customers, launch product, or inspect private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.commercial_preflight import public_use_required


BillingReadinessStatus = Literal["pass", "hold", "stop"]
BillingFindingSeverity = Literal["info", "blocker"]


@dataclass(frozen=True)
class BillingReadinessFinding:
    check_id: str
    severity: BillingFindingSeverity
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
    severity: BillingFindingSeverity,
    passed: bool,
    message: str,
) -> BillingReadinessFinding:
    return BillingReadinessFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def evaluate_billing_pricing_readiness(
    settings: SaeeBackendSettings = SETTINGS,
) -> dict[str, object]:
    """Return deterministic billing and pricing readiness for review."""

    public_use = public_use_required(settings)
    findings = [
        _finding(
            "environment_scope",
            "info",
            True,
            "non-local environment requires explicit billing and pricing review"
            if public_use
            else "local environment detected; billing and pricing readiness is advisory",
        ),
        _finding(
            "pricing_packaging_plan_available",
            "info",
            True,
            "internal MVP pricing and packaging plan is available for review",
        ),
        _finding(
            "billing_policy_draft_available",
            "info",
            True,
            "billing policy draft boundary is documented for human review",
        ),
        _finding(
            "published_price_missing",
            "blocker",
            False,
            "no customer-facing pricing page or approved public offer exists",
        ),
        _finding(
            "payment_provider_missing",
            "blocker",
            False,
            "no payment provider, checkout flow, invoicing process, tax review, or refund policy is configured",
        ),
        _finding(
            "revenue_validation_non_claim",
            "blocker",
            False,
            "no paid pilot, invoice, payment, or revenue validation has been recorded",
        ),
        _finding(
            "customer_validation_non_claim",
            "blocker",
            settings.customer_validated is False,
            "customer_validated must remain false until real customer validation is recorded",
        ),
        _finding(
            "production_non_claim",
            "blocker",
            settings.production_ready is False,
            "production_ready must remain false",
        ),
    ]

    blockers = [finding for finding in findings if finding.severity == "blocker" and not finding.passed]
    status: BillingReadinessStatus = "hold" if blockers else "pass"

    return {
        "billing_pricing_readiness_type": "controlled_preview_billing_pricing_readiness",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "billing_pricing_readiness_v0_1": True,
        "billing_pricing_status": status,
        "pricing_packaging_plan_available": True,
        "internal_price_bands_available": True,
        "billing_policy_draft_available": True,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "invoice_process_ready": False,
        "tax_review_completed": False,
        "refund_policy_available": False,
        "billing_operations_ready": False,
        "tenant_billing_isolated": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
        "product_market_fit_claimed": False,
        "production_readiness_claimed": False,
        "production_ready": settings.production_ready,
        "customer_validated": settings.customer_validated,
        "customer_contacted": False,
        "product_launched": settings.product_launched,
        "public_sdk_released": settings.public_sdk_released,
        "private_core_exposed": settings.private_core_exposed,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blockers),
        "next_action": "complete human pricing review, legal/tax review, payment/invoice process, and real paid validation before claiming billing readiness",
    }
