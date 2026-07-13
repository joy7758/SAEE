"""Optional request guard for the public SAEE MVP API shell."""

from __future__ import annotations

import os
from hashlib import sha256

from fastapi import Header, HTTPException, Request

from saee_backend.config import SETTINGS, SaeeBackendSettings, tenant_id_format_valid
from saee_backend.services.jwt_preview_auth import (
    JwtPreviewAuthError,
    JwtPreviewClaims,
    validate_authorization_header,
)
from saee_backend.services.rbac_policy import RbacPolicyError, evaluate_rbac_route
from saee_backend.services.authorization_context import (
    AuthorizedPrincipalContext,
    issue_authorized_principal_context,
)


TENANT_ID_FORMAT_DETAIL = (
    "X-SAEE-Tenant-ID must start with a letter or digit, use only letters, "
    "digits, dot, underscore, or hyphen, and be at most 64 characters."
)
TENANT_AUDIT_HASH_ALGORITHM = "sha256"
def tenant_id_audit_hash(tenant_id: str) -> str:
    """Return a non-reversible audit hash for a public-shell tenant ID."""

    return sha256(tenant_id.encode("utf-8")).hexdigest()


def _mark_tenant_audit_state(
    request: Request | None,
    *,
    checked: bool,
    tenant_id: str | None,
) -> None:
    """Store tenant audit metadata on request.state without raw tenant IDs."""

    if request is None:
        return
    state = getattr(request, "state", None)
    if state is None:
        return

    setattr(state, "saee_tenant_boundary_checked", checked)
    setattr(state, "saee_tenant_id_present", bool(tenant_id))
    setattr(state, "saee_tenant_id_raw_recorded", False)
    if tenant_id:
        setattr(state, "saee_tenant_id_hash", tenant_id_audit_hash(tenant_id))
        setattr(state, "saee_tenant_id_hash_algorithm", TENANT_AUDIT_HASH_ALGORITHM)
    else:
        setattr(state, "saee_tenant_id_hash", None)
        setattr(state, "saee_tenant_id_hash_algorithm", None)


def invalid_allowed_tenant_ids(settings: SaeeBackendSettings) -> tuple[str, ...]:
    """Return configured tenant IDs that cannot be used safely as public keys."""

    return tuple(
        tenant_id for tenant_id in settings.allowed_tenant_ids if not tenant_id_format_valid(tenant_id)
    )


def require_api_key(x_saee_api_key: str | None = Header(default=None, alias="X-SAEE-API-Key")) -> None:
    """Require an API key only when explicitly enabled by environment.

    Local demo mode remains open by default. Commercial or shared preview
    deployments can set `SAEE_REQUIRE_API_KEY=true` and `SAEE_API_KEY=<secret>`
    without changing endpoint shapes or exposing private-core internals.
    """

    if not SETTINGS.require_api_key:
        return

    expected = os.environ.get("SAEE_API_KEY", "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="SAEE API key protection is enabled but SAEE_API_KEY is not configured.",
        )
    if x_saee_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid SAEE API key.")


def validate_tenant_id(
    tenant_id: str | None,
    settings: SaeeBackendSettings = SETTINGS,
) -> str | None:
    """Validate the optional public-shell tenant request boundary.

    This is a request-envelope guard for controlled previews. It is not
    tenant-isolated storage, billing isolation, or production multi-tenancy.
    """

    if not settings.require_tenant_id:
        return None

    if not settings.allowed_tenant_ids:
        raise HTTPException(
            status_code=503,
            detail="SAEE tenant boundary is enabled but SAEE_ALLOWED_TENANT_IDS is not configured.",
        )
    if invalid_allowed_tenant_ids(settings):
        raise HTTPException(
            status_code=503,
            detail="SAEE_ALLOWED_TENANT_IDS contains tenant IDs with invalid format.",
        )

    normalized = (tenant_id or "").strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Missing X-SAEE-Tenant-ID.")
    if not tenant_id_format_valid(normalized):
        raise HTTPException(status_code=400, detail=TENANT_ID_FORMAT_DETAIL)
    if normalized not in settings.allowed_tenant_ids:
        raise HTTPException(status_code=403, detail="Tenant is not allowed for this SAEE preview.")
    return normalized


