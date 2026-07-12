"""Two-tool local MCP projection for the SAEE Agent Readiness product."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, BinaryIO

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from saee_backend.services.baidu_agent_readiness_service import (
    ReadinessInputError,
    evaluate_agent_run,
    evaluate_evidence,
)


ROOT = Path(__file__).resolve().parents[2]
QIANFAN = ROOT / "agent-interface/qianfan"
PROTOCOL_VERSION = "2025-11-25"
SUPPORTED_PROTOCOLS = ("2025-11-25", "2025-06-18", "2024-11-05")
MAX_LINE_BYTES = 1_000_000
MAX_JSON_DEPTH = 64
TOOLS = (
    ("saee.evaluate_agent_run", "saee-evaluate-agent-run-request.schema.v0.1.json", "saee-evaluate-agent-run-response.schema.v0.1.json"),
    ("saee.evaluate_evidence", "saee-evaluate-evidence-request.schema.v0.1.json", "saee-evaluate-evidence-response.schema.v0.1.json"),
)


def _load(name: str) -> dict[str, Any]:
    value = json.loads((QIANFAN / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"invalid schema: {name}")
    return value


def _registry() -> Registry:
    resources = Registry()
    for name in (
        "saee-readiness-evidence-item.schema.v0.1.json",
        "saee-evaluate-agent-run-request.schema.v0.1.json",
        "saee-evaluate-agent-run-response.schema.v0.1.json",
        "saee-evaluate-evidence-request.schema.v0.1.json",
        "saee-evaluate-evidence-response.schema.v0.1.json",
    ):
        schema = _load(name)
        resources = resources.with_resource(schema["$id"], Resource.from_contents(schema))
    return resources


def tool_definitions() -> list[dict[str, Any]]:
    descriptions = {
        "saee.evaluate_agent_run": "Evaluate declared Agent trace and required evidence coverage before a separately authorized real-world deployment decision.",
        "saee.evaluate_evidence": "Evaluate whether a declared evidence bundle covers an explicit readiness evidence set without authorizing deployment.",
    }
    return [
        {
            "name": operation,
            "title": "评估智能体运行 / Evaluate Agent Run" if operation.endswith("agent_run") else "评估证据 / Evaluate Evidence",
            "description": descriptions[operation],
            "inputSchema": _load(request_schema),
            "outputSchema": _load(response_schema),
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
            "execution": {"taskSupport": "forbidden"},
        }
        for operation, request_schema, response_schema in TOOLS
    ]


def _depth(value: Any, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        return depth
    if isinstance(value, dict):
        return max((_depth(item, depth + 1) for item in value.values()), default=depth)
    if isinstance(value, list):
        return max((_depth(item, depth + 1) for item in value), default=depth)
    return depth


class QianfanReadinessMCPAdapter:
    def __init__(self) -> None:
        self.initialized = False
        self.initialize_responded = False

    def handle(self, message: Any) -> dict[str, Any] | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return {"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None, "error": {"code": -32600, "message": "Invalid Request"}}
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})
        if not isinstance(method, str) or not isinstance(params, dict):
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Invalid params"}}
        if method == "initialize":
            self.initialize_responded = True
            requested = params.get("protocolVersion")
            selected = requested if requested in SUPPORTED_PROTOCOLS else PROTOCOL_VERSION
            return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": selected, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "saee-qianfan-agent-readiness", "title": "SAEE 智能体上线准备平台", "version": "0.1.0"}, "instructions": "Only two read-only assessment tools are public. Results are evidence context, not deployment authorization."}}
        if method == "notifications/initialized":
            self.initialized = self.initialize_responded
            return None
        if not self.initialized:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32002, "message": "Server not initialized"}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tool_definitions()}}
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments")
            definitions = {item["name"]: item for item in tool_definitions()}
            if name not in definitions or not isinstance(arguments, dict):
                return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Unknown tool or invalid arguments"}}
            errors = list(Draft202012Validator(definitions[name]["inputSchema"], registry=_registry()).iter_errors(arguments))
            if errors:
                return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": "READINESS_MCP_ARGUMENTS_INVALID"}], "isError": True}}
            try:
                result = evaluate_agent_run(arguments) if name == "saee.evaluate_agent_run" else evaluate_evidence(arguments)
            except ReadinessInputError as exc:
                return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": exc.code}], "isError": True}}
            return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))}], "structuredContent": result, "isError": False}}
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}


def serve(input_stream: BinaryIO, output_stream: BinaryIO) -> int:
    adapter = QianfanReadinessMCPAdapter()
    while True:
        line = input_stream.readline(MAX_LINE_BYTES + 1)
        if not line:
            return 0
        if len(line) > MAX_LINE_BYTES or not line.endswith(b"\n"):
            output_stream.write(b'{"jsonrpc":"2.0","id":null,"error":{"code":-32602,"message":"Request exceeds size limit"}}\n')
            output_stream.flush()
            continue
        try:
            message = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            result = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        else:
            if _depth(message) > MAX_JSON_DEPTH:
                result = {"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None, "error": {"code": -32602, "message": "Request exceeds nesting limit"}}
            else:
                result = adapter.handle(message)
        if result is not None:
            output_stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
            output_stream.flush()
