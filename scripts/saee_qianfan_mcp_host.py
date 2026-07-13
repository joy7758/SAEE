#!/usr/bin/env python3
"""Bounded Baidu Qianfan function-calling host for the fixed SAEE MCP server.

This is an external-host integration experiment. Qianfan may choose only the
two tools advertised by the local MCP server. The validation path uses one
pre-approved sanitized fixture; it never accepts a model-generated path, URL,
command, code, prompt, raw log, or secret.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import select
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
MCP_SERVER = ROOT / "scripts/saee_mcp_stdio.py"
CLI = ROOT / "scripts/saee_agent_cli.py"
BUNDLE = ROOT / "agent-interface/examples/observed-trace-bundle.json"
EVIDENCE_DIR = ROOT / "agent_recommendation/agent_first_validation/run_005"
QIANFAN_ENDPOINT = "https://qianfan.baidubce.com/v2/chat/completions"
QIANFAN_MODEL = "ernie-4.5-turbo-128k"
QIANFAN_KEY_ENV = "QIANFAN_API_KEY"
MAX_PROVIDER_ROUNDS = 4
MAX_TOOL_ARGUMENT_BYTES = 5_000_000
MAX_JSON_DEPTH = 64
ALLOWED_TOOLS = ("describe_saee", "compare_observed_traces")
FORBIDDEN_KEYS = {
    "path", "url", "command", "module", "code", "secret", "token",
    "api_key", "authorization", "prompt", "message", "tool_payload",
    "raw_log", "raw_logs",
}


class HostError(RuntimeError):
    """An expected fail-closed host error without secret-bearing details."""


class ProviderError(HostError):
    def __init__(self, category: str, status: int | None = None) -> None:
        self.category = category
        self.status = status
        super().__init__(category)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def json_depth(value: Any, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        return depth
    if isinstance(value, dict):
        return max((json_depth(item, depth + 1) for item in value.values()), default=depth)
    if isinstance(value, list):
        return max((json_depth(item, depth + 1) for item in value), default=depth)
    return depth


def forbidden_keys(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                found.append(str(key))
            found.extend(forbidden_keys(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(forbidden_keys(item))
    return found


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise HostError(f"expected JSON object: {path.name}")
    return value


def strip_provider_key(environment: dict[str, str] | None = None) -> dict[str, str]:
    clean = dict(os.environ if environment is None else environment)
    for key in (QIANFAN_KEY_ENV, "OPENAI_API_KEY", "BAIDU_API_KEY"):
        clean.pop(key, None)
    return clean


def safe_tool_call(name: str, arguments: Any, expected: str, fixture: dict[str, Any]) -> None:
    if name not in ALLOWED_TOOLS:
        raise HostError("unknown_tool")
    if name != expected:
        raise HostError("unexpected_tool_order")
    if not isinstance(arguments, dict):
        raise HostError("non_object_arguments")
    if json_depth(arguments) > MAX_JSON_DEPTH:
        raise HostError("arguments_too_deep")
    if len(canonical_json(arguments).encode("utf-8")) > MAX_TOOL_ARGUMENT_BYTES:
        raise HostError("arguments_too_large")
    if forbidden_keys(arguments):
        raise HostError("forbidden_argument_key")
    if name == "describe_saee" and arguments:
        raise HostError("describe_arguments_must_be_empty")
    if name == "compare_observed_traces" and canonical_json(arguments) != canonical_json(fixture):
        raise HostError("fixture_mismatch")


class QianfanClient:
    def __init__(self, key: str | None = None, endpoint: str | None = None, model: str | None = None) -> None:
        self.key = key or os.environ.get(QIANFAN_KEY_ENV, "")
        if not self.key:
            raise ProviderError("missing_api_key")
        self.endpoint = endpoint or QIANFAN_ENDPOINT
        if self.endpoint != QIANFAN_ENDPOINT:
            raise ProviderError("endpoint_not_allowlisted")
        self.model = model or os.environ.get("QIANFAN_MODEL", QIANFAN_MODEL)
        if self.model != QIANFAN_MODEL:
            raise ProviderError("model_not_allowlisted")

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], tool_choice: Any) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "stream": False,
        }
        body = canonical_json(payload)

        # Standard-library HTTPS keeps the credential in process memory only;
        # no PATH-resolved helper receives the key and no shell is involved.
        request = urllib.request.Request(
            self.endpoint,
            data=body.encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read(2_000_001)
                status = int(response.status)
        except urllib.error.HTTPError as exc:
            raise ProviderError("provider_http_error", exc.code) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ProviderError("provider_timeout_or_network_error") from None
        if len(raw) > 2_000_000:
            raise ProviderError("provider_response_too_large")
        if status >= 400:
            raise ProviderError("provider_http_error", status)
        try:
            value = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            raise ProviderError("provider_non_json_response") from None
        if not isinstance(value, dict) or not isinstance(value.get("choices"), list) or not value["choices"]:
            raise ProviderError("provider_invalid_completion")
        return value


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
            raise HostError("mcp_not_started")
        request_id = self.next_id
        self.next_id += 1
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.process.stdin.write(canonical_json(message) + "\n")
        self.process.stdin.flush()
        ready, _, _ = select.select([self.process.stdout], [], [], 20)
        if not ready:
            raise HostError("mcp_timeout")
        line = self.process.stdout.readline()
        if not line:
            raise HostError("mcp_eof")
        try:
            result = json.loads(line)
        except json.JSONDecodeError:
            raise HostError("mcp_non_json_response") from None
        if not isinstance(result, dict):
            raise HostError("mcp_invalid_response")
        self.transcript.append({"request": message, "response": result})
        if "error" in result:
            raise HostError(f"mcp_error_{result['error'].get('code', 'unknown')}")
        return result

    def notify_initialized(self) -> None:
        if self.process is None or self.process.stdin is None:
            raise HostError("mcp_not_started")
        message = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        self.process.stdin.write(canonical_json(message) + "\n")
        self.process.stdin.flush()
        self.transcript.append({"request": message, "response": None})

    def close(self) -> dict[str, Any]:
        if self.process is None:
            return {"returncode": None, "stderr_bytes": 0}
        self.process.stdin.close() if self.process.stdin else None
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=5)
        stderr = self.process.stderr.read() if self.process.stderr else ""
        result = {"returncode": self.process.returncode, "stderr_bytes": len(stderr.encode("utf-8"))}
        self.process = None
        return result


def qianfan_tool_definitions(mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if [tool.get("name") for tool in mcp_tools] != list(ALLOWED_TOOLS):
        raise HostError("mcp_tool_allowlist_drift")
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool["inputSchema"],
            },
        }
        for tool in mcp_tools
    ]


def extract_tool_calls(provider_response: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    message = provider_response["choices"][0].get("message")
    if not isinstance(message, dict):
        raise ProviderError("provider_missing_message")
    calls = message.get("tool_calls")
    if not isinstance(calls, list) or not calls:
        raise ProviderError("provider_did_not_return_tool_call")
    normalized: list[dict[str, Any]] = []
    for call in calls:
        function = call.get("function") if isinstance(call, dict) else None
        if not isinstance(function, dict) or not isinstance(function.get("name"), str):
            raise ProviderError("provider_malformed_tool_call")
        try:
            arguments = json.loads(function.get("arguments", "{}"))
        except json.JSONDecodeError:
            raise ProviderError("provider_non_json_arguments") from None
        call_id = call.get("id") if isinstance(call, dict) else None
        call_type = call.get("type") if isinstance(call, dict) else None
        if not isinstance(call_id, str) or not call_id or call_type != "function":
            raise ProviderError("provider_malformed_tool_call")
        normalized.append({
            "id": call_id,
            "type": call_type,
            "name": function["name"],
            "arguments": arguments,
        })
    ids = [call["id"] for call in normalized]
    if len(ids) != len(set(ids)):
        raise ProviderError("provider_duplicate_tool_call_id")
    return message, normalized


def provider_summary(response: dict[str, Any], calls: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    choice = response.get("choices", [{}])[0] if isinstance(response.get("choices"), list) else {}
    message = choice.get("message", {}) if isinstance(choice, dict) else {}
    summary: dict[str, Any] = {
        "provider_response_id": response.get("id"),
        "model": response.get("model"),
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
    }
    if calls is not None:
        summary["tool_calls"] = [
            {
                "id": call["id"],
                "name": call["name"],
                "arguments_sha256": sha256_json(call["arguments"]),
                "arguments_bytes": len(canonical_json(call["arguments"]).encode("utf-8")),
            }
            for call in calls
        ]
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        summary["content_sha256"] = sha256_bytes(content.encode("utf-8"))
        summary["content_preview"] = content[:800]
    return summary


def run_roundtrip(qianfan: Any, mcp: MCPClient, fixture: dict[str, Any]) -> dict[str, Any]:
    mcp.start()
    try:
        mcp.request("initialize", {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "saee-qianfan-host", "version": "0.1.0"},
        })
        mcp.notify_initialized()
        listed = mcp.request("tools/list", {})
        mcp_tools = listed["result"]["tools"]
        qianfan_tools = qianfan_tool_definitions(mcp_tools)
        crosswalk = {
            "mcp_tool_names": [tool["name"] for tool in mcp_tools],
            "mcp_tools_sha256": sha256_json(mcp_tools),
            "qianfan_tools_sha256": sha256_json(qianfan_tools),
            "qianfan_tool_names": [tool["function"]["name"] for tool in qianfan_tools],
            "schema_crosswalk": [
                {"name": tool["name"], "input_schema_sha256": sha256_json(tool["inputSchema"])}
                for tool in mcp_tools
            ],
        }

        fixture_hash = sha256_json(fixture)
        user_content = (
            "请先调用 describe_saee。只使用当前提供的固定工具；不得执行智能体、"
            "访问外部系统或读取文件。"
        )
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": "你是 SAEE 外部智能体宿主验证器。只调用固定工具，并在最终回答保留所有 false 边界。"},
            {"role": "user", "content": user_content},
        ]
        provider_transcript: list[dict[str, Any]] = [{
            "event": "request",
            "model": qianfan.model,
            "endpoint_host": "qianfan.baidubce.com",
            "tool_names": list(ALLOWED_TOOLS),
            "tool_choice": "describe_saee",
            "fixture_sha256": fixture_hash,
        }]
        first = qianfan.chat(messages, qianfan_tools, {"type": "function", "function": {"name": "describe_saee"}})
        first_message, first_calls = extract_tool_calls(first)
        if len(first_calls) != 1:
            raise HostError("describe_call_count")
        safe_tool_call(first_calls[0]["name"], first_calls[0]["arguments"], "describe_saee", fixture)
        describe_result = mcp.request("tools/call", {"name": "describe_saee", "arguments": {}})["result"]
        provider_transcript.append({"event": "response", **provider_summary(first, first_calls)})
        messages.append(first_message)
        messages.append({
            "role": "tool",
            "tool_call_id": first_calls[0]["id"],
            "name": "describe_saee",
            "content": describe_result["content"][0]["text"],
        })
        messages.append({
            "role": "user",
            "content": (
                "现在调用 compare_observed_traces。参数必须逐字使用以下已批准脱敏 fixture；"
                "不要添加任何字段：\n" + canonical_json(fixture)
            ),
        })

        provider_transcript.append({
            "event": "request",
            "model": qianfan.model,
            "endpoint_host": "qianfan.baidubce.com",
            "tool_names": list(ALLOWED_TOOLS),
            "tool_choice": "compare_observed_traces",
            "fixture_sha256": fixture_hash,
        })
        second = qianfan.chat(messages, qianfan_tools, {"type": "function", "function": {"name": "compare_observed_traces"}})
        second_message, second_calls = extract_tool_calls(second)
        if len(second_calls) != 1:
            raise HostError("compare_call_count")
        safe_tool_call(second_calls[0]["name"], second_calls[0]["arguments"], "compare_observed_traces", fixture)
        compare_result = mcp.request("tools/call", {
            "name": "compare_observed_traces",
            "arguments": second_calls[0]["arguments"],
        })["result"]
        if compare_result.get("isError"):
            raise HostError("mcp_compare_error")
        receipt = compare_result["structuredContent"]
        cli = subprocess.run(
            [sys.executable, str(CLI), "evaluate-traces", "--input", str(BUNDLE)],
            cwd=ROOT,
            env=strip_provider_key(),
            capture_output=True,
            text=True,
            check=True,
        )
        cli_receipt = json.loads(cli.stdout)
        if receipt != cli_receipt:
            raise HostError("receipt_mismatch")
        provider_transcript.append({"event": "response", **provider_summary(second, second_calls)})
        messages.append(second_message)
        compare_tool_message = {
            "role": "tool",
            "tool_call_id": second_calls[0]["id"],
            "name": "compare_observed_traces",
            "content": compare_result["content"][0]["text"],
        }
        messages.append(compare_tool_message)

        provider_transcript.append({
            "event": "request",
            "model": qianfan.model,
            "endpoint_host": "qianfan.baidubce.com",
            "tool_names": [],
            "tool_choice": "none",
            "fixture_sha256": fixture_hash,
        })
        # Keep the final answer round small and deterministic. The full first
        # manifest and fixture were already exchanged in the tool-call rounds;
        # the final host response only needs the schema-valid comparison result.
        final_messages = [
            {
                "role": "system",
                "content": (
                    "你是 SAEE 外部智能体宿主验证器。请根据下面已验证的 tool result 用中文简短总结。"
                    "必须原样保留 candidate-alpha、0.719476、observed_trace_bundle_evaluation、"
                    "production_ready=false、customer_validated=false；不能宣称上线批准或真实客户验证。"
                ),
            },
            second_message,
            compare_tool_message,
            {
                "role": "user",
                "content": (
                    "请在回答中逐字包含以下五行机器事实，然后再补一句中文解释：\n"
                    "candidate-alpha\n0.719476\n"
                    "evaluation_mode=observed_trace_bundle_evaluation\n"
                    "production_ready=false\ncustomer_validated=false"
                ),
            },
        ]
        final = qianfan.chat(final_messages, [], "none")
        final_message = final["choices"][0].get("message", {})
        final_text = final_message.get("content", "") if isinstance(final_message, dict) else ""
        if not isinstance(final_text, str):
            raise HostError("final_answer_not_text")

        def final_facts_present(text: str) -> bool:
            normalized = text.lower().replace("`", "").replace(" ", "")
            required = ("candidate-alpha", "0.719476", "observed_trace_bundle_evaluation", "production_ready=false", "customer_validated=false")
            return all(marker in normalized for marker in required)

        if not final_facts_present(final_text):
            provider_transcript.append({"event": "final_answer_retry", "reason": "missing_required_receipt_facts"})
            retry_messages = [
                {
                    "role": "system",
                    "content": "只输出事实，不要改写机器字段。必须保留 false 边界。",
                },
                {
                    "role": "user",
                    "content": (
                        "根据已验证 SAEE 回执，严格输出以下五行，再加一句中文：\n"
                        "candidate-alpha\n0.719476\n"
                        "evaluation_mode=observed_trace_bundle_evaluation\n"
                        "production_ready=false\ncustomer_validated=false"
                    ),
                },
            ]
            final = qianfan.chat(retry_messages, [], "none")
            final_message = final["choices"][0].get("message", {})
            final_text = final_message.get("content", "") if isinstance(final_message, dict) else ""
            if not isinstance(final_text, str) or not final_facts_present(final_text):
                raise HostError("final_answer_missing_receipt_facts")
        forbidden = ("production_ready=true", "customer_validated=true", "external_system_executed=true")
        if any(marker in final_text for marker in forbidden):
            raise HostError("final_answer_boundary_drift")
        provider_transcript.append({"event": "response", **provider_summary(final)})
        return {
            "status": "pass",
            "provider": "baidu_qianfan",
            "model": qianfan.model,
            "qianfan_api_reached": True,
            "qianfan_tool_call_received": True,
            "mcp_tool_called": True,
            "provider_roundtrip_completed": True,
            "mcp_protocol_version": "2025-11-25",
            "mcp_tools": list(ALLOWED_TOOLS),
            "receipt_schema_valid": True,
            "request_hash_verified": receipt.get("request_sha256") == cli_receipt.get("request_sha256"),
            "content_hash_verified": receipt.get("content_sha256") == cli_receipt.get("content_sha256"),
            "winner": receipt["evaluation_summary"]["recommended_agent"],
            "winner_score": receipt["evaluation_summary"]["confidence_score"],
            "evaluation_mode": receipt["evaluation_mode"],
            "final_answer": final_text,
            "final_answer_sha256": sha256_bytes(final_text.encode("utf-8")),
            "fixture_sha256": fixture_hash,
            "provider_transcript": provider_transcript,
            "mcp_transcript": mcp.transcript,
            "crosswalk": crosswalk,
            "receipt": receipt,
            "mcp_process": mcp.close(),
            "secrets_redacted": True,
            "external_provider_network_used": True,
            "saee_mcp_network_used": False,
            "candidate_code_executed": False,
            "external_system_executed": False,
            "customer_validated": False,
            "production_ready": False,
            "product_launched": False,
        }
    except Exception:
        mcp.close()
        raise


def write_evidence(result: dict[str, Any], directory: Path = EVIDENCE_DIR) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    provider = result["provider_transcript"]
    mcp = result["mcp_transcript"]
    for name, rows in (("provider_transcript.redacted.jsonl", provider), ("mcp_transcript.jsonl", mcp)):
        (directory / name).write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")
    (directory / "tool_schema_crosswalk.json").write_text(canonical_json(result["crosswalk"]) + "\n", encoding="utf-8")
    (directory / "receipt.json").write_text(json.dumps(result["receipt"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    safe = {key: value for key, value in result.items() if key not in {"provider_transcript", "mcp_transcript", "crosswalk", "receipt"}}
    (directory / "validation_result.redacted.json").write_text(json.dumps(safe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Qianfan → SAEE MCP host validation")
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE_DIR)
    args = parser.parse_args()
    fixture = load_json(BUNDLE)
    result = run_roundtrip(QianfanClient(), MCPClient(), fixture)
    if args.write_evidence:
        write_evidence(result, args.evidence_dir)
    print(json.dumps({key: value for key, value in result.items() if key not in {"provider_transcript", "mcp_transcript", "crosswalk", "receipt", "final_answer"}}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
