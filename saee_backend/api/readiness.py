"""Read-only preview readiness routes for the SAEE MVP API shell.

These routes expose public-shell support, vulnerability, privacy/security,
legal/DPA, operations, data-operations, and billing/pricing readiness reports
only. They do not expose contact values,
credentials, request bodies, private-core internals, runtime internals, fitness
logic, selection logic, mutation logic, lineage internals, live data paths, or
payment details.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from saee_backend.api.security import (
    require_api_key,
    require_jwt_preview_auth,
    require_rbac_route,
    require_tenant_boundary,
)
from saee_backend.config import SETTINGS
from saee_backend.services.billing_pricing_readiness import (
    evaluate_billing_pricing_readiness,
)
from saee_backend.services.legal_readiness import evaluate_legal_readiness
from saee_backend.services.operations_readiness import evaluate_operations_readiness
from saee_backend.services.privacy_security_readiness import (
    evaluate_privacy_security_readiness,
)
from saee_backend.services.production_data_operations_evidence import (
    evaluate_production_data_operations_evidence,
)
from saee_backend.services.support_readiness import evaluate_support_readiness
from saee_backend.services.vulnerability_management_readiness import (
    evaluate_vulnerability_management_readiness,
)


router = APIRouter(dependencies=[Depends(require_api_key), Depends(require_jwt_preview_auth)])


@router.get(
    "/support",
    dependencies=[Depends(require_rbac_route("GET /readiness/support"))],
)
def get_support_readiness(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return controlled-preview support readiness for human review."""

    report = evaluate_support_readiness()
    report["route_scope"] = "public_shell_preview_readiness_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["support_contact_value_exposed"] = False
    report["customer_support_available"] = False
    report["production_support_available"] = False
    report["sla_available"] = False
    report["on_call_rotation_available"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    return report


@router.get(
    "/data-operations",
    dependencies=[Depends(require_rbac_route("GET /readiness/data-operations"))],
)
def get_data_operations_readiness(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return read-only data-operations evidence readiness for human review."""

    report = evaluate_production_data_operations_evidence(SETTINGS)
    report["route_scope"] = "public_shell_data_operations_readiness_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["data_operations_readiness_api_v0_1"] = True
    report["read_only_data_operations_readiness_api"] = True
    report["blockers_closed_by_route"] = 0
    report["task_candidates_executed"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    report["live_data_path_inspected"] = False
    report["restore_executed_by_route"] = False
    report["production_ready"] = False
    report["customer_validated"] = False
    report["product_launched"] = False
    report["public_sdk_released"] = False
    report["private_core_exposed"] = False
    report["api_schema_modified"] = False
    report["runtime_modified"] = False
    report["kernel_modified"] = False
    report["external_calls_made"] = False
    return report


@router.get(
    "/operations",
    dependencies=[Depends(require_rbac_route("GET /readiness/operations"))],
)
def get_operations_readiness(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return read-only operations readiness for human review."""

    report = evaluate_operations_readiness(SETTINGS)
    report["route_scope"] = "public_shell_operations_readiness_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["operations_readiness_api_v0_1"] = True
    report["operations_readiness_api_available"] = True
    report["read_only_operations_readiness_api"] = True
    report["blockers_closed_by_route"] = 0
    report["task_candidates_executed"] = False
    report["monitoring_configured_by_route"] = False
    report["external_alert_delivery_configured_by_route"] = False
    report["on_call_rotation_started_by_route"] = False
    report["sla_started_by_route"] = False
    report["support_process_started_by_route"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    report["production_ready"] = False
    report["customer_validated"] = False
    report["product_launched"] = False
    report["public_sdk_released"] = False
    report["private_core_exposed"] = False
    report["api_schema_modified"] = False
    report["runtime_modified"] = False
    report["kernel_modified"] = False
    report["external_calls_made"] = False
    return report


@router.get(
    "/privacy-security",
    dependencies=[Depends(require_rbac_route("GET /readiness/privacy-security"))],
)
def get_privacy_security_readiness(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return read-only privacy/security readiness for human review."""

    report = evaluate_privacy_security_readiness(SETTINGS)
    report["route_scope"] = "public_shell_privacy_security_readiness_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["privacy_security_readiness_api_v0_1"] = True
    report["privacy_security_readiness_api_available"] = True
    report["read_only_privacy_security_readiness_api"] = True
    report["blockers_closed_by_route"] = 0
    report["task_candidates_executed"] = False
    report["formal_security_review_completed_by_route"] = False
    report["privacy_legal_review_completed_by_route"] = False
    report["dpa_approved_by_route"] = False
    report["security_certification_created_by_route"] = False
    report["customer_data_processing_enabled_by_route"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    report["production_ready"] = False
    report["customer_validated"] = False
    report["customer_contacted"] = False
    report["product_launched"] = False
    report["public_sdk_released"] = False
    report["private_core_exposed"] = False
    report["api_schema_modified"] = False
    report["runtime_modified"] = False
    report["kernel_modified"] = False
    report["external_calls_made"] = False
    return report


@router.get(
    "/legal",
    dependencies=[Depends(require_rbac_route("GET /readiness/legal"))],
)
def get_legal_readiness(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return read-only legal and DPA readiness for human review."""

    report = evaluate_legal_readiness(SETTINGS)
    report["route_scope"] = "public_shell_legal_readiness_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["legal_readiness_api_v0_1"] = True
    report["legal_readiness_api_available"] = True
    report["read_only_legal_readiness_api"] = True
    report["blockers_closed_by_route"] = 0
    report["task_candidates_executed"] = False
    report["terms_published_by_route"] = False
    report["privacy_notice_published_by_route"] = False
    report["legal_review_completed_by_route"] = False
    report["dpa_approved_by_route"] = False
    report["customer_data_processing_enabled_by_route"] = False
    report["contract_template_created_by_route"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    report["customer_contacted"] = False
    report["production_ready"] = False
    report["customer_validated"] = False
    report["product_launched"] = False
    report["public_sdk_released"] = False
    report["private_core_exposed"] = False
    report["api_schema_modified"] = False
    report["runtime_modified"] = False
    report["kernel_modified"] = False
    report["external_calls_made"] = False
    return report


@router.get(
    "/billing-pricing",
    dependencies=[Depends(require_rbac_route("GET /readiness/billing-pricing"))],
)
def get_billing_pricing_readiness(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return read-only billing and pricing readiness for human review."""

    report = evaluate_billing_pricing_readiness(SETTINGS)
    report["route_scope"] = "public_shell_billing_pricing_readiness_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["billing_pricing_readiness_api_v0_1"] = True
    report["read_only_billing_pricing_readiness_api"] = True
    report["blockers_closed_by_route"] = 0
    report["task_candidates_executed"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    report["payment_credentials_inspected"] = False
    report["payment_provider_contacted_by_route"] = False
    report["checkout_created_by_route"] = False
    report["invoice_created_by_route"] = False
    report["customer_contacted"] = False
    report["production_ready"] = False
    report["customer_validated"] = False
    report["product_launched"] = False
    report["public_sdk_released"] = False
    report["private_core_exposed"] = False
    report["api_schema_modified"] = False
    report["runtime_modified"] = False
    report["kernel_modified"] = False
    report["external_calls_made"] = False
    return report


@router.get(
    "/vulnerability",
    dependencies=[Depends(require_rbac_route("GET /readiness/vulnerability"))],
)
def get_vulnerability_readiness(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return controlled-preview vulnerability intake readiness for human review."""

    report = evaluate_vulnerability_management_readiness()
    report["route_scope"] = "public_shell_preview_readiness_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["security_contact_value_exposed"] = False
    report["vulnerability_management_available"] = False
    report["production_vulnerability_management_ready"] = False
    report["formal_security_review_completed"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    return report
