#!/usr/bin/env python3
"""Smoke check for controlled-preview RBAC route enforcement."""

from __future__ import annotations

import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from fastapi import HTTPException
except ModuleNotFoundError:
    fake_fastapi = types.ModuleType("fastapi")

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class Request:
        pass

    def Header(default=None, alias: str | None = None):
        return default

    fake_fastapi.HTTPException = HTTPException
    fake_fastapi.Request = Request
    fake_fastapi.Header = Header
    sys.modules["fastapi"] = fake_fastapi

from saee_backend.api.security import validate_rbac_role
from saee_backend.config import load_settings
from saee_backend.services.rbac_policy import evaluate_rbac_route
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_RBAC_PREVIEW_ENFORCEMENT_SMOKE: FAIL: " + message)


def expect_http_error(route: str, role: str | None, settings, status_code: int) -> None:
    try:
        validate_rbac_role(route, role, settings)
    except HTTPException as exc:
        require(
            exc.status_code == status_code,
            f"expected HTTP {status_code}, got {exc.status_code}",
        )
        return
    raise SystemExit(
        f"SAEE_RBAC_PREVIEW_ENFORCEMENT_SMOKE: FAIL: expected HTTP {status_code}"
    )


def main() -> None:
    generate_template()
    default = load_settings({})
    require(default.require_rbac_role is False, "RBAC role guard disabled by default")
    require(default.rbac_policy_path == "", "RBAC policy path empty by default")
    require(default.ready is True, "local default remains ready")
    payload = default.readiness_payload()
    require(payload["rbac_preview_enforcement_available"] is True, "readiness exposes RBAC preview")
    require(payload["rbac_role_required"] is False, "default role required false")
    require(payload["preview_rbac_available"] is False, "default preview RBAC false")
    require(payload["production_auth_ready"] is False, "production auth remains false")

    missing_policy = load_settings({"SAEE_REQUIRE_RBAC_ROLE": "true"})
    require(missing_policy.require_rbac_role is True, "RBAC role guard configurable")
    require(missing_policy.ready is False, "missing policy path is not ready")
    expect_http_error("GET /experiment", "viewer", missing_policy, 503)

    protected = load_settings(
        {
            "SAEE_REQUIRE_RBAC_ROLE": "true",
            "SAEE_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
        }
    )
    require(protected.ready is True, "configured RBAC preview guard is ready")
    protected_payload = protected.readiness_payload()
    require(protected_payload["rbac_role_required"] is True, "role required true")
    require(protected_payload["rbac_policy_path_configured"] is True, "policy configured true")
    require(protected_payload["preview_rbac_available"] is True, "preview RBAC available")
    require(protected_payload["rbac_available"] is False, "production RBAC remains false")
    require(protected_payload["production_auth_ready"] is False, "production auth remains false")

    read_decision = evaluate_rbac_route(str(TEMPLATE_PATH), "GET /experiment", "viewer")
    require(read_decision.allowed is True, "viewer can read experiment list")
    require(read_decision.required_permission == "experiment:read", "read permission expected")
    require(validate_rbac_role("GET /experiment", "viewer", protected) == "viewer", "viewer allowed")
    require(
        validate_rbac_role("POST /experiment/run", "evaluator_operator", protected)
        == "evaluator_operator",
        "evaluator operator can run experiment",
    )
    expect_http_error("POST /experiment/run", None, protected, 401)
    expect_http_error("POST /experiment/run", "viewer", protected, 403)
    expect_http_error("GET /operations/alerts", "viewer", protected, 403)
    require(
        validate_rbac_role("GET /operations/alerts", "support_operator", protected)
        == "support_operator",
        "support operator can read operations alerts",
    )

    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(protected_payload[flag] is False, f"{flag} must remain false")

    print(
        "SAEE_RBAC_PREVIEW_ENFORCEMENT_SMOKE: PASS "
        "default_disabled=true preview_rbac_available=true "
        "viewer_run_denied=true production_auth_ready=false"
    )


if __name__ == "__main__":
    main()
