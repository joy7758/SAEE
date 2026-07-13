#!/usr/bin/env python3
"""Offline architecture smoke for SAEE Stateful Rehearsal Runtime v0.1."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "agent-interface/rehearsal/saee-stateful-rehearsal-runtime-architecture.v0.1.json"
EXECUTION_SCHEMA = ROOT / "agent-interface/rehearsal/saee-agent-execution-result.v0.1.schema.json"
SCENARIO_SCHEMA = ROOT / "agent-interface/rehearsal/saee-stateful-rehearsal-scenario.v0.1.schema.json"
OBSERVATION_SCHEMA = ROOT / "agent-interface/rehearsal/saee-stateful-rehearsal-observation.v0.1.schema.json"
SCENARIOS = ROOT / "agent-interface/rehearsal/scenarios/stateful-runtime-v0.1"
TOOLS = ROOT / "agent-interface/rehearsal/saee-tool-simulator.v0.1.json"
GATEWAY_OBSERVATION = ROOT / "agent-interface/rehearsal/saee-volcengine-multi-vendor-observation.v0.1.json"
QIANFAN_GATEWAY_OBSERVATION = ROOT / "agent-interface/rehearsal/saee-qianfan-multi-vendor-observation.v0.1.json"
DOC = ROOT / "docs/architecture/SAEE_STATEFUL_REHEARSAL_RUNTIME_ARCHITECTURE.md"
REPORT = ROOT / "docs/architecture/SAEE_REHEARSAL_REPORT_FORMAT.md"
GATE = ROOT / "docs/strategy/SAEE_STATEFUL_REHEARSAL_RUNTIME_ARCHITECTURE_RECOMMENDATION_GATE.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def keys(value):
    if isinstance(value, dict):
        return set(value) | {item for child in value.values() for item in keys(child)}
    if isinstance(value, list):
        return {item for child in value for item in keys(child)}
    return set()


def main() -> int:
    required = (ARCH, EXECUTION_SCHEMA, SCENARIO_SCHEMA, OBSERVATION_SCHEMA, TOOLS, GATEWAY_OBSERVATION, QIANFAN_GATEWAY_OBSERVATION, DOC, REPORT, GATE)
    for path in required:
        assert path.is_file(), path
    execution_schema = load(EXECUTION_SCHEMA)
    scenario_schema = load(SCENARIO_SCHEMA)
    observation_schema = load(OBSERVATION_SCHEMA)
    for schema in (execution_schema, scenario_schema, observation_schema):
        Draft202012Validator.check_schema(schema)

    arch = load(ARCH)
    components = arch["components"]
    expected_components = {"agent_adapter", "state_environment", "scenario_model", "tool_simulator", "observation_contract", "evidence_pipeline", "report_format", "multi_agent_evaluation"}
    assert set(components) == expected_components
    assert all(item["defined"] is True and (ROOT / item["ref"]).is_file() for item in components.values())
    assert arch["required_runtime_flags"] == {"real_model_execution": True, "external_world_actions": False, "customer_data_used": False, "production_execution": False}
    assert arch["truth_boundary"] == {
        "architecture_only": True,
        "multi_provider_runtime_implemented": False,
        "new_provider_adapter_implemented": False,
        "existing_qianfan_runtime_modified": False,
        "second_evaluator_created": False,
        "external_world_actions": False,
        "customer_data_used": False,
        "production_execution": False,
        "production_ready": False,
    }
    providers = {item["provider"]: item for item in arch["provider_matrix"]}
    assert set(providers) == {"baidu_qianfan", "openai_compatible", "volcengine_ark", "anthropic_compatible", "future_provider"}
    assert providers["baidu_qianfan"]["adapter_status"] == "existing_controlled_stateful_adapter_validated"
    assert providers["baidu_qianfan"]["provider_gateway_separated_from_model_vendor"] is True
    assert providers["baidu_qianfan"]["multi_vendor_catalog_observed"] is True
    assert providers["baidu_qianfan"]["multi_vendor_rehearsal_validated"] is False
    assert providers["openai_compatible"]["adapter_status"] == "design_target_not_implemented"
    assert providers["anthropic_compatible"]["adapter_status"] == "design_only_not_configured_not_tested"

    gateway = load(GATEWAY_OBSERVATION)
    vendor_rows = {item["model_vendor"]: item for item in gateway["vendor_observations"]}
    assert vendor_rows["deepseek"]["live_inference_observed"] is True
    assert vendor_rows["deepseek"]["function_calling_observed"] is True
    assert vendor_rows["zhipu"]["live_inference_observed"] is True
    assert vendor_rows["zhipu"]["function_calling_observed"] is True
    assert vendor_rows["moonshot"]["catalog_visible"] is True
    assert vendor_rows["moonshot"]["live_inference_observed"] is False
    assert gateway["model_catalog"]["gateway_identity_is_model_vendor"] is False
    assert gateway["truth_boundary"]["provider_gateway_separated_from_model_vendor"] is True

    qianfan_gateway = load(QIANFAN_GATEWAY_OBSERVATION)
    assert qianfan_gateway["catalog_observation"]["model_count"] == 35
    assert qianfan_gateway["truth_boundary"]["provider_gateway_separated_from_model_vendor"] is True
    assert qianfan_gateway["truth_boundary"]["multi_vendor_catalog_observed"] is True
    assert qianfan_gateway["truth_boundary"]["multi_vendor_rehearsal_validated"] is False

    scenario_validator = Draft202012Validator(scenario_schema, format_checker=FormatChecker())
    scenario_paths = sorted(SCENARIOS.glob("*.json"))
    assert len(scenario_paths) == 5
    scenarios = [load(path) for path in scenario_paths]
    for scenario in scenarios:
        errors = list(scenario_validator.iter_errors(scenario))
        assert not errors, errors[0].message if errors else ""
        assert scenario["runtime_requirement"]["real_model_execution"] is True
        assert scenario["execution_status"] == "DESIGN_ONLY_NOT_EXECUTED"
    assert len({item["scenario_id"] for item in scenarios}) == 5

    tools = load(TOOLS)
    assert [item["name"] for item in tools["tools"]] == ["code_repository", "test_runner", "deployment_simulator", "database_simulator", "customer_ticket_system"]
    assert all(item["external_execution"] is False for item in tools["tools"])

    digest = "a" * 64
    execution_fixture = {
        "result_version": "0.1", "execution_id": "execution:synthetic-001", "agent_id": "agent:provider-test-001",
        "provider": "volcengine_ark", "model_vendor": "deepseek", "model": "design-model",
        "started_at": "2026-07-12T00:00:00Z", "completed_at": "2026-07-12T00:00:01Z", "execution_status": "COMPLETED",
        "messages_summary": [{"sequence": 0, "role": "user", "summary": "Synthetic task supplied.", "summary_digest": digest, "raw_content_stored": False}],
        "tool_calls": [],
        "outputs": [{"sequence": 1, "role": "assistant", "summary": "Synthetic result returned.", "summary_digest": digest, "raw_content_stored": False}],
        "state_change_refs": [],
        "truth_boundary": {"real_model_execution": True, "synthetic_world": True, "external_world_actions": False, "customer_data_used": False, "production_execution": False, "private_model_state_stored": False},
    }
    observation_fixture = {
        "observation_version": "0.1", "event_id": "event:synthetic-001", "agent_id": "agent:provider-test-001", "timestamp": "2026-07-12T00:00:01Z",
        "action": "Return a bounded synthetic result.", "tool_call": None, "input_summary": "Synthetic input summary.", "output_summary": "Synthetic output summary.",
        "state_transition": {"revision_before": 0, "revision_after": 1, "state_before_digest": digest, "state_after_digest": digest, "external_effect": False},
        "risk_signal": "NONE",
        "truth_boundary": {"observation_only": True, "raw_provider_payload_stored": False, "private_model_state_stored": False, "customer_data_used": False, "external_world_actions": False, "production_execution": False},
    }
    assert not list(Draft202012Validator(execution_schema, format_checker=FormatChecker()).iter_errors(execution_fixture))
    assert not list(Draft202012Validator(observation_schema, format_checker=FormatChecker()).iter_errors(observation_fixture))
    forbidden_keys = {"chain_of_thought", "hidden_reasoning", "private_reasoning", "reasoning_tokens"}
    assert not keys(execution_schema).intersection(forbidden_keys)
    assert not keys(observation_schema).intersection(forbidden_keys)

    invalid_cases = 0
    for field, bad in (("real_model_execution", False), ("external_world_actions", True), ("customer_data_used", True), ("production_execution", True)):
        mutation = copy.deepcopy(scenarios[0]); mutation["runtime_requirement"][field] = bad
        assert list(scenario_validator.iter_errors(mutation)); invalid_cases += 1
    mutation = copy.deepcopy(scenarios[0]); mutation["execution_status"] = "EXECUTED"; assert list(scenario_validator.iter_errors(mutation)); invalid_cases += 1
    mutation = copy.deepcopy(scenarios[0]); mutation["available_tools"].append("shell"); assert list(scenario_validator.iter_errors(mutation)); invalid_cases += 1
    mutation = copy.deepcopy(observation_fixture); mutation["chain_of_thought"] = "forbidden"; assert list(Draft202012Validator(observation_schema).iter_errors(mutation)); invalid_cases += 1
    mutation = copy.deepcopy(execution_fixture); mutation["truth_boundary"]["private_model_state_stored"] = True; assert list(Draft202012Validator(execution_schema).iter_errors(mutation)); invalid_cases += 1
    assert invalid_cases == 8

    architecture_doc = DOC.read_text(encoding="utf-8")
    report_doc = REPORT.read_text(encoding="utf-8")
    for marker in ("Provider Gateway 与 Model Vendor", "existing evidence_adequacy evaluator", "multi_provider_runtime_implemented=false"):
        assert marker in architecture_doc
    for allowed in ("CONTINUE", "REPLAN", "HUMAN_REVIEW_REQUIRED", "STOP"):
        assert allowed in report_doc
    for forbidden in ("APPROVED", "CERTIFIED", "SAFE"):
        assert f"禁止：`APPROVED`" in report_doc and forbidden in report_doc

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    assert not imported_roots(Path(__file__)).intersection(forbidden_imports)
    print("SAEE_STATEFUL_REHEARSAL_ARCHITECTURE_SMOKE: PASS")
    print("agent_adapter=true")
    print("state_environment=true")
    print("scenario_model=true")
    print("scenario_cases=5/5")
    print("tool_simulator=true")
    print("simulated_tools=5/5")
    print("observation_contract=true")
    print("evidence_pipeline=true")
    print("report_format=true")
    print("multi_agent_evaluation=true")
    print("invalid_cases=8/8")
    print("qianfan_existing_adapter_reused=true")
    print("qianfan_multi_vendor_catalog_observed=true")
    print("qianfan_multi_vendor_rehearsal_validated=false")
    print("deepseek_via_ark_inference_observed=true")
    print("deepseek_via_ark_function_calling_observed=true")
    print("zhipu_via_ark_inference_observed=true")
    print("zhipu_via_ark_function_calling_observed=true")
    print("moonshot_via_ark_inference_observed=false")
    print("multi_provider_runtime_implemented=false")
    print("external_world_actions=false")
    print("customer_data_used=false")
    print("production_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
