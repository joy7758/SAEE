"""Project Capability Runtime responses into the strict HTTP contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[3]
RESPONSE_SCHEMA = ROOT / "schemas/saee-capability-http-response.schema.v0.1.json"
RECEIPT_SCHEMA = ROOT / "schemas/saee-capability-invocation-receipt.schema.v0.1.json"
HTTP_LIMITATIONS = [
    "The HTTP Adapter listens on localhost only and is not a public API.",
    "The HTTP layer is transport only and does not add authorization, authentication, tenancy, billing, or production execution.",
]
TRUTH_BOUNDARY = {
    "runtime_stage": "local_alpha",
    "http_adapter_available": True,
    "bind_address": "127.0.0.1",
    "network_public_access": False,
    "public_service": False,
    "request_persisted": False,
    "payload_persisted": False,
    "customer_data_used": False,
    "external_world_actions": False,
    "oauth_available": False,
    "multi_tenant": False,
    "production_ready": False,
}


def build_http_response(runtime_response: dict[str, Any]) -> dict[str, Any]:
    response = {
        "saee_capability_http_response_v0_1": True,
        "http_adapter_version": "0.1.0",
        "request_id": runtime_response["request_id"],
        "capability_id": runtime_response["capability_id"],
        "operation": runtime_response["operation"],
        "status": runtime_response["status"],
        "result": runtime_response["result"],
        "reason_codes": runtime_response["reason_codes"],
        "limitations": [*runtime_response["limitations"], *HTTP_LIMITATIONS],
        "invocation_receipt": runtime_response["invocation_receipt"],
        "truth_boundary": dict(TRUTH_BOUNDARY),
    }
    schema = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    registry = Registry().with_resource(receipt["$id"], Resource.from_contents(receipt))
    Draft202012Validator(schema, registry=registry).validate(response)
    return response


def http_status_for(response: dict[str, Any], *, route_found: bool = True) -> int:
    if not route_found:
        return 404
    return {"SUCCESS": 200, "REJECTED": 400, "CONTRACT_ONLY": 501, "FAILED": 500}[response["status"]]

