"""Immutable controlled-preview authorization context.

The context binds a locally verified principal to one tenant and one canonical
route decision. Accepted sources are the existing preview JWT verifier and the
provider-neutral offline OIDC/JWKS verifier. Neither source is evidence that a
production identity provider or production OIDC flow is available.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field


ALLOWED_AUTH_SOURCES = frozenset(
    {
        "preview_jwt_hs256",
        "oidc_jwks_offline_verified",
    }
)


@dataclass(frozen=True)
class AuthorizedPrincipalContext:
    subject: str
    tenant_id: str
    roles: tuple[str, ...]
    auth_source: str
    route_scope: str
    granted_role: str
    granted_permission: str
    capability: str = field(repr=False)


TenantAuthorization = str | AuthorizedPrincipalContext | None


def tenant_id_from_authorization(value: TenantAuthorization) -> str | None:
    if isinstance(value, AuthorizedPrincipalContext):
        return value.tenant_id
    return value


def _capability_payload(context: AuthorizedPrincipalContext) -> bytes:
    return json.dumps(
        {
            "auth_source": context.auth_source,
            "granted_permission": context.granted_permission,
            "granted_role": context.granted_role,
            "roles": list(context.roles),
            "route_scope": context.route_scope,
            "subject": context.subject,
            "tenant_id": context.tenant_id,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _capability(secret: str, context: AuthorizedPrincipalContext) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        b"saee-bound-tenant-authorization-v1\x00" + _capability_payload(context),
        hashlib.sha256,
    ).hexdigest()


def issue_authorized_principal_context(
    *,
    subject: str,
    tenant_id: str,
    roles: tuple[str, ...],
    route_scope: str,
    granted_role: str,
    granted_permission: str,
    capability_secret: str,
    auth_source: str = "preview_jwt_hs256",
) -> AuthorizedPrincipalContext:
    if not isinstance(capability_secret, str) or len(capability_secret) < 32:
        raise ValueError("authorization capability secret is not configured securely")
    if auth_source not in ALLOWED_AUTH_SOURCES:
        raise ValueError("authorization context source is invalid")
    unsigned = AuthorizedPrincipalContext(
        subject=subject,
        tenant_id=tenant_id,
        roles=roles,
        auth_source=auth_source,
        route_scope=route_scope,
        granted_role=granted_role,
        granted_permission=granted_permission,
        capability="",
    )
    return AuthorizedPrincipalContext(
        **{
            **unsigned.__dict__,
            "capability": _capability(capability_secret, unsigned),
        }
    )


def validate_authorized_principal_context(
    context: AuthorizedPrincipalContext,
    *,
    capability_secret: str,
    allowed_tenant_ids: tuple[str, ...],
    required_permissions: frozenset[str],
) -> str:
    if not capability_secret:
        raise ValueError("authorization capability secret is not configured")
    if not context.subject.strip() or not context.tenant_id.strip():
        raise ValueError("authorized principal subject and tenant are required")
    if not context.roles or any(not role.strip() for role in context.roles):
        raise ValueError("authorized principal roles are required")
    if context.granted_role not in context.roles:
        raise ValueError("granted role is not present in signed roles")
    if context.auth_source not in ALLOWED_AUTH_SOURCES:
        raise ValueError("authorization context source is invalid")
    if context.tenant_id not in allowed_tenant_ids:
        raise ValueError("authorization context tenant is not allowed")
    if context.granted_permission not in required_permissions:
        raise ValueError("authorization context permission does not allow this operation")
    if not context.route_scope.startswith(("GET /", "POST /")):
        raise ValueError("authorization context route scope is invalid")
    expected = _capability(capability_secret, context)
    if not hmac.compare_digest(context.capability, expected):
        raise ValueError("authorization context capability is invalid")
    return context.tenant_id
