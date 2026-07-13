#!/usr/bin/env python3
"""Validate the fixed SAEE MCP stdio adapter and adoption transcript."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts/saee_mcp_stdio.py"
CLI = ROOT / "scripts/saee_agent_cli.py"
BUNDLE = ROOT / "agent-interface/examples/observed-trace-bundle.json"
INPUT_SCHEMA = ROOT / "agent-interface/schemas/observed-trace-bundle.schema.json"
RECEIPT_SCHEMA = ROOT / "agent-interface/schemas/observed-trace-receipt.schema.json"
MAX_LINE_BYTES = 5_000_000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_MCP_STDIO_SMOKE: FAIL " + message)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.name} must contain an object")
    return value


def request(request_id: int, method: str, params: dict | list | None = None) -> dict:
    value = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        value["params"] = params
    return value


def initialize(request_id: int = 1) -> dict:
    return request(
        request_id,
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "saee-independent-smoke-client", "version": "0.1.0"},
        },
    )


INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}


def run_server(messages: list[dict | str | bytes], cwd: Path) -> tuple[list[dict], str, int]:
    chunks = []
    for message in messages:
        if isinstance(message, bytes):
            chunks.append(message)
        elif isinstance(message, str):
            chunks.append(message.encode("utf-8"))
        else:
            chunks.append(json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    payload = b"\n".join(chunks) + b"\n"
    completed = subprocess.run(
        [sys.executable, str(SERVER)],
        cwd=cwd,
        input=payload,
        capture_output=True,
        check=False,
    )
    stdout = completed.stdout.decode("utf-8")
    lines = [line for line in stdout.splitlines() if line]
    responses = [json.loads(line) for line in lines]
    return responses, completed.stderr.decode("utf-8"), completed.returncode


def by_id(responses: list[dict], request_id: int) -> dict:
    return next(item for item in responses if item.get("id") == request_id)


def main() -> None:
    bundle = load(BUNDLE)
    canonical_input_schema = load(INPUT_SCHEMA)
    cli = subprocess.run(
        [sys.executable, str(CLI), "evaluate-traces", "--input", str(BUNDLE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    cli_receipt = json.loads(cli.stdout)

    mismatch = copy.deepcopy(bundle)
    mismatch["candidates"][1]["context"]["scenario_id"] = "incomparable"
    raw_prompt = copy.deepcopy(bundle)
    raw_prompt["candidates"][0]["runs"][0]["steps"][0]["prompt"] = "forbidden"

    transcript = [
        initialize(1),
        INITIALIZED,
        request(2, "ping", {}),
        request(3, "tools/list", {}),
        request(4, "tools/call", {"name": "describe_saee", "arguments": {}}),
        request(5, "tools/call", {"name": "compare_observed_traces", "arguments": bundle}),
        request(6, "tools/call", {"name": "unknown_tool", "arguments": {}}),
        request(7, "unknown/method", {}),
        request(8, "tools/list", {"cursor": "unexpected"}),
        request(9, "tools/call", {"name": "describe_saee", "arguments": {"extra": True}}),
        request(10, "tools/call", {"name": "compare_observed_traces", "arguments": mismatch}),
        request(11, "tools/call", {"name": "compare_observed_traces", "arguments": raw_prompt}),
        request(12, "ping"),
        request(13, "tools/list"),
        request(14, "tools/call", {"name": "compare_observed_traces", "arguments": bundle}),
        request(15, "tools/call", {"name": "describe_saee", "arguments": {}}),
        {"jsonrpc": "2.0", "id": 16, "params": {}},
        {"id": 17, "method": "ping", "params": {}},
        request(18, "tools/call", []),
        request(19, "tools/call", {"name": "compare_observed_traces", "arguments": bundle}),
        request(20, "ping", {}),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        responses, stderr, returncode = run_server(transcript, tmpdir)
        require(returncode == 0, "server transcript exit")
        require(stderr == "", "stderr must be empty")
        require(len(responses) == 20, f"protocol transcript must pass 20/20, got {len(responses)}")
        require(not list(tmpdir.iterdir()), "stdio adapter must not write files")

    init = by_id(responses, 1)["result"]
    require(init["protocolVersion"] == "2025-11-25", "protocol negotiation")
    require(init["capabilities"] == {"tools": {"listChanged": False}}, "fixed capabilities")
    require(by_id(responses, 2)["result"] == {}, "ping")
    tools = by_id(responses, 3)["result"]["tools"]
    require([tool["name"] for tool in tools] == ["describe_saee", "compare_observed_traces"], "fixed two tools")
    require(tools[1]["inputSchema"] == canonical_input_schema, "canonical input schema drift")
    require(tools[0]["annotations"]["openWorldHint"] is False, "open world annotation")
    require(tools[1]["execution"]["taskSupport"] == "forbidden", "task support")

    compare_result = by_id(responses, 5)["result"]
    require(compare_result["isError"] is False, "compare tool error")
    receipt = compare_result["structuredContent"]
    require(receipt == cli_receipt, "CLI and MCP receipt differ")
    require(json.loads(compare_result["content"][0]["text"]) == receipt, "text compatibility receipt")
    require(not list(Draft202012Validator(tools[1]["outputSchema"]).iter_errors(receipt)), "self-contained output schema")
    require(receipt["provenance"]["candidate_code_executed"] is False, "candidate execution")
    require(receipt["provenance"]["external_calls_made"] is False, "external calls")

    require(by_id(responses, 6)["error"]["code"] == -32602, "unknown tool rejection")
    require(by_id(responses, 7)["error"]["code"] == -32601, "unknown method")
    require(by_id(responses, 8)["error"]["code"] == -32602, "invalid cursor")
    for request_id in (9, 10, 11):
        require(by_id(responses, request_id)["result"]["isError"] is True, f"tool error {request_id}")
    require(by_id(responses, 16)["error"]["code"] == -32600, "missing method")
    require(by_id(responses, 17)["error"]["code"] == -32600, "missing jsonrpc")
    require(by_id(responses, 18)["error"]["code"] == -32602, "invalid params type")

    malicious = []
    for field in ("path", "url", "command", "code", "secret"):
        value = copy.deepcopy(bundle)
        value[field] = f"forbidden-{field}"
        malicious.append(value)
    mixed = [initialize(1000), INITIALIZED]
    successful_ids = []
    for index in range(100):
        request_id = 1100 + index
        mode = index % 5
        if mode == 0:
            successful_ids.append(request_id)
            mixed.append(request(request_id, "tools/call", {"name": "compare_observed_traces", "arguments": bundle}))
        elif mode == 1:
            mixed.append(request(request_id, "tools/call", {"name": "compare_observed_traces", "arguments": malicious[index % len(malicious)]}))
        elif mode == 2:
            mixed.append(request(request_id, "tools/list", {}))
        elif mode == 3:
            mixed.append(request(request_id, "ping", {}))
        else:
            mixed.append(request(request_id, "tools/call", {"name": "unknown_tool", "arguments": {}}))
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        mixed_responses, mixed_stderr, mixed_code = run_server(mixed, tmpdir)
        require(mixed_code == 0 and mixed_stderr == "", "100-request mixed run")
        require(len(mixed_responses) == 101, "100 mixed responses plus initialize")
        require(not list(tmpdir.iterdir()), "100-request run wrote files")
    receipts = [by_id(mixed_responses, request_id)["result"]["structuredContent"] for request_id in successful_ids]
    require(len(receipts) >= 10 and all(item == cli_receipt for item in receipts), "10/10 MCP determinism")

    deep: dict = {"leaf": True}
    for _ in range(70):
        deep = {"nested": deep}
    size_line = b'{"jsonrpc":"2.0","id":30,"method":"ping","padding":"' + b"x" * MAX_LINE_BYTES + b'"}'
    robustness = [initialize(21), INITIALIZED, request(22, "tools/call", {"name": "compare_observed_traces", "arguments": deep}), size_line, request(23, "ping", {})]
    with tempfile.TemporaryDirectory() as tmp:
        robust_responses, robust_stderr, robust_code = run_server(robustness, Path(tmp))
    require(robust_code == 0 and robust_stderr == "", "robustness process")
    require(by_id(robust_responses, 22)["error"]["code"] == -32602, "nesting limit")
    require(any(item.get("error", {}).get("message") == "Request exceeds size limit" for item in robust_responses), "size limit")
    require(by_id(robust_responses, 23)["result"] == {}, "server continues after oversized request")

    source = SERVER.read_text(encoding="utf-8")
    for forbidden_token in ("import socket", "import subprocess", "import importlib", "os.system", "Popen(", "eval(", "exec("):
        require(forbidden_token not in source, f"forbidden runtime capability: {forbidden_token}")

    print(
        "SAEE_MCP_STDIO_SMOKE: PASS protocol=2025-11-25 transcript=20/20 "
        "tools=2 cli_mcp_hash_match=10/10 mixed_requests=100 schema_errors=0 "
        "unknown_tools_rejected=true arbitrary_path_url_command=false "
        "subprocess=false socket=false file_writes=0"
    )


if __name__ == "__main__":
    main()
