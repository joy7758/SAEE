#!/usr/bin/env python3
"""Smoke test for the bounded agent support case contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from saee_agent_support_case_validator import validate_request

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "agent-interface/examples/agent-support-case-request.json"
SCHEMA = ROOT / "agent-interface/schemas/agent-support-case-request.schema.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_AGENT_SUPPORT_CASE_SMOKE: FAIL " + message)


def main() -> None:
    request = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    require(schema["additionalProperties"] is False, "unknown fields rejected")
    require(validate_request(request) == [], "valid request")
    url = copy.deepcopy(request)
    url["summary"] = "请查看 https://example.invalid/secret"
    require(validate_request(url), "URL text rejected")
    secret = copy.deepcopy(request)
    secret["api_key"] = "not-allowed"
    require(validate_request(secret), "secret field rejected")
    dispatch = copy.deepcopy(request)
    dispatch["boundaries"]["external_dispatch"] = True
    require(validate_request(dispatch), "external dispatch rejected")
    print("SAEE_AGENT_SUPPORT_CASE_SMOKE: PASS valid=true url_rejected=true secret_rejected=true dispatch_rejected=true support_status=owner_support_channel_required blockers_closed=0")


if __name__ == "__main__":
    main()
