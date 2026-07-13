#!/usr/bin/env python3
"""Validate the Qoder-compatible project config and two-tool local MCP flow."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_CONFIG = ROOT / ".mcp.json"
QODER_CONFIG = ROOT / "adapters/qoder/qoder-project.mcp.json"
REQUEST = ROOT / "examples/qoder-saee-readiness-demo/request.json"
EXPECTED = ROOT / "examples/qoder-saee-readiness-demo/response.json"
PUBLIC_TOOLS = ["saee.evaluate_agent_run", "saee.evaluate_evidence"]
HIDDEN_TOOLS = {"rehearse_agent", "describe_saee", "compare_observed_traces"}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"SAEE_QODER_ADAPTER_SMOKE: FAIL non-object {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_QODER_ADAPTER_SMOKE: FAIL " + message)


def rpc(request_id: int, method: str, params: dict | None = None) -> dict:
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


def main() -> None:
    root_config = load(ROOT_CONFIG)
    qoder_config = load(QODER_CONFIG)
    require(root_config == qoder_config, "project config drift")
    servers = root_config.get("mcpServers")
    require(isinstance(servers, dict) and list(servers) == ["saee-readiness"], "server set")
    server = servers["saee-readiness"]
    require(server == {
        "command": "python3",
        "args": ["scripts/saee_agent_readiness_mcp_stdio.py"],
        "env": {},
    }, "Qoder stdio config")

    request = load(REQUEST)
    expected = load(EXPECTED)
    messages = [
        rpc(1, "initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "qoder-compatible-local-smoke", "version": "0.1"}}),
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        rpc(2, "tools/list", {}),
        rpc(3, "tools/call", {"name": "saee.evaluate_agent_run", "arguments": request}),
        rpc(4, "tools/call", {"name": "describe_saee", "arguments": {}}),
    ]
    payload = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in messages)
    completed = subprocess.run(
        ["python3", "scripts/saee_agent_readiness_mcp_stdio.py"],
        cwd=ROOT,
        input=payload,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    require(completed.returncode == 0, f"stdio exit={completed.returncode} stderr={completed.stderr[:200]}")
    responses = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    require(len(responses) == 4, "response count")
    initialized, listed, called, hidden = responses
    require(initialized["result"]["serverInfo"]["name"] == "saee-agent-readiness-capability", "server identity")
    tools = listed["result"]["tools"]
    names = [item["name"] for item in tools]
    require(names == PUBLIC_TOOLS, "public tool list")
    require(not (set(names) & HIDDEN_TOOLS), "hidden tool leak")
    require(all(item["annotations"]["readOnlyHint"] is True for item in tools), "read-only annotations")
    require(called["result"]["structuredContent"] == expected, "coding-release receipt")
    require(called["result"]["isError"] is False, "valid call marked error")
    require(hidden["error"]["code"] == -32602, "hidden tool not rejected")
    require(expected["readiness"] == "replan" and expected["recommendation"] == "REPLAN", "decision")
    require(expected["missing_evidence"] == ["ROLLBACK_PLAN", "HUMAN_APPROVAL"], "missing evidence")
    require(expected["truth_boundary"]["deployment_authorized"] is False, "deployment boundary")
    require(expected["truth_boundary"]["production_ready"] is False, "production boundary")
    print(
        "SAEE_QODER_ADAPTER_SMOKE: PASS config=project_mcp tools=2 "
        "coding_demo=replan missing=ROLLBACK_PLAN,HUMAN_APPROVAL "
        "qoder_process_executed=false official_qoder_integration=false "
        "external_execution=false production_ready=false"
    )


if __name__ == "__main__":
    main()
