"""Validate local HTTP envelopes and delegate them to Capability Runtime."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.capability_runtime import invoke_capability

from .http_response_builder import build_http_response, http_status_for


ROOT = Path(__file__).resolve().parents[3]
REQUEST_SCHEMA = ROOT / "schemas/saee-capability-http-request.schema.v0.1.json"
ROUTES = {
    "/capabilities/evaluate-rehearsal-run": "evaluate_rehearsal_run",
    "/capabilities/evaluate-evidence": "evaluate_evidence",
    "/capabilities/rehearse-agent": "rehearse_agent",
}


def _time_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _runtime_request(body: Any, operation: str, invoked_at: str) -> dict[str, Any]:
    source = body if isinstance(body, dict) else {}
    return {
        "request_id": source.get("request_id", "request:http-invalid"),
        "capability_id": source.get("capability_id", "saee.agent-reliability"),
        "operation": operation,
        "payload": source.get("payload", {}),
        "caller_context": {
            "caller_id": "caller:http-localhost",
            "caller_type": "LOCAL_CLI",
            "invoked_at": invoked_at,
            "customer_data_included": False,
            "network_access_requested": False,
            "external_world_action_requested": False,
        },
    }


def process_http_request(path: str, body: Any, *, invoked_at: str | None = None) -> tuple[int, dict[str, Any]]:
    timestamp = invoked_at or _time_now()
    expected_operation = ROUTES.get(path)
    route_found = expected_operation is not None
    schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
    schema_valid = isinstance(body, dict) and not list(Draft202012Validator(schema).iter_errors(body))
    if not route_found:
        runtime = invoke_capability(_runtime_request(body, "http_route_not_found", timestamp))
    elif not schema_valid:
        runtime = invoke_capability(_runtime_request(body, "http_request_invalid", timestamp))
    elif body["operation"] != expected_operation:
        runtime = invoke_capability(_runtime_request(body, "http_operation_mismatch", timestamp))
    else:
        runtime = invoke_capability(_runtime_request(body, expected_operation, timestamp))
    response = build_http_response(runtime)
    return http_status_for(response, route_found=route_found), response
