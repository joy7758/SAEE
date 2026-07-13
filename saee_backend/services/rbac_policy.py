"""Local RBAC route-scope evaluation for the public SAEE API shell.

This module parses a local RBAC policy template and evaluates whether a role is
allowed to access a public-shell route scope. It does not validate identity
tokens, contact an identity provider, fetch JWKS, manage accounts, or expose
private-core internals.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FORBIDDEN_POLICY_TRUE_KEYS = {
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_identity_provider_contacted",
    "jwks_fetched",
    "tokens_validated",
    "rbac_enforced",
    "production_auth_ready",
    "production_identity_provider_available",
    "oauth_oidc_available",
    "rbac_available",
}


@dataclass(frozen=True)
class RbacRouteDecision:
    route: str
    role: str
    allowed: bool
    required_permission: str | None
    allowed_roles: tuple[str, ...]
    reason: str


class RbacPolicyError(ValueError):
    """Raised when the local RBAC policy file is missing or malformed."""


def _unique_strings(values: Any, field: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise RbacPolicyError(f"SAEE RBAC policy {field} must be a list.")
    if not allow_empty and not values:
        raise RbacPolicyError(f"SAEE RBAC policy {field} must not be empty.")
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise RbacPolicyError(f"SAEE RBAC policy {field} must contain non-empty strings.")
    normalized = tuple(value.strip() for value in values)
    if len(set(normalized)) != len(normalized):
        raise RbacPolicyError(f"SAEE RBAC policy {field} contains duplicates.")
    if "*" in normalized:
        raise RbacPolicyError(f"SAEE RBAC policy {field} must not contain wildcard entries.")
    return normalized


def validate_rbac_policy_document(data: dict[str, object]) -> dict[str, object]:
    """Validate role-permission-route consistency without enabling RBAC."""

    if any(data.get(key) is True for key in FORBIDDEN_POLICY_TRUE_KEYS):
        raise RbacPolicyError("SAEE RBAC policy contains a forbidden positive production claim.")

    roles_raw = data.get("roles")
    if not isinstance(roles_raw, list) or not roles_raw:
        raise RbacPolicyError("SAEE RBAC policy missing non-empty roles list.")
    role_permissions: dict[str, frozenset[str]] = {}
    all_permissions: set[str] = set()
    for index, item in enumerate(roles_raw):
        if not isinstance(item, dict):
            raise RbacPolicyError("SAEE RBAC role entry must be an object.")
        role = item.get("role")
        if not isinstance(role, str) or not role.strip():
            raise RbacPolicyError("SAEE RBAC role name must be a non-empty string.")
        role = role.strip()
        if role == "*":
            raise RbacPolicyError("SAEE RBAC wildcard role is forbidden.")
        if role in role_permissions:
            raise RbacPolicyError(f"SAEE RBAC policy contains duplicate role: {role}.")
        permissions = _unique_strings(item.get("permissions"), f"roles[{index}].permissions", allow_empty=True)
        role_permissions[role] = frozenset(permissions)
        all_permissions.update(permissions)

    route_scopes_raw = data.get("route_scopes")
    if not isinstance(route_scopes_raw, list) or not route_scopes_raw:
        raise RbacPolicyError("SAEE RBAC policy missing non-empty route_scopes list.")
    route_names: set[str] = set()
    role_permission_edges = 0
    for index, item in enumerate(route_scopes_raw):
        if not isinstance(item, dict):
            raise RbacPolicyError("SAEE RBAC route scope entry must be an object.")
        route = item.get("route")
        permission = item.get("required_permission")
        if not isinstance(route, str) or not route.strip():
            raise RbacPolicyError("SAEE RBAC route must be a non-empty string.")
        route = route.strip()
        if route in route_names:
            raise RbacPolicyError(f"SAEE RBAC policy contains duplicate route scope: {route}.")
        route_names.add(route)
        if not isinstance(permission, str) or not permission.strip() or permission == "*":
            raise RbacPolicyError(f"SAEE RBAC route {route} has invalid required_permission.")
        permission = permission.strip()
        allowed_roles = _unique_strings(item.get("allowed_roles"), f"route_scopes[{index}].allowed_roles")
        for role in allowed_roles:
            if role not in role_permissions:
                raise RbacPolicyError(f"SAEE RBAC route {route} references unknown role: {role}.")
            if permission not in role_permissions[role]:
                raise RbacPolicyError(
                    f"SAEE RBAC role {role} lacks required permission {permission} for {route}."
                )
            role_permission_edges += 1

    return {
        "roles": frozenset(role_permissions),
        "permissions": frozenset(all_permissions),
        "routes": frozenset(route_names),
        "role_permission_edges": role_permission_edges,
        "role_permissions": role_permissions,
    }


def _read_policy(policy_path: str) -> dict[str, object]:
    if not policy_path:
        raise RbacPolicyError("SAEE RBAC role guard is enabled but no RBAC policy path is configured.")
    path = Path(policy_path).expanduser()
    if not path.exists() or not path.is_file():
        raise RbacPolicyError("SAEE RBAC policy path does not point to a local file.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RbacPolicyError("SAEE RBAC policy file is not parseable JSON.") from exc
    if not isinstance(data, dict):
        raise RbacPolicyError("SAEE RBAC policy must be a JSON object.")
    validate_rbac_policy_document(data)
    return data


def _route_scopes(data: dict[str, object]) -> list[dict[str, object]]:
    route_scopes = data.get("route_scopes")
    if not isinstance(route_scopes, list):
        raise RbacPolicyError("SAEE RBAC policy missing route_scopes list.")
    parsed: list[dict[str, object]] = []
    for item in route_scopes:
        if not isinstance(item, dict):
            raise RbacPolicyError("SAEE RBAC route scope entry must be an object.")
        parsed.append(item)
    return parsed


def evaluate_rbac_route(
    policy_path: str,
    route_scope: str,
    role: str | None,
) -> RbacRouteDecision:
    """Evaluate a role against a public-shell route scope."""

    normalized_role = (role or "").strip()
    if not normalized_role:
        return RbacRouteDecision(
            route=route_scope,
            role="",
            allowed=False,
            required_permission=None,
            allowed_roles=(),
            reason="missing_role",
        )

    data = _read_policy(policy_path)
    for item in _route_scopes(data):
        if item.get("route") != route_scope:
            continue
        allowed_roles_raw = item.get("allowed_roles")
        if not isinstance(allowed_roles_raw, list):
            raise RbacPolicyError("SAEE RBAC route scope missing allowed_roles list.")
        allowed_roles = tuple(str(value) for value in allowed_roles_raw)
        required_permission = item.get("required_permission")
        allowed = normalized_role in allowed_roles
        return RbacRouteDecision(
            route=route_scope,
            role=normalized_role,
            allowed=allowed,
            required_permission=str(required_permission)
            if required_permission is not None
            else None,
            allowed_roles=allowed_roles,
            reason="allowed" if allowed else "role_not_allowed",
        )

    raise RbacPolicyError(f"SAEE RBAC policy has no route scope for {route_scope}.")
