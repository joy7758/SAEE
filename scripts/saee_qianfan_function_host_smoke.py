#!/usr/bin/env python3
"""Offline acceptance and safety checks for the Qianfan function host."""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import saee_mcp_stdio as mcp_server
import saee_qianfan_function_host as host


BUNDLE = host.load_json(ROOT / "agent-interface/examples/observed-trace-bundle.json")
EXPECTED_RECEIPT = host.load_json(ROOT / "agent-interface/examples/observed-trace-receipt.json")
RESULT_SCHEMA = host.load_json(ROOT / "agent-interface/schemas/qianfan-host-result.schema.json")
FINAL_TEXT = (
    "evaluation_mode=observed_trace_bundle_evaluation；"
    "recommended_agent=candidate-alpha；第一名 score=0.719476；"
    "production_ready=false；customer_validated=false；"
    "trace_authenticity_verified=false。"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_QIANFAN_FUNCTION_HOST_SMOKE: FAIL " + message)


def tool_response(name: str, arguments: object, call_id: str) -> dict:
    argument_text = arguments if isinstance(arguments, str) else json.dumps(arguments, ensure_ascii=False, separators=(",", ":"))
    return {
        "id": "fake-" + call_id,
        "model": "fake-qianfan-tool-model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {"name": name, "arguments": argument_text},
                        }
                    ],
                },
                "finish_reason": "tool_calls",
                "flag": 0,
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }


def final_response(content: str = FINAL_TEXT) -> dict:
    return {
        "id": "fake-final",
        "model": "fake-qianfan-tool-model",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
                "flag": 0,
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }


class FakeClient:
    model = "fake-qianfan-tool-model"

    def __init__(self, *, duplicate_id: bool = False, wrong_final: bool = False) -> None:
        self.audit: list[dict] = []
        self.duplicate_id = duplicate_id
        self.wrong_final = wrong_final
        self.payloads: list[dict] = []

    def chat(self, messages: list[dict], tools: list[dict], tool_choice: object, round_number: int) -> dict:
        self.payloads.append({"messages": messages, "tools": tools, "tool_choice": tool_choice})
        self.audit.append(
            {
                "round": round_number,
                "provider_response_id": f"fake-{round_number}",
                "offered_tools": [tool["function"]["name"] for tool in tools],
                "authorization_header_recorded": False,
                "prompt_recorded": False,
                "raw_tool_arguments_recorded": False,
                "raw_tool_results_recorded": False,
            }
        )
        if round_number == 1:
            return tool_response("describe_saee", "", "call-1")
        if round_number == 2:
            return tool_response("compare_observed_traces", BUNDLE, "call-1" if self.duplicate_id else "call-2")
        return final_response("错误总结" if self.wrong_final else FINAL_TEXT)


def expect_error(fn: object, error_type: str) -> None:
    try:
        fn()  # type: ignore[operator]
    except host.HostError as exc:
        require(exc.error_type == error_type, f"expected {error_type}, got {exc.error_type}")
        return
    raise SystemExit("SAEE_QIANFAN_FUNCTION_HOST_SMOKE: FAIL expected " + error_type)


