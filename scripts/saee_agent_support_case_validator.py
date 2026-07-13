#!/usr/bin/env python3
"""Fail-closed validation for a sanitized, agent-readable support case."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "agent-interface/schemas/agent-support-case-request.schema.json"
EXAMPLE = ROOT / "agent-interface/examples/agent-support-case-request.json"
FORBIDDEN_KEYS = {"api_key", "bank", "card", "code", "email", "header", "log", "password", "phone", "secret", "token", "url", "webhook"}
SUSPICIOUS_TEXT = re.compile(r"https?://|www\.|[A-Za-z0-9_+.-]+@[A-Za-z0-9.-]+|(?:sk-|bce-v|AKIA)[A-Za-z0-9_-]+|\b(?:SELECT|INSERT|DROP|curl|python3|npm)\b", re.I)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def forbidden(value: Any, found: list[str], path: str = "request") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                found.append(f"{path}.{key}")
            forbidden(child, found, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            forbidden(child, found, f"{path}[{index}]")
    elif isinstance(value, str) and SUSPICIOUS_TEXT.search(value):
        found.append(f"{path}:sensitive_or_executable_text")


def validate_request(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["request must be an object"]
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(data)]
    found: list[str] = []
    forbidden(data, found)
    if found:
        errors.append("forbidden support fields or text: " + ", ".join(sorted(set(found))))
    if isinstance(data.get("summary"), str) and ("\n" in data["summary"] or "\r" in data["summary"]):
        errors.append("summary must be one line")
    for key, value in (data.get("boundaries") or {}).items():
        if value is not False:
            errors.append(f"boundary must remain false: {key}")
    return sorted(set(errors))


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
    result = {
        "contract_id": "saee-agent-support-case-response-v0.1",
        "request_valid": not errors,
        "case_sha256": hashlib.sha256(canonical(data).encode("utf-8")).hexdigest(),
        "support_status": "owner_support_channel_required",
        "external_dispatch_performed": False,
        "customer_contacted": False,
        "production_ready": False,
        "blockers_closed": 0,
        "errors": errors,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif errors:
        print("SAEE_AGENT_SUPPORT_CASE_VALIDATOR: FAIL " + " | ".join(errors))
    else:
        print("SAEE_AGENT_SUPPORT_CASE_VALIDATOR: PASS request_valid=true support_status=owner_support_channel_required external_dispatch_performed=false blockers_closed=0")
    raise SystemExit(0 if not errors else 2)


if __name__ == "__main__":
    main()
