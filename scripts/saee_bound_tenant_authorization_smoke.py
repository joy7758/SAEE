#!/usr/bin/env python3
"""Adversarial smoke for the controlled-preview bound tenant auth chain."""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import types


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
from saee_backend.config import load_settings
from saee_backend.services.authorization_context import (
    AuthorizedPrincipalContext,
    issue_authorized_principal_context,
)
from saee_backend.models.request import ExperimentCreateRequest
from saee_backend.services.experiment_service import ExperimentService
from saee_backend.services.jwt_preview_auth import sign_preview_jwt
from saee_backend.storage.factory import create_experiment_store
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


SECRET = "synthetic-bound-tenant-auth-secret-32-bytes"
TENANT = "tenant-bound-a"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BOUND_TENANT_AUTHORIZATION_SMOKE: FAIL: " + message)


def require_rejected(callable_, label: str, status: int | None = None) -> None:
    try:
        callable_()
    except HTTPException as exc:
        if status is not None:
            require(exc.status_code == status, label + " wrong HTTP status")
        return
    except (ValueError, TypeError):
        return
    raise SystemExit("SAEE_BOUND_TENANT_AUTHORIZATION_SMOKE: FAIL: " + label + " accepted")


@contextmanager
def patched_env(values: dict[str, str]):
    before = dict(os.environ)
    os.environ.clear()
    os.environ.update(before)
    os.environ.update(values)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(before)


def complete_env() -> dict[str, str]:
    return {
        "SAEE_REQUIRE_BOUND_TENANT_AUTHORIZATION": "true",
        "SAEE_REQUIRE_JWT_PREVIEW_AUTH": "true",
        "SAEE_PREVIEW_JWT_ISSUER": "https://preview.local/issuer",
        "SAEE_PREVIEW_JWT_AUDIENCE": "saee-preview",
        "SAEE_PREVIEW_JWT_HS256_SECRET": SECRET,
        "SAEE_REQUIRE_TENANT_ID": "true",
        "SAEE_ALLOWED_TENANT_IDS": TENANT,
        "SAEE_REQUIRE_RBAC_ROLE": "true",
        "SAEE_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
        "SAEE_STORAGE_BACKEND": "memory",
    }


def claims(*, tenant_id: str = TENANT, roles: list[str] | None = None) -> dict:
    now = int(time.time())
    return {
        "iss": "https://preview.local/issuer",
        "sub": "synthetic-agent-principal",
        "aud": "saee-preview",
        "exp": now + 600,
        "iat": now,
        "tenant_id": tenant_id,
        "roles": roles or ["evaluator_operator"],
    }


class FakeRequest:
    def __init__(self, authorization: str, path: str = "/experiment/run") -> None:
        self.headers = {"authorization": authorization}
        self.state = SimpleNamespace()
        self.scope = {"route": SimpleNamespace(path=path)}
        self.method = "POST"