def main() -> None:
    sentinel = "SENTINEL_QIANFAN_SECRET_MUST_NOT_LEAK"
    previous_key = os.environ.get(host.API_KEY_ENV)
    os.environ[host.API_KEY_ENV] = sentinel
    try:
        successful = []
        first_client: FakeClient | None = None
        for index in range(10):
            client = FakeClient()
            result = host.run_host(client)
            if index == 0:
                first_client = client
            require(result["status"] == "success", "fake provider success")
            require(result["mcp"]["tools"] == list(host.ALLOWED_TOOLS), "fixed tool list")
            require(result["mcp"]["tool_call_sequence"] == list(host.ALLOWED_TOOLS), "tool order")
            require(result["security"]["mcp_child_received_api_key"] is False, "key reached MCP child")
            require(result["truth_boundary"]["production_ready"] is False, "production boundary")
            require(not list(Draft202012Validator(RESULT_SCHEMA).iter_errors(result)), "host result schema")
            serialized = json.dumps(result, ensure_ascii=False)
            require(sentinel not in serialized, "sentinel in host result")
            successful.append(result)

        require(first_client is not None, "first fake client")
        require(len(first_client.payloads) == 3, "provider rounds")
        for payload in first_client.payloads:
            require([tool["function"]["name"] for tool in payload["tools"]] == list(host.ALLOWED_TOOLS), "provider tool list")
        first_tool_schemas = {
            tool["function"]["name"]: tool["function"]["parameters"]
            for tool in first_client.payloads[0]["tools"]
        }
        canonical_schemas = {tool["name"]: tool["inputSchema"] for tool in mcp_server.tool_definitions()}
        require(first_tool_schemas == canonical_schemas, "provider schemas must come from MCP")
        without_schema = copy.deepcopy(BUNDLE)
        without_schema.pop("$schema", None)
        accepted_call, _ = host.extract_tool_call(
            tool_response("compare_observed_traces", without_schema, "schema-locator-omitted"),
            "compare_observed_traces",
            BUNDLE,
        )
        require(accepted_call["id"] == "schema-locator-omitted", "optional schema locator normalization")
        numeric_spelling = copy.deepcopy(BUNDLE)
        numeric_spelling["candidates"][0]["context"]["metric_min"] = 0
        numeric_spelling["candidates"][0]["context"]["metric_max"] = 1
        numeric_spelling["candidates"][0]["runs"][0]["steps"][0]["failure_severity"] = 0
        numeric_call, _ = host.extract_tool_call(
            tool_response("compare_observed_traces", numeric_spelling, "numeric-spelling"),
            "compare_observed_traces",
            BUNDLE,
        )
        require(numeric_call["id"] == "numeric-spelling", "JSON number spelling normalization")

        for result in successful:
            require(result["verification"]["request_sha256"] == EXPECTED_RECEIPT["request_sha256"], "request hash drift")
            require(result["verification"]["content_sha256"] == EXPECTED_RECEIPT["content_sha256"], "content hash drift")
            require(result["verification"]["recommended_agent"] == "candidate-alpha", "winner drift")
            require(result["verification"]["ranking_score"] == 0.719476, "score drift")
        receipt_schema = mcp_server.tool_definitions()[1]["outputSchema"]
        require(not list(Draft202012Validator(receipt_schema).iter_errors(EXPECTED_RECEIPT)), "receipt schema")

        negative_count = 0
        expect_error(lambda: host.extract_tool_call(tool_response("run_agent", {}, "x"), "describe_saee", {}), "tool_not_allowed")
        negative_count += 1
        expect_error(lambda: host.extract_tool_call(tool_response("describe_saee", "not-json", "x"), "describe_saee", {}), "tool_arguments_invalid")
        negative_count += 1
        for field in ("path", "url", "command", "prompt", "message", "code", "secret"):
            altered = copy.deepcopy(BUNDLE)
            altered[field] = "forbidden"
            expect_error(
                lambda value=altered: host.extract_tool_call(
                    tool_response("compare_observed_traces", value, "x"),
                    "compare_observed_traces",
                    BUNDLE,
                ),
                "tool_arguments_invalid",
            )
            negative_count += 1
        deep: dict = {"leaf": True}
        for _ in range(70):
            deep = {"nested": deep}
        expect_error(
            lambda: host.extract_tool_call(tool_response("compare_observed_traces", deep, "x"), "compare_observed_traces", BUNDLE),
            "tool_arguments_invalid",
        )
        negative_count += 1
        expect_error(lambda: host.run_host(FakeClient(duplicate_id=True)), "provider_protocol_error")
        negative_count += 1
        expect_error(lambda: host.run_host(FakeClient(wrong_final=True)), "provider_protocol_error")
        negative_count += 1
        expect_error(lambda: host.QianfanClient("", host.DEFAULT_MODEL), "configuration_error")
        negative_count += 1
        for error_type, status, retryable in (("provider_http_error", 401, False), ("provider_http_error", 429, True), ("provider_timeout", None, True)):
            error = host.HostError(error_type, "safe", exit_code=3, retryable=retryable, http_status=status)
            value = host.error_result(error, True)
            require(value["error"]["type"] == error_type, "typed provider error")
            require(value["error"]["retryable"] is retryable, "provider retryability")
            require(sentinel not in json.dumps(value), "sentinel in error result")
            negative_count += 1

        source = (ROOT / "scripts/saee_qianfan_function_host.py").read_text(encoding="utf-8")
        for forbidden in ("shell=True", "eval(", "exec(", "import importlib", "saee_core_private", "--api-key", "--base-url", "--command", "--mcp-server"):
            require(forbidden not in source, f"forbidden source capability {forbidden}")
        require(source.count(host.ENDPOINT) == 1, "endpoint must be fixed once")
        require(sentinel not in source, "sentinel in source")
        require(negative_count == 16, f"negative count {negative_count}")
        print(
            "SAEE_QIANFAN_FUNCTION_HOST_SMOKE: PASS sessions=10 tools=2 "
            "provider_rounds=3 cli_mcp_host_hash_match=10/10 receipt_schema_errors=0 "
            "negative_cases=16/16 secret_leaks=0 mcp_child_key=false "
            "shell=false candidate_execution=false production_ready=false"
        )
    finally:
        if previous_key is None:
            os.environ.pop(host.API_KEY_ENV, None)
        else:
            os.environ[host.API_KEY_ENV] = previous_key


if __name__ == "__main__":
    main()
