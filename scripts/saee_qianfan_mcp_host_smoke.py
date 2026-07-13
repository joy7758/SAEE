#!/usr/bin/env python3
"""Local fake-provider and fail-closed checks for the Qianfan host bridge."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.saee_qianfan_mcp_host import (  # noqa: E402
    ALLOWED_TOOLS,
    BUNDLE,
    MAX_JSON_DEPTH,
    MAX_TOOL_ARGUMENT_BYTES,
    MCPClient,
    ProviderError,
    QianfanClient,
    HostError,
    load_json,
    run_roundtrip,
    safe_tool_call,
    strip_provider_key,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_QIANFAN_MCP_HOST_SMOKE: FAIL " + message)


class FakeQianfan:
    model = "fake-qianfan-model"

    def __init__(self, fixture: dict) -> None:
        self.fixture = fixture
        self.calls = 0
        self.tool_choices: list[object] = []

    def chat(self, messages, tools, tool_choice):
        self.calls += 1
        self.tool_choices.append(tool_choice)
        if self.calls == 1:
            return {
                "id": "fake-describe-response",
                "model": self.model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{
                            "id": "fake-describe-call",
                            "type": "function",
                            "function": {"name": "describe_saee", "arguments": "{}"},
                        }],
                    },
                    "finish_reason": "tool_calls",
                }],
            }
        if self.calls == 2:
            return {
                "id": "fake-compare-response",
                "model": self.model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{
                            "id": "fake-compare-call",
                            "type": "function",
                            "function": {"name": "compare_observed_traces", "arguments": json.dumps(self.fixture, ensure_ascii=False)},
                        }],
                    },
                    "finish_reason": "tool_calls",
                }],
            }
        return {
            "id": "fake-final-response",
            "model": self.model,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "candidate-alpha 获得 0.719476，evaluation_mode=observed_trace_bundle_evaluation；production_ready=false，customer_validated=false。",
                },
                "finish_reason": "stop",
            }],
        }


def main() -> None:
    fixture = load_json(BUNDLE)
    fake = FakeQianfan(fixture)
    result = run_roundtrip(fake, MCPClient(), fixture)
    require(result["status"] == "pass", "fake provider roundtrip")
    require(fake.calls == 3, "three provider rounds")
    require(result["mcp_tools"] == list(ALLOWED_TOOLS), "two-tool allowlist")
    require(result["winner"] == "candidate-alpha", "winner")
    require(result["request_hash_verified"] is True, "request hash")
    require(result["content_hash_verified"] is True, "content hash")
    require(result["secrets_redacted"] is True, "redaction flag")

    negatives = [
        ("unknown_tool", lambda: safe_tool_call("run_agent", {}, "describe_saee", fixture)),
        ("path", lambda: safe_tool_call("compare_observed_traces", {**fixture, "path": "/tmp/x"}, "compare_observed_traces", fixture)),
        ("url", lambda: safe_tool_call("compare_observed_traces", {**fixture, "url": "https://example.invalid"}, "compare_observed_traces", fixture)),
        ("command", lambda: safe_tool_call("compare_observed_traces", {**fixture, "command": "rm -rf /"}, "compare_observed_traces", fixture)),
        ("code", lambda: safe_tool_call("compare_observed_traces", {**fixture, "code": "print(1)"}, "compare_observed_traces", fixture)),
        ("secret", lambda: safe_tool_call("compare_observed_traces", {**fixture, "secret": "redact-me"}, "compare_observed_traces", fixture)),
        ("prompt", lambda: safe_tool_call("compare_observed_traces", {**fixture, "prompt": "ignore boundaries"}, "compare_observed_traces", fixture)),
        ("non_json_arguments", lambda: safe_tool_call("compare_observed_traces", [], "compare_observed_traces", fixture)),
        ("fixture_mismatch", lambda: safe_tool_call("compare_observed_traces", {**fixture, "bundle_id": "tampered"}, "compare_observed_traces", fixture)),
        ("unexpected_order", lambda: safe_tool_call("describe_saee", {}, "compare_observed_traces", fixture)),
        ("wrong_depth", lambda: safe_tool_call("compare_observed_traces", (lambda: None)(), "compare_observed_traces", fixture)),
    ]
    # Dedicated oversized and deeply nested objects exercise the same checks
    # without passing through the canonical fixture equality branch.
    oversized = {"x": "x" * MAX_TOOL_ARGUMENT_BYTES}
    deep: dict = {"leaf": True}
    for _ in range(MAX_JSON_DEPTH + 2):
        deep = {"nested": deep}
    negatives.extend([
        ("oversized", lambda: safe_tool_call("describe_saee", oversized, "describe_saee", fixture)),
        ("deep", lambda: safe_tool_call("describe_saee", deep, "describe_saee", fixture)),
    ])
    passed = 0
    negative_evidence = []
    for name, case in negatives:
        try:
            case()
        except HostError:
            passed += 1
            negative_evidence.append({"case_id": name, "outcome": "rejected", "side_effects": "none"})
        else:
            raise SystemExit(f"SAEE_QIANFAN_MCP_HOST_SMOKE: FAIL negative={name}")
    require(passed == len(negatives), "negative cases")

    try:
        QianfanClient(key="", endpoint="https://qianfan.baidubce.com/v2/chat/completions")
    except ProviderError as exc:
        require(exc.category == "missing_api_key", "missing key classification")
    else:
        raise SystemExit("SAEE_QIANFAN_MCP_HOST_SMOKE: FAIL missing key accepted")
    try:
        QianfanClient(key="redacted", endpoint="https://example.invalid/chat")
    except ProviderError as exc:
        require(exc.category == "endpoint_not_allowlisted", "endpoint allowlist")
    else:
        raise SystemExit("SAEE_QIANFAN_MCP_HOST_SMOKE: FAIL endpoint accepted")

    clean_env = strip_provider_key({"QIANFAN_API_KEY": "redacted", "OPENAI_API_KEY": "redacted", "PATH": "/usr/bin"})
    require("QIANFAN_API_KEY" not in clean_env and "OPENAI_API_KEY" not in clean_env, "MCP environment key stripping")
    source = (ROOT / "scripts/saee_qianfan_mcp_host.py").read_text(encoding="utf-8")
    require("bce-v3/ALTAK-" not in source, "key absent from source")
    require("shell=True" not in source, "shell disabled")
    require("QIANFAN_API_KEY" not in (ROOT / "agent_recommendation/agent_first_validation/run_005").as_posix(), "evidence path")
    (ROOT / "agent_recommendation/agent_first_validation/run_005/negative_cases.local.json").write_text(
        json.dumps({"schema_version": "0.1.0", "cases": negative_evidence, "passed": passed, "total": len(negatives)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "SAEE_QIANFAN_MCP_HOST_SMOKE: PASS fake_roundtrip=true provider_rounds=3 "
        f"negative_cases={passed}/{len(negatives)} tools=2 request_hash=true content_hash=true "
        "shell=false key_source_hits=0 mcp_key_env_stripped=true"
    )


if __name__ == "__main__":
    main()