def _request_authorization_header(request: Request | None) -> str | None:
    if request is None:
        return None
    headers = getattr(request, "headers", None)
    if headers is None or not hasattr(headers, "get"):
        return None
    return headers.get("authorization") or headers.get("Authorization")


def _preview_claims_from_request(
    request: Request | None,
    authorization: str | None,
    settings: SaeeBackendSettings = SETTINGS,
) -> JwtPreviewClaims | None:
    if not settings.require_jwt_preview_auth:
        return None

    cached = None
    if request is not None:
        state = getattr(request, "state", None)
        cached = getattr(state, "saee_jwt_preview_claims", None)
    if isinstance(cached, JwtPreviewClaims):
        return cached

    try:
        claims = validate_authorization_header(
            authorization or _request_authorization_header(request),
            settings,
        )
    except JwtPreviewAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    if request is not None:
        state = getattr(request, "state", None)
        if state is not None:
            setattr(state, "saee_jwt_preview_claims", claims)
    return claims


def require_jwt_preview_auth(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> JwtPreviewClaims | None:
    """Require a signed preview JWT only when explicitly enabled.

    This checks `Authorization: Bearer <token>` for controlled-preview
    authentication on the public API shell. It is not production OAuth/OIDC,
    SSO, JWKS validation, account lifecycle, or a production-auth readiness
    claim.
    """

    return _preview_claims_from_request(request, authorization)


def validate_tenant_boundary(
    tenant_id: str | None,
    claims: JwtPreviewClaims | None,
    settings: SaeeBackendSettings = SETTINGS,
) -> str | None:
    """Validate tenant boundary from either preview JWT claims or header."""

    if claims is None:
        return validate_tenant_id(tenant_id, settings)

    token_tenant_id = claims.tenant_id.strip()
    header_tenant_id = (tenant_id or "").strip()
    if invalid_allowed_tenant_ids(settings):
        raise HTTPException(
            status_code=503,
            detail="SAEE_ALLOWED_TENANT_IDS contains tenant IDs with invalid format.",
        )
    if not tenant_id_format_valid(token_tenant_id):
        raise HTTPException(status_code=401, detail="Preview JWT tenant_id has invalid format.")
    if header_tenant_id and not tenant_id_format_valid(header_tenant_id):
        raise HTTPException(status_code=400, detail=TENANT_ID_FORMAT_DETAIL)
    if header_tenant_id and header_tenant_id != token_tenant_id:
        raise HTTPException(
            status_code=403,
            detail="X-SAEE-Tenant-ID does not match the preview JWT tenant_id.",
        )
    if settings.allowed_tenant_ids and token_tenant_id not in settings.allowed_tenant_ids:
        raise HTTPException(status_code=403, detail="Tenant is not allowed for this SAEE preview.")
    return token_tenant_id


def require_tenant_boundary(
    request: Request,
    x_saee_tenant_id: str | None = Header(default=None, alias="X-SAEE-Tenant-ID"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_saee_role: str | None = Header(default=None, alias="X-SAEE-Role"),
) -> str | AuthorizedPrincipalContext | None:
    _mark_tenant_audit_state(request, checked=True, tenant_id=None)
    claims = _preview_claims_from_request(request, authorization)
    tenant_id = validate_tenant_boundary(x_saee_tenant_id, claims)
    _mark_tenant_audit_state(request, checked=True, tenant_id=tenant_id)
    if SETTINGS.require_bound_tenant_authorization:
        if claims is None or tenant_id is None or not SETTINGS.ready:
            raise HTTPException(
                status_code=503,
                detail="Bound tenant authorization chain is not completely configured.",
            )
        route = request.scope.get("route") if hasattr(request, "scope") else None
        route_path = getattr(route, "path", "")
        route_scope = f"{request.method.upper()} {route_path}" if route_path else ""
        if not route_scope:
            raise HTTPException(status_code=503, detail="Canonical route scope is unavailable.")
        requested_role = (x_saee_role or "").strip()
        if requested_role and requested_role not in claims.roles:
            raise HTTPException(
                status_code=403,
                detail="X-SAEE-Role is not present in the preview JWT roles.",
            )
        granted_role = (
            validate_rbac_role(route_scope, requested_role)
            if requested_role
            else validate_rbac_roles(route_scope, claims.roles)
        )
        if not granted_role:
            raise HTTPException(status_code=403, detail="No signed role was granted.")
        try:
            decision = evaluate_rbac_route(
                SETTINGS.rbac_policy_path,
                route_scope,
                granted_role,
            )
        except RbacPolicyError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        if not decision.allowed or not decision.required_permission:
            raise HTTPException(status_code=403, detail="Route permission was not granted.")
        context = issue_authorized_principal_context(
            subject=claims.subject,
            tenant_id=tenant_id,
            roles=claims.roles,
            route_scope=route_scope,
            granted_role=granted_role,
            granted_permission=decision.required_permission,
            capability_secret=os.environ.get("SAEE_PREVIEW_JWT_HS256_SECRET", "").strip(),
        )
        setattr(request.state, "saee_authorized_principal", context)
        if route_path.startswith("/experiment"):
            return context
        return tenant_id
    return tenant_id


def validate_rbac_roles(
    route_scope: str,
    roles: tuple[str, ...],
    settings: SaeeBackendSettings = SETTINGS,
) -> str | None:
    """Validate at least one preview JWT role against a route scope."""

    if not (settings.require_rbac_role or settings.require_jwt_preview_auth):
        return None
    if not roles:
        raise HTTPException(status_code=401, detail="Preview JWT has no roles.")

    last_denied_role = ""
    try:
        for role in roles:
            decision = evaluate_rbac_route(settings.rbac_policy_path, route_scope, role)
            if decision.allowed:
                return decision.role
            last_denied_role = decision.role
    except RbacPolicyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    detail = "SAEE preview JWT roles are not allowed for this route."
    if last_denied_role:
        detail = f"SAEE role is not allowed for this route: {last_denied_role}."
    raise HTTPException(status_code=403, detail=detail)


def validate_rbac_role(
    route_scope: str,
    role: str | None,
    settings: SaeeBackendSettings = SETTINGS,
) -> str | None:
    """Validate the optional public-shell RBAC role boundary.

    This is controlled-preview route authorization over public report routes.
    It is not production OIDC, SSO, token validation, account lifecycle, or a
    production-auth readiness claim.
    """

    if not settings.require_rbac_role:
        return None

    try:
        decision = evaluate_rbac_route(settings.rbac_policy_path, route_scope, role)
    except RbacPolicyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if decision.reason == "missing_role":
        raise HTTPException(status_code=401, detail="Missing X-SAEE-Role.")
    if not decision.allowed:
        raise HTTPException(status_code=403, detail="SAEE role is not allowed for this route.")
    return decision.role


def require_rbac_route(route_scope: str):
    def dependency(
        request: Request,
        x_saee_role: str | None = Header(default=None, alias="X-SAEE-Role"),
        authorization: str | None = Header(default=None, alias="Authorization"),
    ) -> str | None:
        if SETTINGS.require_jwt_preview_auth:
            claims = _preview_claims_from_request(request, authorization)
            assert claims is not None
            requested_role = (x_saee_role or "").strip()
            if requested_role:
                if requested_role not in claims.roles:
                    raise HTTPException(
                        status_code=403,
                        detail="X-SAEE-Role is not present in the preview JWT roles.",
                    )
                return validate_rbac_role(route_scope, requested_role)
            return validate_rbac_roles(route_scope, claims.roles)
        return validate_rbac_role(route_scope, x_saee_role)

    return dependency
