#!/usr/bin/env python3
"""Smoke check for controlled-preview signed JWT authentication."""

from __future__ import annotations

import importlib
import os
import sys
import time
import types
from contextlib import contextmanager
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
else:
    from fastapi import HTTPException

from saee_backend.config import load_settings
from saee_backend.services.jwt_preview_auth import (
    JwtPreviewAuthError,
    sign_preview_jwt,
    validate_authorization_header,
    validate_preview_jwt,
)
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


SECRET = "local-preview-secret-for-smoke-only"
ISSUER = "https://preview-idp.example.invalid/"
AUDIENCE = "saee-controlled-preview"
TENANT_ID = "tenant-alpha"


class FakeRequest:
    def __init__(self, authorization: str | None = None):
        self.headers = {}
        if authorization:
            self.headers["authorization"] = authorization
        self.state = types.SimpleNamespace()


@contextmanager
def patched_env(values: dict[str, str]):
    previous = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_JWT_PREVIEW_AUTH_SMOKE: FAIL: " + message)


def expect_http_error(fn, status_code: int, message: str) -> None:
    try:
        fn()
    except HTTPException as exc:
        require(exc.status_code == status_code, f"{message}: expected {status_code}, got {exc.status_code}")
        return
    raise SystemExit("SAEE_JWT_PREVIEW_AUTH_SMOKE: FAIL: expected HTTP error: " + message)


def expect_jwt_error(fn, message: str) -> None:
    try:
        fn()
    except JwtPreviewAuthError:
        return
    raise SystemExit("SAEE_JWT_PREVIEW_AUTH_SMOKE: FAIL: expected JWT error: " + message)


def claims_payload(*, roles: list[str], tenant_id: str = TENANT_ID, aud: str = AUDIENCE) -> dict[str, object]:
    now = int(time.time())
    return {
        "iss": ISSUER,
        "sub": "preview-user-001",
        "aud": aud,
        "exp": now + 3600,
        "iat": now - 10,
        "tenant_id": tenant_id,
        "roles": roles,
    }


def configured_env() -> dict[str, str]:
    return {
        "SAEE_REQUIRE_JWT_PREVIEW_AUTH": "true",
        "SAEE_PREVIEW_JWT_ISSUER": ISSUER,
        "SAEE_PREVIEW_JWT_AUDIENCE": AUDIENCE,
        "SAEE_PREVIEW_JWT_HS256_SECRET": SECRET,
        "SAEE_REQUIRE_TENANT_ID": "true",
        "SAEE_ALLOWED_TENANT_IDS": TENANT_ID,
        "SAEE_REQUIRE_RBAC_ROLE": "true",
        "SAEE_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
    }


def reload_security_module():
    import saee_backend.config as config_module

    importlib.reload(config_module)
    security_module = importlib.import_module("saee_backend.api.security")
    return importlib.reload(security_module)


def main() -> None:
    generate_template()

    default = load_settings({})
    require(default.require_jwt_preview_auth is False, "JWT preview disabled by default")
    default_payload = default.readiness_payload()
    require(default_payload["jwt_preview_auth_required"] is False, "default JWT preview not required")
    require(default_payload["jwt_preview_auth_available"] is False, "default JWT preview unavailable")
    require(default_payload["jwt_preview_production_oidc"] is False, "JWT preview not production OIDC")
    require(default_payload["production_auth_ready"] is False, "production auth remains false")

    missing = load_settings({"SAEE_REQUIRE_JWT_PREVIEW_AUTH": "true"})
    require(missing.require_jwt_preview_auth is True, "JWT preview configurable")
    require(missing.ready is False, "JWT preview missing config is not ready")
    require(
        missing.auth_mode == "jwt_preview_required_unconfigured",
        "missing config auth mode expected",
    )

    with patched_env(configured_env()):
        configured = load_settings()
        payload = configured.readiness_payload()
        require(configured.ready is True, "configured JWT preview should be ready")
        require(configured.auth_mode == "jwt_preview", "configured auth mode must be jwt_preview")
        require(payload["jwt_preview_auth_available"] is True, "JWT preview available")
        require(payload["jwt_preview_uses_local_hs256"] is True, "JWT preview uses local HS256")
        require(payload["jwt_preview_production_oidc"] is False, "JWT preview is not production OIDC")
        require(payload["oauth_oidc_available"] is False, "OAuth/OIDC remains false")
        require(payload["rbac_available"] is False, "production RBAC remains false")
        require(payload["production_auth_ready"] is False, "production auth remains false")

        token = sign_preview_jwt(claims_payload(roles=["evaluator_operator"]), SECRET)
        claims = validate_preview_jwt(token, configured)
        require(claims.tenant_id == TENANT_ID, "tenant claim should be normalized")
        require(claims.roles == ("evaluator_operator",), "role claim should be normalized")
        require(
            validate_authorization_header("Bearer " + token, configured).subject == "preview-user-001",
            "Authorization bearer validation should pass",
        )
        expect_jwt_error(
            lambda: validate_preview_jwt(
                sign_preview_jwt(claims_payload(roles=["evaluator_operator"], aud="wrong-audience"), SECRET),
                configured,
            ),
            "wrong audience",
        )
        expect_jwt_error(
            lambda: validate_preview_jwt(
                sign_preview_jwt(claims_payload(roles=["evaluator_operator"]), "wrong-secret"),
                configured,
            ),
            "wrong signature",
        )

        security = reload_security_module()
        auth_header = "Bearer " + token
        request = FakeRequest(auth_header)
        require(
            security.require_jwt_preview_auth(request, auth_header).tenant_id == TENANT_ID,
            "security dependency should accept valid bearer token",
        )
        require(
            security.require_tenant_boundary(request, TENANT_ID, auth_header) == TENANT_ID,
            "tenant boundary should accept matching token tenant",
        )
        expect_http_error(
            lambda: security.require_tenant_boundary(request, "tenant-beta", auth_header),
            403,
            "tenant mismatch",
        )
        run_dependency = security.require_rbac_route("POST /experiment/run")
        require(
            run_dependency(request, None, auth_header) == "evaluator_operator",
            "JWT role should allow experiment run",
        )
        expect_http_error(
            lambda: run_dependency(request, "viewer", auth_header),
            403,
            "X-SAEE-Role cannot choose role missing from token",
        )

        viewer_token = sign_preview_jwt(claims_payload(roles=["viewer"]), SECRET)
        viewer_request = FakeRequest("Bearer " + viewer_token)
        expect_http_error(
            lambda: run_dependency(viewer_request, None, "Bearer " + viewer_token),
            403,
            "viewer cannot run experiment",
        )
        read_dependency = security.require_rbac_route("GET /experiment")
        require(
            read_dependency(viewer_request, None, "Bearer " + viewer_token) == "viewer",
            "viewer can read experiment list",
        )
        expect_http_error(
            lambda: security.require_jwt_preview_auth(FakeRequest(None), None),
            401,
            "missing Authorization rejected",
        )

    print(
        "SAEE_JWT_PREVIEW_AUTH_SMOKE: PASS "
        "default_off=true jwt_preview_available=true "
        "viewer_run_denied=true production_auth_ready=false"
    )


if __name__ == "__main__":
    main()
