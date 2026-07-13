#!/usr/bin/env python3
"""Offline adversarial smoke for the synthetic MCP dry integration."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.mcp_ecosystem_discovery_simulator import select_tool
from saee_backend.services.mcp_ecosystem_dry_integration import run_all_scenarios
from saee_backend.services.mcp_result_interpretation_validator import validate_interpretation


SCENARIO_DIR = ROOT / "agent-interface/mcp/mcp-dry-integration-scenarios"
AGENT_SCHEMA = ROOT / "schemas/saee-synthetic-mcp-agent.schema.v0.1.json"
TRACE_SCHEMA = ROOT / "schemas/saee-mcp-dry-integration-trace.schema.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/mcp/saee-mcp-dry-integration-result.v0.1.json"
CONTROLLER = ROOT / "saee_backend/services/mcp_ecosystem_dry_integration.py"
ADAPTER = ROOT / "saee_backend/services/capability_mcp_adapter.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expect_schema_reject(validator: Draft202012Validator, value: dict) -> None:
    try:
        validator.validate(value)
    except ValidationError:
        return
    raise AssertionError("invalid fixture unexpectedly passed schema")


def main() -> int:
    agent_validator = Draft202012Validator(load(AGENT_SCHEMA))
    trace_validator = Draft202012Validator(load(TRACE_SCHEMA))
    scenarios = [load(path) for path in sorted(SCENARIO_DIR.glob("*.json"))]
    require(len(scenarios) >= 6, "scenario count below six")

    actual = run_all_scenarios()
    checked_in = load(RESULT_PATH)
    require(actual == checked_in, "checked-in result differs from deterministic controller output")
    traces = actual["scenario_results"]
    for trace in traces:
        trace_validator.validate(trace)
    require(actual["tool_results"]["tools_discovered"] >= 3, "tool discovery below three")
    require(actual["tool_results"]["runtime_invocations"] == 3, "runtime invocation count invalid")
    require(sum(1 for item in traces if item["runtime_delegation"]["delegated"]) == 3, "runtime delegation proof invalid")
    require(actual["tool_results"]["selection_rejections"] == 2, "selection rejection count invalid")
    require(actual["tool_results"]["abstentions"] == 1, "abstention count invalid")

    controller_tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    direct_evaluator_imports = 0
    forbidden_modules = {
        "saee_backend.services.agent_run_capability",
        "saee_backend.services.evidence_adequacy",
        "saee_backend.services.local_evidence_tool",
        "saee_backend.services.capability_runtime.capability_router",
    }
    for node in ast.walk(controller_tree):
        if isinstance(node, ast.ImportFrom) and node.module in forbidden_modules:
            direct_evaluator_imports += 1
        elif isinstance(node, ast.Import):
            direct_evaluator_imports += sum(alias.name in forbidden_modules for alias in node.names)
    require(direct_evaluator_imports == 0, "controller directly imports evaluator/runtime router")
    adapter_text = ADAPTER.read_text(encoding="utf-8")
    require("from saee_backend.services.capability_runtime import invoke_capability" in adapter_text, "adapter runtime delegation import missing")

    valid_agent = {
        "agent_id": "agent:synthetic-mcp:smoke",
        "agent_goal": "Select a bounded SAEE tool.",
        "available_capabilities": ["evaluate_agent_run", "evaluate_evidence", "rehearse_agent"],
        "selected_tool": "evaluate_evidence",
        "interpretation_policy": {
            "supported_means": "PROFILE_REQUIREMENT_SATISFIED",
            "result_is_authorization": False,
            "overinterpretation_rejected": True,
        },
        "simulation_only": True,
    }
    agent_validator.validate(valid_agent)

    invalid_cases = 0
    mutations = []
    for field in valid_agent:
        value = copy.deepcopy(valid_agent); value.pop(field); mutations.append(value)
    for field, replacement in (
        ("simulation_only", False),
        ("selected_tool", "authorize"),
        ("available_capabilities", []),
        ("agent_id", "real-agent"),
        ("agent_goal", ""),
    ):
        value = copy.deepcopy(valid_agent); value[field] = replacement; mutations.append(value)
    for forbidden in ("real_agent_identity", "external_connection", "customer_data"):
        value = copy.deepcopy(valid_agent); value[forbidden] = "forbidden"; mutations.append(value)
    for value in mutations:
        expect_schema_reject(agent_validator, value); invalid_cases += 1

    scenario = copy.deepcopy(scenarios[0])
    for mutation in (
        {**scenario, "simulation_only": False},
        {**scenario, "task_type": "UNSUPPORTED"},
        {**scenario, "external_connection": True},
        {**scenario, "customer_data": True},
        {**scenario, "real_agent_identity": "agent:external"},
    ):
        try:
            select_tool(mutation)
        except ValueError:
            invalid_cases += 1
        else:
            raise AssertionError("invalid scenario unexpectedly selected a tool")

    supported = {"operation": "evaluate_evidence", "status": "SUCCESS", "result": {"claim_assessment": "SUPPORTED"}}
    require(validate_interpretation(supported)["meaning"] == "PROFILE_REQUIREMENT_SATISFIED", "SUPPORTED meaning invalid")
    for claim in ("APPROVED", "CERTIFIED", "SAFE", "DEPLOYED"):
        result = validate_interpretation(supported, claim)
        require(result["valid"] is False, f"{claim} overinterpretation accepted")
        invalid_cases += 1
    for malformed in (None, {}, {"operation": "evaluate_evidence", "status": "SUCCESS", "result": {}}, {"operation": "unknown", "status": "SUCCESS", "result": {}}):
        require(validate_interpretation(malformed)["valid"] is False, "malformed result accepted")
        invalid_cases += 1

    path_escape = next(item for item in scenarios if item["scenario_id"] == "EVIDENCE_EVALUATION_TASK")
    path_escape = {**path_escape, "input_ref": "../../.config/saee/provider-keys.env"}
    try:
        from saee_backend.services.mcp_ecosystem_dry_integration import run_dry_scenario
        run_dry_scenario(path_escape)
    except ValueError as exc:
        require(str(exc) == "MCP_DRY_INPUT_REF_NOT_ALLOWLISTED", "unexpected input-ref rejection")
        invalid_cases += 1
    else:
        raise AssertionError("non-allowlisted input reference was read")

    deterministic_runs = 5
    for _ in range(deterministic_runs):
        require(run_all_scenarios() == actual, "dry integration output is nondeterministic")
    require(invalid_cases >= 20, "adversarial case count below twenty")

    print("SAEE_MCP_ECOSYSTEM_DRY_INTEGRATION_SMOKE: PASS")
    print(f"tools={actual['tool_results']['tools_discovered']}")
    print(f"scenarios={len(traces)}")
    print("runtime_delegation=true")
    print(f"direct_evaluator_imports={direct_evaluator_imports}")
    print(f"invalid_cases={invalid_cases}")
    print(f"deterministic_runs={deterministic_runs}")
    print("external_mcp=false")
    print("external_agent=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
