"""Request audit logging for the SAEE MVP API shell.

This module records public-shell request metadata only. It does not record
request bodies, response bodies, API keys, Authorization headers, cookies, or
private-core internals.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.public_input_contract import (
    CONTROL_CHARACTER_PATTERN,
    contains_high_confidence_credential,
)

if TYPE_CHECKING:
    from fastapi import Request, Response


FORBIDDEN_AUDIT_FIELDS = {
    "authorization",
    "cookie",
    "x-saee-api-key",
    "x-saee-tenant-id",
    "request_body",
    "response_body",
    "raw_tenant_id",
    "private_core_exposed",
    "private_core_internals",
    "fitness_logic",
    "selection_logic",
    "mutation_logic",
    "lineage_internals",
}
AUDIT_REQUIRED_FIELDS = {
    "timestamp",
    "request_id",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "audit_scope",
    "body_recorded",
    "credentials_recorded",
    "private_core_recorded",
    "tenant_boundary_checked",
    "tenant_id_present",
    "tenant_id_hash_recorded",
    "tenant_id_raw_recorded",
}
AUDIT_OPTIONAL_FIELDS = {
    "client_host",
    "error_type",
    "tenant_id_hash",
    "tenant_id_hash_algorithm",
}
TENANT_AUDIT_METADATA_FIELDS = {
    "tenant_boundary_checked",
    "tenant_id_present",
    "tenant_id_hash_recorded",
    "tenant_id_raw_recorded",
    "tenant_id_hash",
    "tenant_id_hash_algorithm",
}
SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")
AUDIT_ROUTE_TEMPLATES = {
    "/health",
    "/ready",
    "/experiment",
    "/experiment/create",
    "/experiment/run",
    "/experiment/{experiment_id}/stability",
    "/experiment/{experiment_id}/failures",
    "/experiment/{experiment_id}/ranking",
    "/experiment/{experiment_id}/survival",
    "/operations/telemetry",
    "/operations/alerts",
    "/readiness/support",
    "/readiness/data-operations",
    "/readiness/operations",
    "/readiness/privacy-security",
    "/readiness/legal",
    "/readiness/billing-pricing",
    "/readiness/vulnerability",
    "/commercial/status",
    "/__unmatched__",
}


def _safe_audit_text(value: Any, *, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError(f"request audit {field} is invalid")
    if CONTROL_CHARACTER_PATTERN.search(value) or contains_high_confidence_credential(value):
        raise ValueError(f"request audit {field} is invalid")
    return value


def validate_tenant_audit_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    unknown = set(metadata) - TENANT_AUDIT_METADATA_FIELDS
    if unknown:
        raise ValueError("tenant audit metadata contains unknown fields")
    normalized = dict(metadata)
    for field in (
        "tenant_boundary_checked",
        "tenant_id_present",
        "tenant_id_hash_recorded",
        "tenant_id_raw_recorded",
    ):
        if field in normalized and type(normalized[field]) is not bool:
            raise ValueError(f"tenant audit metadata {field} must be boolean")
    if normalized.get("tenant_id_raw_recorded") is not False:
        raise ValueError("tenant audit metadata must not record a raw tenant ID")
    hash_recorded = normalized.get("tenant_id_hash_recorded") is True
    if hash_recorded:
        tenant_hash = normalized.get("tenant_id_hash")
        if not isinstance(tenant_hash, str) or not SHA256_HEX_PATTERN.fullmatch(tenant_hash):
            raise ValueError("tenant audit metadata hash must be SHA-256 hex")
        if normalized.get("tenant_id_hash_algorithm") != "sha256":
            raise ValueError("tenant audit metadata hash algorithm must be sha256")
        if normalized.get("tenant_id_present") is not True:
            raise ValueError("tenant audit metadata hash requires tenant presence")
    elif "tenant_id_hash" in normalized or "tenant_id_hash_algorithm" in normalized:
        raise ValueError("tenant audit metadata hash fields require hash_recorded=true")
    return normalized


def validate_request_audit_event(event: dict[str, Any]) -> None:
    if not isinstance(event, dict):
        raise ValueError("request audit event must be an object")
    fields = set(event)
    if fields - (AUDIT_REQUIRED_FIELDS | AUDIT_OPTIONAL_FIELDS):
        raise ValueError("request audit event contains unknown fields")
    if AUDIT_REQUIRED_FIELDS - fields:
        raise ValueError("request audit event is missing required fields")
    try:
        datetime.fromisoformat(str(event["timestamp"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("request audit timestamp is invalid") from exc
    _safe_audit_text(event["request_id"], field="request_id", maximum=128)
    method = _safe_audit_text(event["method"], field="method", maximum=16)
    if method != method.upper():
        raise ValueError("request audit method must be uppercase")
    path = _safe_audit_text(event["path"], field="path", maximum=1024)
    if path not in AUDIT_ROUTE_TEMPLATES:
        raise ValueError("request audit path must be a registered route template")
    if type(event["status_code"]) is not int or not 100 <= event["status_code"] <= 599:
        raise ValueError("request audit status_code is invalid")
    duration = event["duration_ms"]
    if isinstance(duration, bool) or not isinstance(duration, (int, float)):
        raise ValueError("request audit duration_ms is invalid")
    if not math.isfinite(float(duration)) or float(duration) < 0:
        raise ValueError("request audit duration_ms is invalid")
    if event["audit_scope"] != "public_api_shell_metadata_only":
        raise ValueError("request audit scope is invalid")
    for field in (
        "body_recorded",
        "credentials_recorded",
        "private_core_recorded",
        "tenant_id_raw_recorded",
    ):
        if event[field] is not False:
            raise ValueError(f"request audit {field} must be false")
    validate_tenant_audit_metadata(
        {field: event[field] for field in TENANT_AUDIT_METADATA_FIELDS if field in event}
    )
    for field, maximum in (("client_host", 255), ("error_type", 128)):
        if field in event:
            _safe_audit_text(event[field], field=field, maximum=maximum)


def new_request_id() -> str:
    return f"req-{uuid4().hex}"


def build_request_audit_event(
    *,
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    client_host: str | None = None,
    error_type: str | None = None,
    tenant_audit_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 3),
        "audit_scope": "public_api_shell_metadata_only",
        "body_recorded": False,
        "credentials_recorded": False,
        "private_core_recorded": False,
        "tenant_boundary_checked": False,
        "tenant_id_present": False,
        "tenant_id_hash_recorded": False,
        "tenant_id_raw_recorded": False,
    }
    if client_host:
        event["client_host"] = client_host
    if error_type:
        event["error_type"] = error_type
    if tenant_audit_metadata:
        event.update(validate_tenant_audit_metadata(tenant_audit_metadata))
    validate_request_audit_event(event)
    return event


def tenant_audit_metadata_from_request(request: "Request") -> dict[str, Any]:
    """Return safe tenant-boundary audit metadata from request state."""

    state = getattr(request, "state", None)
    tenant_hash = getattr(state, "saee_tenant_id_hash", None)
    tenant_hash_algorithm = getattr(state, "saee_tenant_id_hash_algorithm", None)
    metadata: dict[str, Any] = {
        "tenant_boundary_checked": bool(
            getattr(state, "saee_tenant_boundary_checked", False)
        ),
        "tenant_id_present": bool(getattr(state, "saee_tenant_id_present", False)),
        "tenant_id_hash_recorded": bool(tenant_hash),
        "tenant_id_raw_recorded": False,
    }
    if tenant_hash:
        metadata["tenant_id_hash"] = str(tenant_hash)
        metadata["tenant_id_hash_algorithm"] = str(tenant_hash_algorithm or "sha256")
    return metadata


def audit_route_template(request: "Request") -> str:
    """Return a registered route template without raw URL path parameters."""

    route = request.scope.get("route") if hasattr(request, "scope") else None
    candidate = getattr(route, "path", None)
    if isinstance(candidate, str) and candidate in AUDIT_ROUTE_TEMPLATES:
        return candidate
    return "/__unmatched__"


def write_request_audit_event(
    event: dict[str, Any],
    settings: SaeeBackendSettings = SETTINGS,
) -> bool:
    if not settings.request_audit_enabled:
        return False
    validate_request_audit_event(event)
    serialized = json.dumps(event, sort_keys=True)
    lowered = serialized.lower()
    leaked = [field for field in FORBIDDEN_AUDIT_FIELDS if field in lowered]
    if leaked:
        raise ValueError("request audit event contains forbidden fields: " + ", ".join(leaked))
    path = Path(settings.request_audit_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(serialized + "\n")
    return True


async def request_audit_middleware(request: "Request", call_next) -> "Response":
    request_id = new_request_id()
    request.state.saee_request_id = request_id
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started) * 1000
        write_request_audit_event(
            build_request_audit_event(
                request_id=request_id,
                method=request.method,
                path=audit_route_template(request),
                status_code=500,
                duration_ms=duration_ms,
                client_host=request.client.host if request.client else None,
                error_type="unhandled_exception",
                tenant_audit_metadata=tenant_audit_metadata_from_request(request),
            )
        )
        raise

    duration_ms = (perf_counter() - started) * 1000
    response.headers["X-SAEE-Request-ID"] = request_id
    write_request_audit_event(
        build_request_audit_event(
            request_id=request_id,
            method=request.method,
            path=audit_route_template(request),
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_host=request.client.host if request.client else None,
            tenant_audit_metadata=tenant_audit_metadata_from_request(request),
        )
    )
    return response
