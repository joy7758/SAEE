#!/usr/bin/env python3
"""Fixed, dependency-free MCP stdio adapter for SAEE observed trace evaluation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, BinaryIO


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ValidationError

from saee_backend.observed_trace_adapter import (
    ObservedTraceBundle,
    evaluate_observed_trace_bundle,
)


SERVER_NAME = "saee-observed-trace"
SERVER_VERSION = "0.1.0"
LATEST_PROTOCOL_VERSION = "2025-11-25"
SUPPORTED_PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2024-11-05")
MAX_LINE_BYTES = 5_000_000
MAX_JSON_DEPTH = 64
MANIFEST_PATH = ROOT / "agent-interface/agent-manifest.json"
MANIFEST_SCHEMA_PATH = ROOT / "agent-interface/schemas/saee-agent-manifest.schema.json"
OBSERVED_SCHEMA_PATH = ROOT / "agent-interface/schemas/observed-trace-bundle.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "agent-interface/schemas/observed-trace-receipt.schema.json"
PUBLIC_SCHEMA_PATH = ROOT / "schemas/saee_mvp_api.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path.name}")
    return value


def self_contained_receipt_schema() -> dict[str, Any]:
    schema = load_json(RECEIPT_SCHEMA_PATH)
    public = load_json(PUBLIC_SCHEMA_PATH)
    encoded = json.dumps(schema, ensure_ascii=False).replace(
        "../../schemas/saee_mvp_api.schema.json#/$defs/",
        "#/$defs/",
    )
    bundled = json.loads(encoded)
    bundled["$defs"] = public["$defs"]
    return bundled


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "describe_saee",
            "title": "SAEE 能力说明 / SAEE Capability Description",
            "description": "返回中英双语 SAEE 清单；返回 bilingual SAEE manifest。",
            "inputSchema": {"type": "object", "additionalProperties": False},
            "outputSchema": load_json(MANIFEST_SCHEMA_PATH),
            "annotations": {
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False,
            },
            "execution": {"taskSupport": "forbidden"},
        },
        {
            "name": "compare_observed_traces",
            "title": "比较真实运行轨迹包 / Compare Observed Trace Bundles",
            "description": (
                "比较内联的脱敏数值轨迹包；不接受路径、URL、命令或原始日志。 "
                "Compare an inline sanitized numerical trace bundle; no paths, URLs, commands, or raw logs."
            ),
            "inputSchema": load_json(OBSERVED_SCHEMA_PATH),
            "outputSchema": self_contained_receipt_schema(),
            "annotations": {
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False,
            },
            "execution": {"taskSupport": "forbidden"},
        },
    ]


def json_depth(value: Any, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        return depth
    if isinstance(value, dict):
        return max((json_depth(item, depth + 1) for item in value.values()), default=depth)
    if isinstance(value, list):
        return max((json_depth(item, depth + 1) for item in value), default=depth)
    return depth


def response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def tool_result(value: dict[str, Any], is_error: bool = False) -> dict[str, Any]:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result: dict[str, Any] = {
        "content": [{"type": "text", "text": serialized}],
        "isError": is_error,
    }
    if not is_error:
        result["structuredContent"] = value
    return result


class ServerState:
    def __init__(self) -> None:
        self.initialize_responded = False
        self.initialized = False
        self.protocol_version = LATEST_PROTOCOL_VERSION


def handle_message(message: Any, state: ServerState) -> dict[str, Any] | None:
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        return error_response(message.get("id") if isinstance(message, dict) else None, -32600, "Invalid Request")
    request_id = message.get("id")
    method = message.get("method")
    if not isinstance(method, str):
        return error_response(request_id, -32600, "Invalid Request")
    is_notification = "id" not in message
    params = message.get("params", {})
    if not isinstance(params, dict):
        return None if is_notification else error_response(request_id, -32602, "Invalid params")

    if method == "initialize":
        if is_notification:
            return None
        protocol = params.get("protocolVersion")
        if not isinstance(protocol, str) or not isinstance(params.get("capabilities"), dict) or not isinstance(params.get("clientInfo"), dict):
            return error_response(request_id, -32602, "Invalid initialize params")
        selected = protocol if protocol in SUPPORTED_PROTOCOL_VERSIONS else LATEST_PROTOCOL_VERSION
        state.protocol_version = selected
        state.initialize_responded = True
        return response(
            request_id,
            {
                "protocolVersion": selected,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": SERVER_NAME,
                    "title": "SAEE 真实运行轨迹评估 / SAEE Observed Trace Evaluation",
                    "version": SERVER_VERSION,
                    "description": "固定双工具、本地只读、不执行外部世界。 Fixed two-tool local read-only server.",
                },
                "instructions": (
                    "仅提交符合 observed trace schema 的内联脱敏数值包。 "
                    "Submit only inline sanitized numerical bundles matching the observed trace schema."
                ),
            },
        )

    if method == "notifications/initialized":
        if state.initialize_responded:
            state.initialized = True
        return None
    if method == "notifications/cancelled":
        return None
    if method == "ping":
        return None if is_notification else response(request_id, {})
    if not state.initialized:
        return None if is_notification else error_response(request_id, -32002, "Server not initialized")
    if method == "tools/list":
        if params not in ({}, {"cursor": None}):
            return error_response(request_id, -32602, "Invalid tools/list params")
        return response(request_id, {"tools": tool_definitions()})
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str) or not isinstance(arguments, dict):
            return error_response(request_id, -32602, "Invalid tools/call params")
        if name == "describe_saee":
            if arguments:
                return response(request_id, tool_result({"error_type": "schema_validation_error", "message": "describe_saee accepts no arguments"}, True))
            return response(request_id, tool_result(load_json(MANIFEST_PATH)))
        if name == "compare_observed_traces":
            try:
                bundle = ObservedTraceBundle.model_validate(arguments)
                receipt = evaluate_observed_trace_bundle(bundle)
                return response(request_id, tool_result(receipt))
            except ValidationError:
                return response(
                    request_id,
                    tool_result(
                        {
                            "error_type": "schema_validation_error",
                            "message": "Observed trace bundle failed the strict allowlist or comparability contract",
                        },
                        True,
                    ),
                )
        return error_response(request_id, -32602, "Unknown tool")
    return None if is_notification else error_response(request_id, -32601, "Method not found")


def emit(stream: BinaryIO, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    stream.write(data + b"\n")
    stream.flush()


def serve(input_stream: BinaryIO, output_stream: BinaryIO) -> int:
    state = ServerState()
    while True:
        line = input_stream.readline(MAX_LINE_BYTES + 1)
        if not line:
            return 0
        if len(line) > MAX_LINE_BYTES:
            while line and not line.endswith(b"\n"):
                line = input_stream.readline(MAX_LINE_BYTES + 1)
            emit(output_stream, error_response(None, -32602, "Request exceeds size limit"))
            continue
        try:
            message = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            emit(output_stream, error_response(None, -32700, "Parse error"))
            continue
        if json_depth(message) > MAX_JSON_DEPTH:
            request_id = message.get("id") if isinstance(message, dict) else None
            emit(output_stream, error_response(request_id, -32602, "Request exceeds nesting limit"))
            continue
        try:
            result = handle_message(message, state)
        except Exception:
            request_id = message.get("id") if isinstance(message, dict) else None
            result = error_response(request_id, -32603, "Internal error")
        if result is not None:
            emit(output_stream, result)


def main() -> int:
    return serve(sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    raise SystemExit(main())
