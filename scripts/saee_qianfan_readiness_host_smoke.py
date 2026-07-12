#!/usr/bin/env python3
"""Offline fake-provider validation for the Qianfan readiness host."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_qianfan_readiness_host import (
    FIXTURES,
    MCP_TO_PROVIDER,
    PUBLIC_MCP_TOOLS,
    ReadinessHostError,
    extract_call,
    run_roundtrip,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_QIANFAN_READINESS_HOST_SMOKE: FAIL " + message)


class FakeQianfan:
    model = "fake-qianfan-readiness-model"

    def __init__(self, fixture: dict) -> None:
        self.fixture = fixture
        self.calls = 0
        self.seen_tools: list[str] = []

    def chat(self, messages, tools, tool_choice):
        self.calls += 1
        if self.calls == 1:
            self.seen_tools = [item["function"]["name"] for item in tools]
            return {
                "id": "fake-tool-response",
                "choices": [{
                    "message": {"role": "assistant", "content": "", "tool_calls": [{"id": "call-1", "type": "function", "function": {"name": "saee_evaluate_agent_run", "arguments": json.dumps(self.fixture, ensure_ascii=False)}}]},
                    "finish_reason": "tool_calls"
                }]
            }
        result = json.loads(messages[-1]["content"])
        return {
            "id": "fake-final-response",
            "choices": [{"message": {"role": "assistant", "content": f"readiness={result['readiness']} score={result['score']} deployment_authorized=false production_ready=false"}, "finish_reason": "stop"}]
        }


def fake_response(name: str, arguments: dict) -> dict:
    return {"choices": [{"message": {"tool_calls": [{"id": "x", "type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}]}}]}


def main() -> None:
    results = []
    for scenario, path in FIXTURES.items():
        fixture = json.loads(path.read_text(encoding="utf-8"))
        provider = FakeQianfan(fixture)
        result = run_roundtrip(provider, fixture)
        require(result["status"] == "pass", scenario)
        require(provider.calls == 2, "provider rounds")
        require(provider.seen_tools == ["saee_evaluate_agent_run", "saee_evaluate_evidence"], "provider aliases")
        require(result["public_mcp_tools"] == list(PUBLIC_MCP_TOOLS), "MCP tools")
        require(result["function_alias_crosswalk"] == MCP_TO_PROVIDER, "crosswalk")
        require(result["truth_boundary"]["external_provider_network_used"] is False, "fake network boundary")
        require(result["truth_boundary"]["production_ready"] is False, "production boundary")
        results.append(result)
    customer, coding = results
    require(customer["result"]["readiness"] == "conditional", "customer readiness")
    require(coding["result"]["readiness"] == "replan", "coding readiness")

    fixture = json.loads(FIXTURES["customer-service"].read_text(encoding="utf-8"))
    negatives = [
        ("unknown", fake_response("describe_saee", fixture), "provider_tool_not_allowed"),
        ("tampered", fake_response("saee_evaluate_agent_run", {**fixture, "task": "tampered"}), "provider_fixture_mismatch"),
    ]
    for _, response, expected in negatives:
        try:
            extract_call(response, fixture)
        except ReadinessHostError as exc:
            require(str(exc) == expected, expected)
        else:
            raise SystemExit("SAEE_QIANFAN_READINESS_HOST_SMOKE: FAIL negative accepted")
    print(
        "SAEE_QIANFAN_READINESS_HOST_SMOKE: PASS provider_simulations=2 provider_rounds=4 "
        "mcp_tools=2 alias_crosswalk=2 negative_cases=2 external_provider_network=false "
        "external_world_actions=0 marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
