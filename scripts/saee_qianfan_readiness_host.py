#!/usr/bin/env python3
"""Bounded Qianfan function-calling host for the SAEE readiness MCP product.

The provider sees underscore-safe function aliases. The host maps them to the
canonical two MCP names and accepts only a checked-in synthetic fixture. No
model-generated path, URL, command, code, secret, or customer record is allowed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import select
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.qianfan_client import QianfanClient, QianfanProviderError, canonical_json, sha256_json, strip_provider_key


MCP_SERVER = ROOT / "scripts/saee_qianfan_readiness_mcp_stdio.py"
FIXTURES = {
    "customer-service": ROOT / "cloud-entry-package/demo/customer-service-refund/request.json",
    "coding-agent": ROOT / "cloud-entry-package/demo/coding-agent-release/request.json",
}
MCP_TO_PROVIDER = {
    "saee.evaluate_agent_run": "saee_evaluate_agent_run",
    "saee.evaluate_evidence": "saee_evaluate_evidence",
}
PROVIDER_TO_MCP = {value: key for key, value in MCP_TO_PROVIDER.items()}
PUBLIC_MCP_TOOLS = tuple(MCP_TO_PROVIDER)
MAX_ARGUMENT_BYTES = 1_000_000


class ReadinessHostError(RuntimeError):
    pass


class MCPClient:
    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self.next_id = 1
        self.transcript: list[dict[str, Any]] = []

    def start(self) -> None:
        self.process = subprocess.Popen(
            [sys.executable, str(MCP_SERVER)],
            cwd=ROOT,
            env=strip_provider_key(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=False,
        )

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.process is None or self.process.stdin is None or self.process.stdout is None:
            raise ReadinessHostError("mcp_not_started")
        request_id = self.next_id
        self.next_id += 1
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.process.stdin.write(canonical_json(message) + "\n")
        self.process.stdin.flush()
        ready, _, _ = select.select([self.process.stdout], [], [], 20)
        if not ready:
            raise ReadinessHostError("mcp_timeout")
        line = self.process.stdout.readline()
        if not line:
            raise ReadinessHostError("mcp_eof")
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            raise ReadinessHostError("mcp_non_json_response") from None
        self.transcript.append({"request": message, "response": response})
        if not isinstance(response, dict) or "error" in response:
            raise ReadinessHostError("mcp_error")
        return response

    def initialized(self) -> None:
        if self.process is None or self.process.stdin is None:
            raise ReadinessHostError("mcp_not_started")
        message = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        self.process.stdin.write(canonical_json(message) + "\n")
        self.process.stdin.flush()
        self.transcript.append({"request": message, "response": None})

    def close(self) -> dict[str, Any]:
        if self.process is None:
            return {"returncode": None, "stderr_bytes": 0}
        if self.process.stdin:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=5)
        stderr = self.process.stderr.read() if self.process.stderr else ""
        result = {"returncode": self.process.returncode, "stderr_bytes": len(stderr.encode("utf-8"))}
        self.process = None
        return result


def qianfan_tools(mcp_tools: list[dict[str, Any]], fixture_id: str) -> list[dict[str, Any]]:
    names = [item.get("name") for item in mcp_tools]
    if names != list(PUBLIC_MCP_TOOLS):
        raise ReadinessHostError("mcp_public_tool_drift")
    return [
        {
            "type": "function",
            "function": {
                "name": MCP_TO_PROVIDER[item["name"]],
                "description": item["description"],
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["fixture_id"],
                    "properties": {
                        "fixture_id": {
                            "type": "string",
                            "enum": [fixture_id],
                            "description": "Host-approved checked-in synthetic fixture identifier. The host resolves it to the full MCP request.",
                        }
                    },
                },
            },
        }
        for item in mcp_tools
    ]


def extract_call(response: dict[str, Any], expected_fixture: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    choices = response.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ReadinessHostError("provider_choice_invalid")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    calls = message.get("tool_calls") if isinstance(message, dict) else None
    if not isinstance(calls, list) or len(calls) != 1:
        raise ReadinessHostError("provider_tool_call_invalid")
    call = calls[0]
    function = call.get("function") if isinstance(call, dict) else None
    provider_name = function.get("name") if isinstance(function, dict) else None
    if provider_name not in PROVIDER_TO_MCP:
        raise ReadinessHostError("provider_tool_not_allowed")
    try:
        arguments = json.loads(function.get("arguments", ""))
    except (AttributeError, json.JSONDecodeError):
        raise ReadinessHostError("provider_arguments_invalid") from None
    if not isinstance(arguments, dict) or len(canonical_json(arguments).encode("utf-8")) > MAX_ARGUMENT_BYTES:
        raise ReadinessHostError("provider_arguments_invalid")
    if canonical_json(arguments) != canonical_json({"fixture_id": fixture_id}):
        raise ReadinessHostError("provider_fixture_mismatch")
    return {
        "id": call.get("id"),
        "provider_name": provider_name,
        "mcp_name": PROVIDER_TO_MCP[provider_name],
        "provider_arguments": arguments,
        "arguments": expected_fixture,
        "message": message,
    }


def run_roundtrip(provider: Any, fixture: dict[str, Any], fixture_id: str, mcp: MCPClient | None = None) -> dict[str, Any]:
    client = mcp or MCPClient()
    client.start()
    try:
        client.request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "saee-qianfan-readiness-host", "version": "0.1.0"}})
        client.initialized()
        listed = client.request("tools/list", {})
        mcp_tools = listed["result"]["tools"]
        tools = qianfan_tools(mcp_tools, fixture_id)
        target = "saee_evaluate_agent_run"
        messages = [
            {"role": "system", "content": "You are a bounded SAEE readiness reviewer. Call only the forced assessment function. Never claim deployment authorization, certification, customer validation, or production readiness."},
            {"role": "user", "content": "Evaluate the host-approved checked-in synthetic fixture with fixture_id=" + fixture_id + ". Do not invent or request another input."},
        ]
        first = provider.chat(messages, tools, {"type": "function", "function": {"name": target}})
        call = extract_call(first, fixture, fixture_id)
        if call["provider_name"] != target or call["mcp_name"] != "saee.evaluate_agent_run":
            raise ReadinessHostError("provider_wrong_product_operation")
        mcp_result = client.request("tools/call", {"name": call["mcp_name"], "arguments": call["arguments"]})["result"]
        if mcp_result.get("isError") is not False:
            raise ReadinessHostError("mcp_product_call_failed")
        result = mcp_result["structuredContent"]
        final_messages = [
            {"role": "system", "content": "Summarize the verified SAEE result. Preserve readiness, score, missing_evidence, deployment_authorized=false, and production_ready=false. Do not add approval claims."},
            {"role": "user", "content": canonical_json(result)},
        ]
        final = provider.chat(final_messages, [], "none")
        final_message = final.get("choices", [{}])[0].get("message", {})
        final_text = final_message.get("content") if isinstance(final_message, dict) else None
        if not isinstance(final_text, str):
            raise ReadinessHostError("provider_final_text_missing")
        provider_final_text = final_text
        normalized = provider_final_text.lower().replace(" ", "")
        required = (
            f"readiness={result['readiness']}",
            f"score={result['score']}",
            "deployment_authorized=false",
            "production_ready=false",
        )
        provider_final_boundary_preserved = all(item in normalized for item in required) and not any(
            item in normalized for item in ("deployment_authorized=true", "production_ready=true", "customer_validated=true")
        )
        if not provider_final_boundary_preserved:
            final_text = (
                f"readiness={result['readiness']} score={result['score']} "
                f"missing_evidence={canonical_json(result['missing_evidence'])} "
                "deployment_authorized=false production_ready=false"
            )
        return {
            "status": "pass",
            "provider": "baidu_qianfan",
            "model": provider.model,
            "provider_function_alias": target,
            "mcp_operation": call["mcp_name"],
            "public_mcp_tools": list(PUBLIC_MCP_TOOLS),
            "function_alias_crosswalk": dict(MCP_TO_PROVIDER),
            "fixture_sha256": sha256_json(fixture),
            "provider_fixture_reference": {"fixture_id": fixture_id, "full_fixture_sent_to_provider": False},
            "result": result,
            "final_answer": final_text,
            "provider_receipt": {
                "round_count": 2,
                "tool_call_response_id": first.get("id"),
                "tool_call_model": first.get("model"),
                "tool_call_finish_reason": first.get("choices", [{}])[0].get("finish_reason"),
                "final_response_id": final.get("id"),
                "final_model": final.get("model"),
                "final_finish_reason": final.get("choices", [{}])[0].get("finish_reason"),
                "provider_final_answer_sha256": hashlib.sha256(provider_final_text.encode("utf-8")).hexdigest(),
                "provider_final_boundary_preserved": provider_final_boundary_preserved,
                "host_canonical_summary_fallback": not provider_final_boundary_preserved,
                "delivered_final_answer_sha256": hashlib.sha256(final_text.encode("utf-8")).hexdigest(),
            },
            "mcp_transcript": client.transcript,
            "truth_boundary": {
                "synthetic_fixture": True,
                "external_provider_network_used": provider.__class__.__name__ == "QianfanClient",
                "saee_mcp_network_used": False,
                "customer_data_used": False,
                "external_world_actions": 0,
                "deployment_authorized": False,
                "official_qianfan_integration": False,
                "marketplace_submission": False,
                "customer_validated": False,
                "production_ready": False,
            },
            "mcp_process": client.close(),
        }
    except Exception:
        client.close()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one bounded Qianfan → SAEE readiness product roundtrip")
    parser.add_argument("--scenario", choices=sorted(FIXTURES), default="customer-service")
    parser.add_argument("--receipt", type=Path, help="Write a sanitized JSON receipt without provider text or MCP transcript")
    args = parser.parse_args()
    fixture = json.loads(FIXTURES[args.scenario].read_text(encoding="utf-8"))
    try:
        result = run_roundtrip(QianfanClient(), fixture, args.scenario)
    except QianfanProviderError as exc:
        print(json.dumps({
            "status": "provider_error",
            "category": exc.category,
            "http_status": exc.status,
            "credential_value_exposed": False,
            "provider_response_body_exposed": False,
            "truth_boundary": {
                "real_qianfan_product_roundtrip": False,
                "external_world_actions": 0,
                "marketplace_submission": False,
                "production_ready": False,
            },
        }, ensure_ascii=False, sort_keys=True))
        return 2
    except ReadinessHostError as exc:
        failure = {
            "status": "host_validation_error",
            "category": str(exc),
            "scenario": args.scenario,
            "credential_value_exposed": False,
            "provider_response_body_exposed": False,
            "truth_boundary": {
                "real_qianfan_product_roundtrip": False,
                "external_world_actions": 0,
                "marketplace_submission": False,
                "production_ready": False,
            },
        }
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(failure, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True))
        return 3
    printable = {key: value for key, value in result.items() if key not in {"mcp_transcript", "final_answer"}}
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(printable, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(printable, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
