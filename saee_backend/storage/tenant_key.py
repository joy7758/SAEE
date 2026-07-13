"""Tenant key helpers for public-shell experiment storage.

This module keeps controlled-preview tenant IDs key-safe before they enter
memory or SQLite persistence. It does not implement production multi-tenancy,
tenant authorization, billing isolation, account lifecycle, or private-core
access.
"""

from __future__ import annotations

from hashlib import sha256

from saee_backend.config import tenant_id_format_valid
from saee_backend.services.public_input_contract import validate_public_identifier

RESERVED_TENANT_STORAGE_PREFIX = "tenant:"
TENANT_STORAGE_KEY_VERSION = "v1"


def validate_experiment_id(experiment_id: str) -> str:
    """Return an experiment ID safe for the tenant-key namespace.

    The ``tenant:`` prefix is reserved for scoped storage keys. Rejecting it
    for caller-supplied IDs prevents an unscoped record from masquerading as a
    record belonging to another tenant during scoped listing.
    """

    validate_public_identifier(experiment_id, field_name="experiment_id")
    if experiment_id.startswith(RESERVED_TENANT_STORAGE_PREFIX):
        raise ValueError(
            "experiment_id uses the reserved tenant storage key prefix"
        )
    return experiment_id


def validate_storage_tenant_id(tenant_id: str | None) -> str | None:
    """Return a key-safe tenant ID or raise for unsafe direct storage calls."""

    if tenant_id is None:
        return None
    if not tenant_id_format_valid(tenant_id):
        raise ValueError(
            "tenant_id must be key-safe: start with a letter or digit, use only "
            "letters, digits, dot, underscore, or hyphen, and be at most 64 characters"
        )
    return tenant_id


def validate_required_storage_tenant_id(
    tenant_id: str | None,
    *,
    required: bool,
    allowed_tenant_ids: tuple[str, ...] = (),
) -> str | None:
    """Validate tenant scope and configured membership for storage calls.

    The allowlist is a controlled-preview configuration boundary, not caller
    identity authentication or production tenant authorization.
    """

    safe_tenant_id = validate_storage_tenant_id(tenant_id)
    safe_allowed_tenant_ids = validate_storage_tenant_allowlist(
        required=required,
        allowed_tenant_ids=allowed_tenant_ids,
    )
    if required:
        if safe_tenant_id is None:
            raise ValueError("tenant_id is required by the configured storage boundary")
        if safe_tenant_id not in safe_allowed_tenant_ids:
            raise ValueError("tenant_id is not allowed by the configured storage boundary")
    return safe_tenant_id


def validate_storage_tenant_allowlist(
    *,
    required: bool,
    allowed_tenant_ids: tuple[str, ...],
) -> tuple[str, ...]:
    """Return an immutable, key-safe allowlist snapshot or fail closed."""

    snapshot = tuple(allowed_tenant_ids)
    if not required:
        return snapshot
    if not snapshot:
        raise ValueError("tenant allowlist is required by the configured storage boundary")
    if any(not tenant_id_format_valid(tenant_id) for tenant_id in snapshot):
        raise ValueError("tenant allowlist contains an invalid tenant ID")
    return snapshot


def tenant_storage_key(experiment_id: str, tenant_id: str | None = None) -> str:
    """Return the internal storage key for an experiment and optional tenant."""

    safe_experiment_id = validate_experiment_id(experiment_id)
    safe_tenant_id = validate_storage_tenant_id(tenant_id)
    if safe_tenant_id is None:
        return safe_experiment_id
    tenant_digest = sha256(safe_tenant_id.encode("utf-8")).hexdigest()
    return (
        f"{RESERVED_TENANT_STORAGE_PREFIX}{TENANT_STORAGE_KEY_VERSION}:"
        f"{tenant_digest}:{safe_experiment_id}"
    )


def tenant_public_experiment_id(key: str, tenant_id: str | None = None) -> str | None:
    """Return the public experiment ID visible within the requested tenant scope."""

    safe_tenant_id = validate_storage_tenant_id(tenant_id)
    if safe_tenant_id is None:
        if key.startswith(RESERVED_TENANT_STORAGE_PREFIX):
            return None
        return key
    tenant_digest = sha256(safe_tenant_id.encode("utf-8")).hexdigest()
    prefix = (
        f"{RESERVED_TENANT_STORAGE_PREFIX}{TENANT_STORAGE_KEY_VERSION}:"
        f"{tenant_digest}:"
    )
    if not key.startswith(prefix):
        return None
    return key[len(prefix) :]
