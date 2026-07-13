"""Read-only operations routes for the SAEE MVP API shell.

These routes expose public-shell aggregate operations reports only. They do
not inspect request bodies, credentials, private-core internals, runtime
internals, fitness logic, selection logic, mutation logic, or lineage internals.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from saee_backend.api.security import (
    require_api_key,
    require_jwt_preview_auth,
    require_rbac_route,
    require_tenant_boundary,
)
from saee_backend.services.operations_alert_policy import evaluate_operations_alert_policy
from saee_backend.services.operations_telemetry import build_operations_telemetry_snapshot


router = APIRouter(dependencies=[Depends(require_api_key), Depends(require_jwt_preview_auth)])


@router.get(
    "/telemetry",
    dependencies=[Depends(require_rbac_route("GET /operations/telemetry"))],
)
def get_operations_telemetry(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return aggregate request-metadata telemetry for local/pre-commercial review."""

    snapshot = build_operations_telemetry_snapshot(tenant_id=tenant_id)
    snapshot["route_scope"] = "public_shell_operations_read_only"
    snapshot["tenant_boundary_checked"] = tenant_id is not None
    snapshot["tenant_scope_filter_applied"] = tenant_id is not None
    snapshot["tenant_id_raw_filter_recorded"] = False
    snapshot["production_monitoring_available"] = False
    snapshot["operations_telemetry_external_export_available"] = False
    snapshot["body_inspected"] = False
    snapshot["credentials_inspected"] = False
    snapshot["private_core_inspected"] = False
    return snapshot


@router.get(
    "/alerts",
    dependencies=[Depends(require_rbac_route("GET /operations/alerts"))],
)
def get_operations_alert_candidates(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return local alert candidates for human review only."""

    report = evaluate_operations_alert_policy(tenant_id=tenant_id)
    report["route_scope"] = "public_shell_operations_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["tenant_scope_filter_applied"] = tenant_id is not None
    report["tenant_id_raw_filter_recorded"] = False
    report["external_alert_delivery_available"] = False
    report["production_monitoring_available"] = False
    report["alerting_available"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    return report
