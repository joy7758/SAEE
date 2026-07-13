#!/usr/bin/env python3
"""Smoke check for SAEE tenant request boundary v0.1."""

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

from saee_backend.api.security import validate_tenant_boundary, validate_tenant_id
from saee_backend.config import load_settings
from saee_backend.services.jwt_preview_auth import JwtPreviewClaims


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_TENANT_BOUNDARY_SMOKE: FAIL: {message}")


def expect_http_error(tenant_id: str | None, settings, status_code: int) -> None:
    try:
        validate_tenant_id(tenant_id, settings)
    except HTTPException as exc:
        require(exc.status_code == status_code, f"expected status {status_code}, got {exc.status_code}")
        return
    raise SystemExit(f"SAEE_TENANT_BOUNDARY_SMOKE: FAIL: expected HTTP {status_code}")


def expect_boundary_error(tenant_id: str | None, claims: JwtPreviewClaims, settings, status_code: int) -> None:
    try:
        validate_tenant_boundary(tenant_id, claims, settings)
    except HTTPException as exc:
        require(exc.status_code == status_code, f"expected status {status_code}, got {exc.status_code}")
        return
    raise SystemExit(f"SAEE_TENANT_BOUNDARY_SMOKE: FAIL: expected HTTP {status_code}")


def build_claims(tenant_id: str) -> JwtPreviewClaims:
    return JwtPreviewClaims(
        subject="preview-user",
        issuer="local",
        audience="saee",
        tenant_id=tenant_id,
        roles=("viewer",),
        expires_at=4_102_444_800,
        issued_at=1_767_225_600,
        raw_claims={},
    )


def main() -> None:
    default = load_settings({})
    require(default.require_tenant_id is False, "tenant boundary must be disabled by default")
    require(default.allowed_tenant_ids == (), "tenant allowlist must be empty by default")
    require(default.ready is True, "local default readiness must remain true")
    require(validate_tenant_id(None, default) is None, "disabled tenant boundary must allow local default")

    missing_allowlist = load_settings({"SAEE_REQUIRE_TENANT_ID": "true"})
    require(missing_allowlist.require_tenant_id is True, "tenant boundary must be configurable")
    require(missing_allowlist.allowed_tenant_ids == (), "missing allowlist must stay empty")
    require(missing_allowlist.ready is False, "required tenant boundary without allowlist must not be ready")
    expect_http_error("tenant-a", missing_allowlist, 503)

    protected = load_settings(
        {
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": "tenant-a, tenant-b",
        }
    )
    require(protected.ready is True, "tenant-protected config with allowlist must be ready")
    require(protected.allowed_tenant_ids == ("tenant-a", "tenant-b"), "tenant allowlist must parse CSV")
    require(validate_tenant_id("tenant-a", protected) == "tenant-a", "allowed tenant must pass")
    require(validate_tenant_id(" tenant-b ", protected) == "tenant-b", "tenant header must trim safely")
    expect_http_error(None, protected, 400)
    expect_http_error("tenant/a", protected, 400)
    expect_http_error("tenant:a", protected, 400)
    expect_http_error("-tenant-a", protected, 400)
    expect_http_error("tenant a", protected, 400)
    expect_http_error("tenant-x", protected, 403)

    invalid_allowlist = load_settings(
        {
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": "tenant-a,tenant/a",
        }
    )
    require(invalid_allowlist.ready is False, "invalid tenant allowlist must not be ready")
    expect_http_error("tenant-a", invalid_allowlist, 503)

    require(
        validate_tenant_boundary(None, build_claims("tenant-a"), protected) == "tenant-a",
        "preview JWT tenant_id must pass tenant boundary",
    )
    require(
        validate_tenant_boundary("tenant-a", build_claims("tenant-a"), protected) == "tenant-a",
        "matching header and preview JWT tenant_id must pass",
    )
    expect_boundary_error("tenant-b", build_claims("tenant-a"), protected, 403)
    expect_boundary_error(None, build_claims("tenant/a"), protected, 401)
    expect_boundary_error("tenant/a", build_claims("tenant-a"), protected, 400)

    payload = protected.readiness_payload()
    require(payload["tenant_boundary_available"] is True, "readiness must expose tenant boundary")
    require(payload["tenant_id_required"] is True, "readiness must expose tenant ID requirement")
    require(payload["tenant_allowlist_configured"] is True, "readiness must expose tenant allowlist")
    require(
        payload["preview_storage_scoped_by_tenant"] is True,
        "readiness must expose preview tenant storage scoping",
    )
    require(payload["tenant_storage_isolated"] is False, "tenant storage isolation must remain false")
    require(payload["tenant_billing_isolated"] is False, "tenant billing isolation must remain false")
    require(payload["multi_tenant_production_ready"] is False, "multi-tenant production ready must remain false")
    require(payload["production_ready"] is False, "production ready must remain false")
    require(payload["private_core_exposed"] is False, "private core exposed must remain false")

    doc = (ROOT / "phase_b_product/commercial_readiness/TENANT_BOUNDARY_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_TENANT_BOUNDARY_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("tenant_boundary_v0_1: true" in doc, "tenant boundary doc missing state")
    require(
        "preview_storage_scoped_by_tenant: true" in doc,
        "tenant doc missing preview storage scope",
    )
    require("tenant_storage_isolated: false" in doc, "tenant doc must not claim storage isolation")
    require("multi_tenant_production_ready: false" in doc, "tenant doc must not claim production")
    require("answer: conditional" in gate, "tenant gate must remain conditional")
    require("recommend_public_launch_now: false" in gate, "tenant gate must not recommend launch")

    print(
        "SAEE_TENANT_BOUNDARY_SMOKE: PASS "
        "tenant_boundary_available=true "
        "default_required=false "
        "allowlist_guard=true "
        "tenant_id_format_guard=true "
        "preview_storage_scoped_by_tenant=true "
        "tenant_storage_isolated=false "
        "multi_tenant_production_ready=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
