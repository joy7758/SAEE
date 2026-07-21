"""Strict request/response facade for the local Capability Runtime Alpha."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from .capability_router import route_capability_request
from .invocation_receipt import create_invocation_receipt


ROOT = Path(__file__).resolve().parents[3]
REQUEST_SCHEMA = ROOT / "schemas/saee-capability-invocation-request.schema.v0.1.json"
RESPONSE_SCHEMA = ROOT / "schemas/saee-capability-invocation-response.schema.v0.1.json"
KNOWN_OPERATIONS = {"evaluate_rehearsal_run", "evaluate_evidence", "rehearse_agent"}
FORBIDDEN_KEY = re.compile(r"(?:api[_-]?key|access[_-]?token|secret|password|credential|chain[_-]?of[_-]?thought|hidden[_-]?reasoning)", re.I)
MAX_REQUEST_BYTES = 1_000_000
LIMITATIONS = [
    "This Runtime is local Alpha software and provides no public network service.",
    "It reuses existing fixed SAEE evaluators and does not create a new reliability or evidence evaluator.",
    "A SUCCESS status means local invocation completed; it is not task success, safety, compliance, or certification.",
    "The Runtime does not authorize deployment, permission expansion, or another external action.",
    "The Runtime accepts no customer data and performs no network, subprocess, dynamic import, or external-world execution.",
    "Invocation receipts retain metadata and digests only; they are returned inline and are not persisted.",
]
TRUTH_BOUNDARY = {
    "runtime_stage": "local_alpha",
    "network_api_available": False,
    "public_service": False,
    "standard_mcp_transport": False,
    "customer_data_used": False,
    "external_world_actions": False,
    "authorization_performed": False,
    "deployment_authorized": False,
    "production_ready": False,
}


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(FORBIDDEN_KEY.search(str(key)) or _contains_forbidden_key(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_key(child) for child in value)
    return False


def _safe_request_id(request: Any) -> str:
    if isinstance(request, dict) and isinstance(request.get("request_id"), str) and re.fullmatch(r"request:[A-Za-z0-9._:-]{1,120}", request["request_id"]):
        return request["request_id"]
    return "request:invalid"


def _safe_operation(request: Any) -> str:
    value = request.get("operation") if isinstance(request, dict) else None
    return value if value in KNOWN_OPERATIONS else "UNKNOWN"


def _valid_rfc3339(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _validate_response(response: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
    receipt_schema = json.loads((ROOT / "schemas/saee-capability-invocation-receipt.schema.v0.1.json").read_text(encoding="utf-8"))
    registry = Registry().with_resource(receipt_schema["$id"], Resource.from_contents(receipt_schema))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker(), registry=registry).iter_errors(response), key=lambda item: list(item.absolute_path))
    if errors:
        raise RuntimeError(f"Capability Runtime produced invalid response: {errors[0].message}")
    return response


def _response(request: Any, status: str, result: dict[str, Any], reason_codes: list[str]) -> dict[str, Any]:
    receipt = create_invocation_receipt(request, status, result)
    return _validate_response({
        "saee_capability_invocation_response_v0_1": True,
        "response_version": "0.1.0",
        "request_id": _safe_request_id(request),
        "capability_id": "saee.agent-reliability",
        "operation": _safe_operation(request),
        "status": status,
        "result": result,
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "limitations": list(LIMITATIONS),
        "invocation_receipt": receipt,
        "truth_boundary": dict(TRUTH_BOUNDARY),
    })


def invoke_capability(request: Any) -> dict[str, Any]:
    """Validate and invoke one local Package operation without side effects."""

    if not isinstance(request, dict):
        return _response(request, "REJECTED", {}, ["CAPABILITY_REQUEST_SCHEMA_INVALID"])
    try:
        request_bytes = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError):
        return _response(request, "REJECTED", {}, ["CAPABILITY_REQUEST_SCHEMA_INVALID"])
    if len(request_bytes) > MAX_REQUEST_BYTES:
        return _response(request, "REJECTED", {}, ["CAPABILITY_REQUEST_TOO_LARGE"])
    schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(request), key=lambda item: list(item.absolute_path))
    if errors:
        return _response(request, "REJECTED", {}, ["CAPABILITY_REQUEST_SCHEMA_INVALID"])
    if not _valid_rfc3339(request["caller_context"]["invoked_at"]):
        return _response(request, "REJECTED", {}, ["CAPABILITY_REQUEST_SCHEMA_INVALID"])
    if _contains_forbidden_key(request.get("payload")):
        return _response(request, "REJECTED", {}, ["CAPABILITY_SENSITIVE_INPUT_FORBIDDEN"])
    try:
        routed = route_capability_request(request)
    except Exception:
        return _response(request, "FAILED", {}, ["CAPABILITY_RUNTIME_FAILURE"])
    reason_codes = list(routed.get("reason_codes", []))
    return _response(request, routed["status"], routed.get("result", {}), reason_codes)
