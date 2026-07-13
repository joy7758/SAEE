"""Read-only commercial status route for the SAEE MVP API shell.

This route exposes the existing local commercial go/no-go report for
controlled preview review only. It does not close blockers, authorize launch,
inspect private-core internals, modify runtime behavior, or change the API
contract schema.
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
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go


router = APIRouter(dependencies=[Depends(require_api_key), Depends(require_jwt_preview_auth)])


@router.get(
    "/status",
    dependencies=[Depends(require_rbac_route("GET /commercial/status"))],
)
def get_commercial_status(
    tenant_id: str | None = Depends(require_tenant_boundary),
) -> dict[str, object]:
    """Return local commercial go/no-go status for human review."""

    report = evaluate_commercial_go_no_go(SETTINGS)
    report["commercial_status_api_v0_1"] = True
    report["commercial_status_api_available"] = True
    report["read_only_commercial_status_api"] = True
    report["route_scope"] = "public_shell_commercial_read_only"
    report["tenant_boundary_checked"] = tenant_id is not None
    report["task_candidates_executed"] = False
    report["blockers_closed_by_route"] = 0
    report["production_ready"] = False
    report["customer_validated"] = False
    report["product_launched"] = False
    report["public_sdk_released"] = False
    report["private_core_exposed"] = False
    report["api_schema_modified"] = False
    report["runtime_modified"] = False
    report["kernel_modified"] = False
    report["external_calls_made"] = False
    report["body_inspected"] = False
    report["credentials_inspected"] = False
    report["private_core_inspected"] = False
    return report
