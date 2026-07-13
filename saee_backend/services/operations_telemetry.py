"""Local operations telemetry snapshot for the SAEE public API shell.

This module reads local request-audit JSONL metadata and builds an aggregate
snapshot for pre-commercial operations review. It does not tail logs, export
metrics, call external services, inspect request bodies, inspect credentials,
or inspect private core.
"""

from __future__ import annotations

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from statistics import median
from typing import Any

from saee_backend.config import SETTINGS, SaeeBackendSettings


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 3)
    rank = (len(ordered) - 1) * percentile
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    value = ordered[lower] * (1 - weight) + ordered[upper] * weight
    return round(value, 3)


def _load_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    if not path.exists():
        return [], 0
    events: list[dict[str, Any]] = []
    invalid_lines = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                invalid_lines += 1
                continue
            if isinstance(parsed, dict):
                events.append(parsed)
            else:
                invalid_lines += 1
    return events, invalid_lines


def _status_is_error(status_code: object) -> bool:
    try:
        return int(status_code or 0) >= 500
    except (TypeError, ValueError):
        return False


def _tenant_hash(tenant_id: str) -> str:
    return sha256(tenant_id.encode("utf-8")).hexdigest()


def build_operations_telemetry_snapshot(
    settings: SaeeBackendSettings = SETTINGS,
    tenant_id: str | None = None,
) -> dict[str, object]:
    """Return an aggregate telemetry snapshot from local request metadata."""

    path = Path(settings.request_audit_path)
    events, invalid_lines = _load_events(path)
    tenant_filter_applied = tenant_id is not None
    if tenant_id is not None:
        tenant_hash = _tenant_hash(tenant_id)
        events = [event for event in events if event.get("tenant_id_hash") == tenant_hash]
    durations = [
        float(event["duration_ms"])
        for event in events
        if isinstance(event.get("duration_ms"), (int, float))
    ]
    status_counts = Counter(str(event.get("status_code", "unknown")) for event in events)
    method_counts = Counter(str(event.get("method", "unknown")) for event in events)
    path_counts = Counter(str(event.get("path", "unknown")) for event in events)
    error_count = sum(1 for event in events if _status_is_error(event.get("status_code")))
    tenant_boundary_checked_count = sum(
        1 for event in events if event.get("tenant_boundary_checked") is True
    )
    tenant_scoped_request_count = sum(
        1 for event in events if event.get("tenant_id_present") is True
    )
    tenant_id_hash_recorded_count = sum(
        1 for event in events if event.get("tenant_id_hash_recorded") is True
    )
    tenant_id_raw_recorded_count = sum(
        1 for event in events if event.get("tenant_id_raw_recorded") is True
    )
    latest_timestamp = max((str(event.get("timestamp", "")) for event in events), default=None)

    return {
        "telemetry_type": "local_public_shell_operations_telemetry",
        "telemetry_source": "request_audit_jsonl",
        "request_audit_enabled": settings.request_audit_enabled,
        "request_audit_path": str(path),
        "audit_file_exists": path.exists(),
        "local_operations_telemetry_available": True,
        "operations_telemetry_external_export_available": False,
        "local_alert_policy_available": True,
        "external_alert_delivery_available": False,
        "production_monitoring_available": False,
        "alerting_available": False,
        "incident_response_runbook_available": True,
        "production_operations_ready": False,
        "event_count": len(events),
        "invalid_line_count": invalid_lines,
        "tenant_scope_filter_applied": tenant_filter_applied,
        "tenant_id_raw_filter_recorded": False,
        "status_code_counts": dict(sorted(status_counts.items())),
        "method_counts": dict(sorted(method_counts.items())),
        "path_counts": dict(path_counts.most_common(10)),
        "error_count": error_count,
        "tenant_audit_metadata_available": True,
        "tenant_boundary_checked_count": tenant_boundary_checked_count,
        "tenant_scoped_request_count": tenant_scoped_request_count,
        "tenant_id_hash_recorded_count": tenant_id_hash_recorded_count,
        "tenant_id_raw_recorded_count": tenant_id_raw_recorded_count,
        "duration_ms_min": round(min(durations), 3) if durations else None,
        "duration_ms_median": round(median(durations), 3) if durations else None,
        "duration_ms_p95": _percentile(durations, 0.95),
        "duration_ms_max": round(max(durations), 3) if durations else None,
        "latest_timestamp": latest_timestamp,
        "body_inspected": False,
        "credentials_inspected": False,
        "private_core_inspected": False,
        "private_core_exposed": settings.private_core_exposed,
        "production_ready": settings.production_ready,
        "customer_validated": settings.customer_validated,
        "product_launched": settings.product_launched,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "next_action": "use as local pre-commercial operations snapshot only; configure real monitoring before production use",
    }