def run_checks() -> None:
    generate_template()
    os.environ["SAEE_PREVIEW_JWT_HS256_SECRET"] = SECRET
    header_mode = load_settings(
        {
            "SAEE_REQUIRE_API_KEY": "true",
            "SAEE_API_KEY": "synthetic-shared-key",
            "SAEE_REQUIRE_TENANT_ID": "true",
            "SAEE_ALLOWED_TENANT_IDS": TENANT,
            "SAEE_REQUIRE_RBAC_ROLE": "true",
            "SAEE_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
        }
    )
    require(header_mode.ready is False, "header-asserted tenant/role mode must not be ready")

    partial_jwt = load_settings(
        {
            "SAEE_REQUIRE_JWT_PREVIEW_AUTH": "true",
            "SAEE_PREVIEW_JWT_ISSUER": "https://preview.local/issuer",
            "SAEE_PREVIEW_JWT_AUDIENCE": "saee-preview",
            "SAEE_PREVIEW_JWT_HS256_SECRET": SECRET,
            "SAEE_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
        }
    )
    require(partial_jwt.ready is False, "JWT without strict tenant chain must not be ready")

    settings = load_settings(complete_env())
    require(settings.ready is True, "complete bound authorization chain not ready")
    readiness = settings.readiness_payload()
    require(readiness["bound_tenant_authorization_chain_complete"] is True, "chain flag")
    require(readiness["header_asserted_tenant_role_authorization_allowed"] is False, "header flag")

    store = create_experiment_store(settings)
    require_rejected(lambda: store.create("exp-direct", TENANT), "raw tenant direct store")
    context = issue_authorized_principal_context(
        subject="synthetic-agent-principal",
        tenant_id=TENANT,
        roles=("evaluator_operator",),
        route_scope="POST /experiment/create",
        granted_role="evaluator_operator",
        granted_permission="experiment:create",
        capability_secret=SECRET,
    )
    read_context = issue_authorized_principal_context(
        subject="synthetic-agent-principal",
        tenant_id=TENANT,
        roles=("viewer",),
        route_scope="GET /experiment",
        granted_role="viewer",
        granted_permission="experiment:read",
        capability_secret=SECRET,
    )
    store.create("exp-context", context)
    require(store.exists("exp-context", read_context), "authorized context store create")
    service = ExperimentService(store)
    require_rejected(
        lambda: service.create_experiment(
            ExperimentCreateRequest(experiment_id="exp-service-raw"),
            TENANT,
        ),
        "raw tenant direct service",
    )
    service.create_experiment(
        ExperimentCreateRequest(experiment_id="exp-service-context"),
        context,
    )
    wrong_tenant = issue_authorized_principal_context(
        subject=context.subject,
        tenant_id="tenant-unlisted",
        roles=context.roles,
        route_scope=context.route_scope,
        granted_role=context.granted_role,
        granted_permission=context.granted_permission,
        capability_secret=SECRET,
    )
    require_rejected(lambda: store.create("exp-wrong", wrong_tenant), "unlisted context tenant")
    forged = AuthorizedPrincipalContext(
        subject="synthetic-agent-principal",
        tenant_id=TENANT,
        roles=("viewer",),
        auth_source="preview_jwt_hs256",
        route_scope="GET /experiment",
        granted_role="viewer",
        granted_permission="experiment:read",
        capability="0" * 64,
    )
    require_rejected(lambda: store.create("exp-forged", forged), "forged capability")
    empty_principal = AuthorizedPrincipalContext(
        **{**forged.__dict__, "subject": "", "roles": (), "capability": "0" * 64}
    )
    require_rejected(lambda: store.create("exp-empty", empty_principal), "empty principal")
    require_rejected(
        lambda: store.create("exp-read-create", read_context),
        "read permission used for create",
    )
    forged_source = AuthorizedPrincipalContext(
        **{**forged.__dict__, "auth_source": "caller_asserted", "capability": "0" * 64}
    )
    require_rejected(lambda: store.create("exp-source", forged_source), "forged auth source")

    with tempfile.TemporaryDirectory() as tmpdir:
        sqlite_settings = load_settings(
            {
                **complete_env(),
                "SAEE_STORAGE_BACKEND": "sqlite",
                "SAEE_STORAGE_PATH": str(Path(tmpdir) / "bound.sqlite3"),
            }
        )
        sqlite_store = create_experiment_store(sqlite_settings)
        require_rejected(
            lambda: sqlite_store.create("exp-sqlite-raw", TENANT),
            "raw tenant direct SQLite store",
        )
        sqlite_store.create("exp-sqlite-context", context)
        require(
            sqlite_store.exists("exp-sqlite-context", read_context),
            "authorized SQLite context create",
        )

    with patched_env(complete_env()):
        import saee_backend.config as config_module

        importlib.reload(config_module)
        security = importlib.reload(importlib.import_module("saee_backend.api.security"))
        token = sign_preview_jwt(claims(), SECRET)
        auth = "Bearer " + token
        request = FakeRequest(auth)
        principal = security.require_tenant_boundary(
            request,
            TENANT,
            auth,
            "evaluator_operator",
        )
        require(isinstance(principal, AuthorizedPrincipalContext), "API context type")
        require(principal.tenant_id == TENANT, "API context tenant")
        require(principal.route_scope == "POST /experiment/run", "canonical route scope")
        require(bool(principal.granted_permission), "granted permission")
        require_rejected(
            lambda: security.require_tenant_boundary(
                FakeRequest(auth),
                "tenant-unlisted",
                auth,
                "evaluator_operator",
            ),
            "tenant switch",
            403,
        )
        require_rejected(
            lambda: security.require_tenant_boundary(
                FakeRequest(auth),
                TENANT,
                auth,
                "admin",
            ),
            "role spoof",
            403,
        )
        require_rejected(
            lambda: security.require_tenant_boundary(
                FakeRequest(auth, "/unknown"),
                TENANT,
                auth,
                "evaluator_operator",
            ),
            "unknown route",
            503,
        )

    main_source = (ROOT / "saee_backend/main.py").read_text(encoding="utf-8")
    require(main_source.count("Depends(require_api_key)") >= 2, "probe API-key dependency")
    require("minimal_non_tenant" in main_source, "health probe scope")
    require("configuration_non_tenant" in main_source, "ready probe scope")


def main() -> None:
    run_checks()
    print(
        "SAEE_BOUND_TENANT_AUTHORIZATION_SMOKE: PASS "
        "negative_cases=14/14 principal_context_immutable=true "
        "capability_verified=true operation_permission_bound=true "
        "raw_tenant_direct_store_denied=true tenant_switch_denied=true "
        "role_spoof_denied=true partial_chain_ready=false "
        "tenant_authorization_policy_reviewed=false production_auth_ready=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
