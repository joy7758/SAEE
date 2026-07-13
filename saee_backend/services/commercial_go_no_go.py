"""Commercial go/no-go aggregation for the SAEE public API shell.

This module aggregates existing public-shell readiness signals into a single
local decision report. It does not deploy SAEE, call external services, change
API schema, inspect private core, or modify runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SaeeBackendSettings
from saee_backend.services.commercial_preflight import evaluate_commercial_preflight
from saee_backend.services.production_auth_evidence import (
    evaluate_production_auth_evidence,
)
from saee_backend.services.production_billing_revenue_evidence import (
    evaluate_production_billing_revenue_evidence,
)
from saee_backend.services.production_customer_validation_evidence import (
    evaluate_production_customer_validation_evidence,
)
from saee_backend.services.production_data_operations_evidence import (
    evaluate_production_data_operations_evidence,
)
from saee_backend.services.production_operations_evidence import (
    evaluate_production_operations_evidence,
)
from saee_backend.services.production_privacy_security_legal_evidence import (
    evaluate_production_privacy_security_legal_evidence,
)
from saee_backend.services.production_support_evidence import (
    evaluate_production_support_evidence,
)
from saee_backend.services.production_tenant_storage_evidence import (
    evaluate_production_tenant_storage_evidence,
)


CommercialStatus = Literal["go", "hold", "stop"]
BlockerScope = Literal["controlled_preview", "production_launch"]


@dataclass(frozen=True)
class GoNoGoBlocker:
    blocker_id: str
    category: str
    scope: BlockerScope
    satisfied: bool
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "blocker_id": self.blocker_id,
            "category": self.category,
            "scope": self.scope,
            "satisfied": self.satisfied,
            "message": self.message,
        }


def _blocker(
    blocker_id: str,
    category: str,
    scope: BlockerScope,
    satisfied: bool,
    message: str,
) -> GoNoGoBlocker:
    return GoNoGoBlocker(
        blocker_id=blocker_id,
        category=category,
        scope=scope,
        satisfied=satisfied,
        message=message,
    )


def _production_blockers(
    readiness: dict[str, object],
    auth_evidence: dict[str, object],
    support_evidence: dict[str, object],
    data_ops_evidence: dict[str, object],
    operations_evidence: dict[str, object],
    privacy_security_legal_evidence: dict[str, object],
    billing_revenue_evidence: dict[str, object],
    tenant_storage_evidence: dict[str, object],
    customer_validation_evidence: dict[str, object],
) -> list[GoNoGoBlocker]:
    return [
        _blocker(
            "production_identity_provider",
            "auth",
            "production_launch",
            readiness["production_identity_provider_available"] is True
            or auth_evidence["production_identity_provider_available"] is True,
            "Production identity provider must be available before commercial launch.",
        ),
        _blocker(
            "oauth_oidc",
            "auth",
            "production_launch",
            readiness["oauth_oidc_available"] is True
            or auth_evidence["oauth_oidc_available"] is True,
            "OAuth/OIDC must be available before production authentication can be claimed.",
        ),
        _blocker(
            "rbac",
            "auth",
            "production_launch",
            readiness["rbac_available"] is True or auth_evidence["rbac_available"] is True,
            "Role-based access control must be available before production launch.",
        ),
        _blocker(
            "tenant_storage_isolation",
            "tenant",
            "production_launch",
            readiness["tenant_storage_isolated"] is True
            or tenant_storage_evidence[
                "tenant_storage_isolation_evidence_complete"
            ]
            is True,
            "Tenant-isolated storage is required before multi-tenant production use.",
        ),
        _blocker(
            "production_monitoring",
            "operations",
            "production_launch",
            readiness["production_monitoring_available"] is True
            or operations_evidence["production_monitoring_available"] is True,
            "Production monitoring must be available before production launch.",
        ),
        _blocker(
            "external_alert_delivery",
            "operations",
            "production_launch",
            readiness["external_alert_delivery_available"] is True
            or operations_evidence["external_alert_delivery_available"] is True,
            "External alert delivery must be available before production operations.",
        ),
        _blocker(
            "on_call_rotation",
            "operations",
            "production_launch",
            readiness["on_call_rotation_available"] is True
            or support_evidence["on_call_rotation_available"] is True
            or operations_evidence["on_call_rotation_available"] is True,
            "On-call rotation must be available before production operations.",
        ),
        _blocker(
            "sla",
            "support",
            "production_launch",
            readiness["sla_available"] is True or support_evidence["sla_available"] is True,
            "SLA must be approved before commercial production support is claimed.",
        ),
        _blocker(
            "support_contact",
            "support",
            "production_launch",
            readiness["support_contact_configured"] is True
            or support_evidence["support_contact_available"] is True,
            "Support contact must be configured before customer-facing preview support.",
        ),
        _blocker(
            "customer_support",
            "support",
            "production_launch",
            readiness["customer_support_available"] is True
            or support_evidence["customer_support_available"] is True,
            "Customer support must be available before commercial launch.",
        ),
        _blocker(
            "formal_security_review",
            "privacy_security",
            "production_launch",
            readiness["formal_security_review_completed"] is True
            or privacy_security_legal_evidence["formal_security_review_completed"] is True,
            "Formal security review must be complete before production readiness.",
        ),
        _blocker(
            "privacy_legal_review",
            "privacy_security",
            "production_launch",
            readiness["privacy_legal_review_completed"] is True
            or privacy_security_legal_evidence["privacy_legal_review_completed"] is True,
            "Privacy legal review must be complete before customer data processing.",
        ),
        _blocker(
            "data_processing_agreement",
            "privacy_security",
            "production_launch",
            readiness["data_processing_agreement_available"] is True
            or privacy_security_legal_evidence["data_processing_agreement_available"] is True,
            "A data processing agreement is required before customer data processing.",
        ),
        _blocker(
            "vulnerability_management",
            "privacy_security",
            "production_launch",
            readiness["vulnerability_management_available"] is True
            or privacy_security_legal_evidence["vulnerability_management_available"] is True,
            "Vulnerability management must be available before production launch.",
        ),
        _blocker(
            "pilot_results",
            "validation",
            "production_launch",
            readiness["pilot_results_recorded"] is True
            or customer_validation_evidence["pilot_results_evidence_complete"] is True,
            "Pilot results must be recorded before claiming customer validation.",
        ),
        _blocker(
            "customer_validated",
            "validation",
            "production_launch",
            readiness["customer_validated"] is True
            or customer_validation_evidence["customer_validation_evidence_complete"]
            is True,
            "Real customer validation is required before commercial launch.",
        ),
        _blocker(
            "pricing_page",
            "billing",
            "production_launch",
            readiness["pricing_page_published"] is True
            or billing_revenue_evidence["pricing_page_evidence_complete"] is True,
            "Published pricing must be approved before self-serve commercial launch.",
        ),
        _blocker(
            "payment_provider",
            "billing",
            "production_launch",
            readiness["payment_provider_configured"] is True
            or billing_revenue_evidence["payment_provider_evidence_complete"] is True,
            "Payment provider must be configured before paid trials or checkout.",
        ),
        _blocker(
            "invoice_process",
            "billing",
            "production_launch",
            readiness["invoice_process_ready"] is True
            or billing_revenue_evidence["invoice_process_evidence_complete"] is True,
            "Invoice process must be ready before enterprise paid pilots.",
        ),
        _blocker(
            "tax_review",
            "billing",
            "production_launch",
            readiness["tax_review_completed"] is True
            or billing_revenue_evidence["tax_review_evidence_complete"] is True,
            "Tax review must be complete before collecting payment.",
        ),
        _blocker(
            "refund_policy",
            "billing",
            "production_launch",
            readiness["refund_policy_available"] is True
            or billing_revenue_evidence["refund_policy_evidence_complete"] is True,
            "Refund policy must be available before paid checkout.",
        ),
        _blocker(
            "tenant_billing_isolation",
            "billing",
            "production_launch",
            readiness["tenant_billing_isolated"] is True
            or billing_revenue_evidence[
                "tenant_billing_isolation_evidence_complete"
            ]
            is True,
            "Tenant billing isolation must be available before multi-tenant paid use.",
        ),
        _blocker(
            "restore_tested",
            "data_ops",
            "production_launch",
            readiness["restore_tested"] is True
            or data_ops_evidence["restore_tested"] is True,
            "Restore must be tested before production data operations.",
        ),
        _blocker(
            "production_restore_policy",
            "data_ops",
            "production_launch",
            readiness["production_restore_policy_available"] is True
            or data_ops_evidence["production_restore_policy_available"] is True,
            "Production restore policy must exist before production launch.",
        ),
    ]


def _boundary_violations(readiness: dict[str, object], preflight: dict[str, object]) -> list[str]:
    checks = {
        "production_ready": readiness["production_ready"],
        "product_launched": readiness["product_launched"],
        "production_legal_ready": readiness["production_legal_ready"],
        "legal_approval_completed": readiness["legal_approval_completed"],
        "customer_data_processing_ready": readiness["customer_data_processing_ready"],
        "private_core_exposed": readiness["private_core_exposed"],
        "external_calls_made": preflight["external_calls_made"],
        "api_schema_modified": preflight["api_schema_modified"],
        "runtime_modified": preflight["runtime_modified"],
        "kernel_modified": preflight["kernel_modified"],
    }
    return [key for key, value in checks.items() if value is True]


def evaluate_commercial_go_no_go(settings: SaeeBackendSettings) -> dict[str, object]:
    """Return a deterministic local commercial go/no-go report."""

    readiness = settings.readiness_payload()
    preflight = evaluate_commercial_preflight(settings)
    auth_evidence = evaluate_production_auth_evidence(settings)
    support_evidence = evaluate_production_support_evidence(settings)
    data_ops_evidence = evaluate_production_data_operations_evidence(settings)
    operations_evidence = evaluate_production_operations_evidence(settings)
    privacy_security_legal_evidence = (
        evaluate_production_privacy_security_legal_evidence(settings)
    )
    billing_revenue_evidence = evaluate_production_billing_revenue_evidence(settings)
    tenant_storage_evidence = evaluate_production_tenant_storage_evidence(settings)
    customer_validation_evidence = evaluate_production_customer_validation_evidence(
        settings
    )
    preview_status: CommercialStatus = "go" if preflight["status"] == "pass" else "hold"
    production_blockers = _production_blockers(
        readiness,
        auth_evidence,
        support_evidence,
        data_ops_evidence,
        operations_evidence,
        privacy_security_legal_evidence,
        billing_revenue_evidence,
        tenant_storage_evidence,
        customer_validation_evidence,
    )
    unsatisfied_production = [blocker for blocker in production_blockers if not blocker.satisfied]
    boundary_violations = _boundary_violations(readiness, preflight)
    boundary_violations.extend(
        f"production_auth_evidence:{item}"
        for item in auth_evidence["boundary_violations"]
    )
    boundary_violations.extend(
        f"production_support_evidence:{item}"
        for item in support_evidence["boundary_violations"]
    )
    boundary_violations.extend(
        f"production_data_operations_evidence:{item}"
        for item in data_ops_evidence["boundary_violations"]
    )
    boundary_violations.extend(
        f"production_operations_evidence:{item}"
        for item in operations_evidence["boundary_violations"]
    )
    boundary_violations.extend(
        f"production_privacy_security_legal_evidence:{item}"
        for item in privacy_security_legal_evidence["boundary_violations"]
    )
    boundary_violations.extend(
        f"production_billing_revenue_evidence:{item}"
        for item in billing_revenue_evidence["boundary_violations"]
    )
    boundary_violations.extend(
        f"production_tenant_storage_evidence:{item}"
        for item in tenant_storage_evidence["boundary_violations"]
    )
    boundary_violations.extend(
        f"production_customer_validation_evidence:{item}"
        for item in customer_validation_evidence["boundary_violations"]
    )

    if boundary_violations:
        commercial_status: CommercialStatus = "stop"
        production_launch_status: CommercialStatus = "stop"
        next_action = "fix boundary violations before any commercial action"
    elif unsatisfied_production:
        commercial_status = "hold"
        production_launch_status = "hold"
        next_action = "resolve production launch blockers before commercial release"
    else:
        commercial_status = "go"
        production_launch_status = "go"
        next_action = "separate human launch approval still required"

    satisfied_count = len(production_blockers) - len(unsatisfied_production)
    readiness_score = round(satisfied_count / len(production_blockers), 4)

    return {
        "go_no_go_type": "commercial_readiness_go_no_go",
        "environment": settings.environment,
        "commercial_status": commercial_status,
        "controlled_preview_status": preview_status,
        "production_launch_status": production_launch_status,
        "controlled_preview_preflight_status": preflight["status"],
        "production_auth_evidence_status": auth_evidence["status"],
        "production_auth_evidence_path_configured": auth_evidence[
            "auth_evidence_path_configured"
        ],
        "production_auth_evidence_file_parseable": auth_evidence[
            "auth_evidence_file_parseable"
        ],
        "production_support_evidence_status": support_evidence["status"],
        "production_support_evidence_path_configured": support_evidence[
            "support_evidence_path_configured"
        ],
        "production_support_evidence_file_parseable": support_evidence[
            "support_evidence_file_parseable"
        ],
        "production_data_operations_evidence_status": data_ops_evidence["status"],
        "production_data_operations_evidence_path_configured": data_ops_evidence[
            "data_operations_evidence_path_configured"
        ],
        "production_data_operations_evidence_file_parseable": data_ops_evidence[
            "data_operations_evidence_file_parseable"
        ],
        "production_operations_evidence_status": operations_evidence["status"],
        "production_operations_evidence_path_configured": operations_evidence[
            "operations_evidence_path_configured"
        ],
        "production_operations_evidence_file_parseable": operations_evidence[
            "operations_evidence_file_parseable"
        ],
        "production_privacy_security_legal_evidence_status": privacy_security_legal_evidence[
            "status"
        ],
        "production_privacy_security_legal_evidence_path_configured": privacy_security_legal_evidence[
            "privacy_security_legal_evidence_path_configured"
        ],
        "production_privacy_security_legal_evidence_file_parseable": privacy_security_legal_evidence[
            "privacy_security_legal_evidence_file_parseable"
        ],
        "production_billing_revenue_evidence_status": billing_revenue_evidence[
            "status"
        ],
        "production_billing_revenue_evidence_path_configured": billing_revenue_evidence[
            "billing_revenue_evidence_path_configured"
        ],
        "production_billing_revenue_evidence_file_parseable": billing_revenue_evidence[
            "billing_revenue_evidence_file_parseable"
        ],
        "production_tenant_storage_evidence_status": tenant_storage_evidence[
            "status"
        ],
        "production_tenant_storage_evidence_path_configured": tenant_storage_evidence[
            "tenant_storage_evidence_path_configured"
        ],
        "production_tenant_storage_evidence_file_parseable": tenant_storage_evidence[
            "tenant_storage_evidence_file_parseable"
        ],
        "production_customer_validation_evidence_status": customer_validation_evidence[
            "status"
        ],
        "production_customer_validation_evidence_path_configured": customer_validation_evidence[
            "customer_validation_evidence_path_configured"
        ],
        "production_customer_validation_evidence_file_parseable": customer_validation_evidence[
            "customer_validation_evidence_file_parseable"
        ],
        "data_ops_evidence_restore_tested": data_ops_evidence["restore_tested"],
        "data_ops_evidence_production_restore_tested": data_ops_evidence[
            "production_restore_tested"
        ],
        "data_ops_evidence_production_restore_policy_available": data_ops_evidence[
            "production_restore_policy_available"
        ],
        "auth_evidence_production_identity_provider_available": auth_evidence[
            "production_identity_provider_available"
        ],
        "auth_evidence_oauth_oidc_available": auth_evidence["oauth_oidc_available"],
        "auth_evidence_rbac_available": auth_evidence["rbac_available"],
        "support_evidence_customer_support_available": support_evidence[
            "customer_support_available"
        ],
        "support_evidence_sla_available": support_evidence["sla_available"],
        "support_evidence_on_call_rotation_available": support_evidence[
            "on_call_rotation_available"
        ],
        "operations_evidence_production_monitoring_available": operations_evidence[
            "production_monitoring_available"
        ],
        "operations_evidence_external_alert_delivery_available": operations_evidence[
            "external_alert_delivery_available"
        ],
        "operations_evidence_on_call_rotation_available": operations_evidence[
            "on_call_rotation_available"
        ],
        "privacy_security_legal_evidence_formal_security_review_completed": privacy_security_legal_evidence[
            "formal_security_review_completed"
        ],
        "privacy_security_legal_evidence_privacy_legal_review_completed": privacy_security_legal_evidence[
            "privacy_legal_review_completed"
        ],
        "privacy_security_legal_evidence_data_processing_agreement_available": privacy_security_legal_evidence[
            "data_processing_agreement_available"
        ],
        "privacy_security_legal_evidence_vulnerability_management_available": privacy_security_legal_evidence[
            "vulnerability_management_available"
        ],
        "billing_revenue_evidence_pricing_page_complete": billing_revenue_evidence[
            "pricing_page_evidence_complete"
        ],
        "billing_revenue_evidence_payment_provider_complete": billing_revenue_evidence[
            "payment_provider_evidence_complete"
        ],
        "billing_revenue_evidence_invoice_process_complete": billing_revenue_evidence[
            "invoice_process_evidence_complete"
        ],
        "billing_revenue_evidence_tax_review_complete": billing_revenue_evidence[
            "tax_review_evidence_complete"
        ],
        "billing_revenue_evidence_refund_policy_complete": billing_revenue_evidence[
            "refund_policy_evidence_complete"
        ],
        "billing_revenue_evidence_tenant_billing_isolation_complete": billing_revenue_evidence[
            "tenant_billing_isolation_evidence_complete"
        ],
        "tenant_storage_evidence_model_complete": tenant_storage_evidence[
            "tenant_storage_model_evidence_complete"
        ],
        "tenant_storage_evidence_isolation_complete": tenant_storage_evidence[
            "tenant_storage_isolation_evidence_complete"
        ],
        "tenant_storage_evidence_operations_complete": tenant_storage_evidence[
            "tenant_operations_evidence_complete"
        ],
        "tenant_storage_evidence_security_privacy_complete": tenant_storage_evidence[
            "tenant_security_privacy_evidence_complete"
        ],
        "customer_validation_evidence_pilot_results_complete": customer_validation_evidence[
            "pilot_results_evidence_complete"
        ],
        "customer_validation_evidence_customer_value_complete": customer_validation_evidence[
            "customer_value_evidence_complete"
        ],
        "customer_validation_evidence_claim_permission_complete": customer_validation_evidence[
            "claim_permission_evidence_complete"
        ],
        "customer_validation_evidence_boundary_review_complete": customer_validation_evidence[
            "boundary_review_evidence_complete"
        ],
        "customer_validation_evidence_complete": customer_validation_evidence[
            "customer_validation_evidence_complete"
        ],
        "readiness_score": readiness_score,
        "satisfied_production_checks": satisfied_count,
        "total_production_checks": len(production_blockers),
        "production_blocker_count": len(unsatisfied_production),
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blockers": [blocker.as_dict() for blocker in production_blockers],
        "unsatisfied_blockers": [blocker.as_dict() for blocker in unsatisfied_production],
        "production_ready": readiness["production_ready"],
        "customer_validated": readiness["customer_validated"],
        "product_launched": readiness["product_launched"],
        "public_sdk_released": readiness["public_sdk_released"],
        "legal_readiness_v0_1": readiness["legal_readiness_v0_1"],
        "legal_readiness_status": readiness["legal_readiness_status"],
        "terms_of_service_draft_available": readiness["terms_of_service_draft_available"],
        "terms_of_service_published": readiness["terms_of_service_published"],
        "terms_legal_review_completed": readiness["terms_legal_review_completed"],
        "privacy_notice_draft_available": readiness["privacy_notice_draft_available"],
        "privacy_notice_published": readiness["privacy_notice_published"],
        "privacy_legal_review_completed": readiness["privacy_legal_review_completed"],
        "dpa_review_packet_available": readiness["dpa_review_packet_available"],
        "data_processing_agreement_draft_available": readiness[
            "data_processing_agreement_draft_available"
        ],
        "data_processing_agreement_available": readiness["data_processing_agreement_available"],
        "customer_contract_template_available": readiness[
            "customer_contract_template_available"
        ],
        "legal_approval_completed": readiness["legal_approval_completed"],
        "customer_data_processing_ready": readiness["customer_data_processing_ready"],
        "production_legal_ready": readiness["production_legal_ready"],
        "private_core_exposed": readiness["private_core_exposed"],
        "external_calls_made": preflight["external_calls_made"],
        "api_schema_modified": preflight["api_schema_modified"],
        "runtime_modified": preflight["runtime_modified"],
        "kernel_modified": preflight["kernel_modified"],
        "external_ai_assistant_tested": preflight["external_ai_assistant_tested"],
        "external_model_api_called": preflight["external_model_api_called"],
        "next_action": next_action,
    }
