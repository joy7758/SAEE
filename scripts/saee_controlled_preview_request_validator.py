#!/usr/bin/env python3
"""Validate a bounded, agent-readable SAEE controlled-preview request.

The validator only checks a file-backed request. It never stores a request,
contacts a customer, calls a provider, executes candidate code, or closes a
commercial blocker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "agent-interface/schemas/controlled-preview-request.schema.json"
EXAMPLE = ROOT / "agent-interface/examples/controlled-preview-request.json"

FORBIDDEN_KEYS = {
    "api_key", "authorization", "command", "code", "email", "message",
    "password", "path", "phone", "prompt", "raw_log", "secret", "token",
    "url", "customer_email", "customer_record", "customer_secret",
}
MODE_TO_INPUT_KIND = {
    "synthetic_descriptor_simulation": "non_executable_agent_descriptors",
    "observed_trace_bundle_evaluation": "sanitized_observed_agent_trace_bundle",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _forbidden_keys(value: Any, found: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in FORBIDDEN_KEYS:
                found.append(str(key))
            _forbidden_keys(child, found)
    elif isinstance(value, list):
        for child in value:
            _forbidden_keys(child, found)


def validate_request(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["request must be a JSON object"]
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(data)]
    found: list[str] = []
    _forbidden_keys(data, found)
    if found:
        errors.append("forbidden keys: " + ", ".join(sorted(set(found))))
    tenant_id = data.get("tenant_id")
    experiment_id = data.get("experiment_id")
    if isinstance(tenant_id, str) and tenant_id.startswith("tenant:"):
        errors.append("tenant_id uses reserved storage prefix")
    if isinstance(experiment_id, str) and experiment_id.startswith("tenant:"):
        errors.append("experiment_id uses reserved storage prefix")
    mode = data.get("evaluation_mode")
    input_data = data.get("input")
    if isinstance(mode, str) and isinstance(input_data, dict):
        expected = MODE_TO_INPUT_KIND.get(mode)
        if expected and input_data.get("kind") != expected:
            errors.append("input.kind does not match evaluation_mode")
    boundaries = data.get("boundaries")
    if isinstance(boundaries, dict):
        for key, value in boundaries.items():
            if value is not False:
                errors.append(f"boundary must remain false: {key}")
    return sorted(set(errors))


def result(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    return {
        "contract_id": "saee-controlled-preview-request-result-v0.1",
        "request_valid": not errors,
        "request_sha256": hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "errors": errors,
        "next_action": "run the selected offline SAEE evaluator only after the caller separately authorizes a controlled preview",
        "production_ready": False,
        "customer_validated": False,
        "external_system_executed": False,
        "candidate_code_executed": False,
        "blockers_closed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(EXAMPLE))
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"request_valid": False, "errors": [str(exc)]}, ensure_ascii=False))
        raise SystemExit(2) from exc
    errors = validate_request(data)
    output = result(data if isinstance(data, dict) else {}, errors)
    if args.as_json:
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    elif errors:
        print("SAEE_CONTROLLED_PREVIEW_REQUEST_VALIDATOR: FAIL " + " | ".join(errors))
    else:
        print("SAEE_CONTROLLED_PREVIEW_REQUEST_VALIDATOR: PASS request_valid=true production_ready=false blockers_closed=0")
    raise SystemExit(0 if not errors else 2)


if __name__ == "__main__":
    main()
