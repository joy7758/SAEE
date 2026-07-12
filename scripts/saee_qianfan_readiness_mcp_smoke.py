#!/usr/bin/env python3
"""Offline acceptance checks for the two-tool Qianfan readiness product MCP."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.baidu_agent_readiness_service import (
    ReadinessInputError,
    evaluate_agent_run,
    evaluate_evidence,
)
from saee_backend.services.qianfan_readiness_mcp_adapter import (
    QianfanReadinessMCPAdapter,
    tool_definitions,
)


CUSTOMER = ROOT / "examples/baidu-qianfan/customer-service-refund/request.json"
CODING = ROOT / "examples/baidu-qianfan/coding-agent-release/request.json"
EVIDENCE = ROOT / "examples/baidu-qianfan/evaluate-evidence/request.json"
DESCRIPTOR = ROOT / "agent-interface/qianfan/saee-qianfan-agent-readiness-mcp.v0.1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_QIANFAN_READINESS_MCP_SMOKE: FAIL " + message)


def message(request_id: int, method: str, params: dict | None = None) -> dict:
    value = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        value["params"] = params
    return value


def ready() -> QianfanReadinessMCPAdapter:
    adapter = QianfanReadinessMCPAdapter()
    init = adapter.handle(message(1, "initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "smoke", "version": "0.1"}}))
    require(init is not None and init["result"]["protocolVersion"] == "2025-11-25", "initialize")
    require(adapter.handle({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) is None, "initialized notification")
    return adapter


def main() -> None:
    customer = load(CUSTOMER)
    coding = load(CODING)
    evidence_request = load(EVIDENCE)
    descriptor = load(DESCRIPTOR)
    tools = tool_definitions()
    names = [item["name"] for item in tools]
    require(names == ["saee.evaluate_agent_run", "saee.evaluate_evidence"], "public tool list")
    require(descriptor["public_tools"] == names and descriptor["truth_boundary"]["tool_count"] == 2, "descriptor")
    require(not ({"rehearse_agent", "describe_saee", "compare_observed_traces"} & set(names)), "internal tool leak")
    for tool in tools:
        Draft202012Validator.check_schema(tool["inputSchema"])
        Draft202012Validator.check_schema(tool["outputSchema"])
        require(tool["annotations"]["readOnlyHint"] is True and tool["annotations"]["destructiveHint"] is False, "tool annotations")

    customer_result = evaluate_agent_run(customer)
    coding_result = evaluate_agent_run(coding)
    evidence_result = evaluate_evidence(evidence_request)
    require(customer_result["readiness"] == "conditional" and customer_result["score"] == 75, "customer demo")
    require(customer_result["missing_evidence"] == ["HUMAN_APPROVAL"], "customer missing approval")
    require(coding_result["readiness"] == "replan" and coding_result["score"] == 50, "coding demo")
    require(coding_result["missing_evidence"] == ["ROLLBACK_PLAN", "HUMAN_APPROVAL"], "coding missing evidence")
    require(evidence_result["evidence_quality"] == "PARTIAL" and evidence_result["coverage_score"] == 67, "evidence demo")
    require(evidence_result["missing_evidence"] == ["ROLLBACK_PLAN"], "evidence missing rollback")
    for result in (customer_result, coding_result, evidence_result):
        require(result["score_semantics"] == "required_evidence_coverage_percent_not_reliability_probability", "score semantics")
        require(result["truth_boundary"]["deployment_authorized"] is False, "deployment boundary")
        require(result["truth_boundary"]["production_ready"] is False, "production boundary")

    adapter = ready()
    listed = adapter.handle(message(2, "tools/list", {}))
    require(listed is not None and [item["name"] for item in listed["result"]["tools"]] == names, "MCP discovery")
    run_call = adapter.handle(message(3, "tools/call", {"name": "saee.evaluate_agent_run", "arguments": customer}))
    evidence_call = adapter.handle(message(4, "tools/call", {"name": "saee.evaluate_evidence", "arguments": evidence_request}))
    debug_call = adapter.handle(message(5, "tools/call", {"name": "describe_saee", "arguments": {}}))
    require(run_call is not None and run_call["result"]["structuredContent"] == customer_result, "MCP run delegation")
    require(evidence_call is not None and evidence_call["result"]["structuredContent"] == evidence_result, "MCP evidence delegation")
    require(debug_call is not None and debug_call["error"]["code"] == -32602, "debug tool rejected")

    invalid = copy.deepcopy(customer)
    invalid["customer_data_included"] = True
    try:
        evaluate_agent_run(invalid)
    except ReadinessInputError as exc:
        require(exc.code == "READINESS_AGENT_RUN_REQUEST_INVALID", "customer-data rejection code")
    else:
        raise SystemExit("SAEE_QIANFAN_READINESS_MCP_SMOKE: FAIL customer data accepted")
    duplicate = copy.deepcopy(customer)
    duplicate["evidence"][1]["evidence_type"] = "TEST_RESULT"
    try:
        evaluate_agent_run(duplicate)
    except ReadinessInputError as exc:
        require(exc.code == "READINESS_EVIDENCE_TYPE_DUPLICATE", "duplicate type rejection")
    else:
        raise SystemExit("SAEE_QIANFAN_READINESS_MCP_SMOKE: FAIL duplicate evidence accepted")

    canonical = json.dumps(customer_result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(json.dumps(evaluate_agent_run(customer), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic")
    print(
        "SAEE_QIANFAN_READINESS_MCP_SMOKE: PASS tools=2 demos=3 "
        "customer_readiness=conditional coding_readiness=replan evidence_quality=PARTIAL "
        "invalid_cases=3 deterministic_runs=5/5 network=false external_execution=false production_ready=false"
    )


if __name__ == "__main__":
    main()
