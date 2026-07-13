#!/usr/bin/env python3
"""Smoke-test the controlled-preview request contract and fail-closed edges."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from saee_controlled_preview_request_validator import validate_request

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "agent-interface/examples/controlled-preview-request.json"
SCHEMA = ROOT / "agent-interface/schemas/controlled-preview-request.schema.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CONTROLLED_PREVIEW_REQUEST_SMOKE: FAIL " + message)


def main() -> None:
    request = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    require(schema["additionalProperties"] is False, "schema must reject unknown fields")
    require(validate_request(request) == [], "valid example")

    reserved = copy.deepcopy(request)
    reserved["experiment_id"] = "tenant:tenant-b:exp"
    require(validate_request(reserved), "reserved prefix must be rejected")

    forbidden = copy.deepcopy(request)
    forbidden["api_key"] = "redacted"
    require(validate_request(forbidden), "secret field must be rejected")

    execution = copy.deepcopy(request)
    execution["boundaries"]["external_system_execution"] = True
    require(validate_request(execution), "external execution must be rejected")

    mismatch = copy.deepcopy(request)
    mismatch["evaluation_mode"] = "synthetic_descriptor_simulation"
    require(validate_request(mismatch), "mode/input mismatch must be rejected")

    print(
        "SAEE_CONTROLLED_PREVIEW_REQUEST_SMOKE: PASS "
        "valid=true reserved_prefix_rejected=true forbidden_field_rejected=true "
        "external_execution_rejected=true production_ready=false "
        "customer_validated=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
