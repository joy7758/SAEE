"""Local MCP stdio adapter that delegates every Tool to Capability Runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, BinaryIO

from jsonschema import Draft202012Validator

from saee_backend.services.capability_runtime import invoke_capability


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_VERSION = "2025-11-25"
SUPPORTED_PROTOCOLS = ("2025-11-25", "2025-06-18", "2024-11-05")
SERVER_NAME = "saee-capability-runtime-adapter"
SERVER_VERSION = "0.1.0"
MAX_LINE_BYTES = 5_000_000
MAX_JSON_DEPTH = 64
PACKAGE_MCP = ROOT / "capability-package/mcp-tool.json"
REQUEST_SCHEMA = ROOT / "schemas/saee-capability-invocation-request.schema.v0.1.json"
RESPONSE_SCHEMA = ROOT / "schemas/saee-capability-invocation-response.schema.v0.1.json"
RECEIPT_SCHEMA = ROOT / "schemas/saee-capability-invocation-receipt.schema.v0.1.json"
EVIDENCE_SCHEMA = ROOT / "agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"invalid JSON object: {path.name}")
    return value


def _caller_context_schema() -> dict[str, Any]:
    return _load(REQUEST_SCHEMA)["properties"]["caller_context"]


def _tool_input(payload_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["request_id", "payload", "caller_context"],
        "properties": {
            "request_id": _load(REQUEST_SCHEMA)["properties"]["request_id"],
            "payload": payload_schema,
            "caller_context": _caller_context_schema(),
        },
    }


def _output_schema() -> dict[str, Any]:
    response = _load(RESPONSE_SCHEMA)
    response["properties"]["invocation_receipt"] = _load(RECEIPT_SCHEMA)
    return response


def tool_definitions() -> list[dict[str, Any]]:
    package = _load(PACKAGE_MCP)
    descriptions = {item["name"]: item["description"] for item in package["tools"]}
    run_payload = {
        "type": "object",
        "additionalProperties": False,
        "required": ["rehearsal_run"],
        "properties": {
            "rehearsal_run": {
                "type": "object",
                "minProperties": 1,
                "description": "Canonical validation is delegated to agent_run_capability using saee-agent-rehearsal-run.v0.1.schema.json."
            }
        },
    }
    rehearsal_payload = {
        "type": "object",
        "additionalProperties": False,
        "required": ["agent_reference", "scenario_reference", "consent_scope"],
        "properties": {
            "agent_reference": {"type": "string", "minLength": 1},
            "scenario_reference": {"type": "string", "minLength": 1},
            "consent_scope": {"const": "local_controlled_synthetic_only"},
        },
    }
    payloads = {
        "evaluate_rehearsal_run": run_payload,
        "evaluate_evidence": _load(EVIDENCE_SCHEMA),
        "rehearse_agent": rehearsal_payload,
    }
    titles = {
        "evaluate_rehearsal_run": "评估内部排演运行 / Evaluate Rehearsal Run",
        "evaluate_evidence": "评估证据充分性 / Evaluate Evidence",
        "rehearse_agent": "智能体演练契约 / Rehearse Agent Contract",
    }
    return [
        {
            "name": name,
            "title": titles[name],
            "description": descriptions[name],
            "inputSchema": _tool_input(payloads[name]),
            "outputSchema": _output_schema(),
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
            "execution": {"taskSupport": "forbidden"},
        }
        for name in ("evaluate_rehearsal_run", "evaluate_evidence", "rehearse_agent")
    ]


def _json_depth(value: Any, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        return depth
    if isinstance(value, dict):
        return max((_json_depth(item, depth + 1) for item in value.values()), default=depth)
    if isinstance(value, list):
        return max((_json_depth(item, depth + 1) for item in value), default=depth)
    return depth


def _response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_result(value: dict[str, Any]) -> dict[str, Any]:
    is_error = value["status"] != "SUCCESS"
    return {
        "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))}],
        "structuredContent": value,
        "isError": is_error,
    }


class AdapterState:
    def __init__(self) -> None:
        self.initialize_responded = False
        self.initialized = False
        self.protocol_version = PROTOCOL_VERSION


class CapabilityMCPAdapter:
    def __init__(self) -> None:
        self.state = AdapterState()

    def handle(self, message: Any) -> dict[str, Any] | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return _error(message.get("id") if isinstance(message, dict) else None, -32600, "Invalid Request")
        request_id = message.get("id")
        method = message.get("method")
        if not isinstance(method, str):
            return _error(request_id, -32600, "Invalid Request")
        notification = "id" not in message
        params = message.get("params", {})
        if not isinstance(params, dict):
            return None if notification else _error(request_id, -32602, "Invalid params")
        if method == "initialize":
            if notification:
                return None
            protocol = params.get("protocolVersion")
            if not isinstance(protocol, str) or not isinstance(params.get("capabilities"), dict) or not isinstance(params.get("clientInfo"), dict):
                return _error(request_id, -32602, "Invalid initialize params")
            selected = protocol if protocol in SUPPORTED_PROTOCOLS else PROTOCOL_VERSION
            self.state.protocol_version = selected
            self.state.initialize_responded = True
            return _response(request_id, {
                "protocolVersion": selected,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "title": "SAEE 本地能力适配器 / SAEE Local Capability Adapter", "version": SERVER_VERSION, "description": "本地只读 MCP Adapter；所有 Tool 委托 SAEE Capability Runtime。"},
                "instructions": "仅提交本地受控、无客户数据、无网络和无外部动作的内联请求。Tool 结果不是授权、认证或部署批准。",
            })
        if method == "notifications/initialized":
            if self.state.initialize_responded:
                self.state.initialized = True
            return None
        if method == "ping":
            return None if notification else _response(request_id, {})
        if not self.state.initialized:
            return None if notification else _error(request_id, -32002, "Server not initialized")
        if method == "tools/list":
            if params not in ({}, {"cursor": None}):
                return _error(request_id, -32602, "Invalid tools/list params")
            return _response(request_id, {"tools": tool_definitions()})
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            definitions = {item["name"]: item for item in tool_definitions()}
            if not isinstance(name, str) or not isinstance(arguments, dict):
                return _error(request_id, -32602, "Invalid tools/call params")
            if name not in definitions:
                return _error(request_id, -32602, "Unknown tool")
            errors = list(Draft202012Validator(definitions[name]["inputSchema"]).iter_errors(arguments))
            if errors:
                rejected = {
                    "request_id": arguments.get("request_id", "request:invalid") if isinstance(arguments.get("request_id"), str) else "request:invalid",
                    "capability_id": "saee.agent-reliability",
                    "operation": name,
                    "status": "REJECTED",
                    "result": {},
                    "reason_codes": ["CAPABILITY_MCP_ARGUMENTS_INVALID"],
                    "limitations": ["MCP arguments failed the strict Tool schema."] * 6,
                }
                return _response(request_id, {"content": [{"type": "text", "text": json.dumps(rejected, sort_keys=True)}], "isError": True})
            runtime_request = {"request_id": arguments["request_id"], "capability_id": "saee.agent-reliability", "operation": name, "payload": arguments["payload"], "caller_context": arguments["caller_context"]}
            value = invoke_capability(runtime_request)
            return _response(request_id, _tool_result(value))
        return None if notification else _error(request_id, -32601, "Method not found")


def _emit(stream: BinaryIO, payload: dict[str, Any]) -> None:
    stream.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
    stream.flush()


def serve(input_stream: BinaryIO, output_stream: BinaryIO) -> int:
    adapter = CapabilityMCPAdapter()
    while True:
        line = input_stream.readline(MAX_LINE_BYTES + 1)
        if not line:
            return 0
        if len(line) > MAX_LINE_BYTES:
            while line and not line.endswith(b"\n"):
                line = input_stream.readline(MAX_LINE_BYTES + 1)
            _emit(output_stream, _error(None, -32602, "Request exceeds size limit"))
            continue
        try:
            message = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            _emit(output_stream, _error(None, -32700, "Parse error"))
            continue
        if _json_depth(message) > MAX_JSON_DEPTH:
            _emit(output_stream, _error(message.get("id") if isinstance(message, dict) else None, -32602, "Request exceeds nesting limit"))
            continue
        try:
            result = adapter.handle(message)
        except Exception:
            result = _error(message.get("id") if isinstance(message, dict) else None, -32603, "Internal error")
        if result is not None:
            _emit(output_stream, result)
