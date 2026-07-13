#!/usr/bin/env python3
"""Offline smoke for SAEE Agent Ecosystem Integration Examples Alpha."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_integration_evaluator import evaluate_integration_scenario
from saee_backend.services.capability_http_adapter import process_http_request


SCENARIOS = ROOT / "agent-interface/integration/examples"
EXAMPLES = ROOT / "examples/agent-integrations"
SCHEMA = ROOT / "schemas/saee-agent-result-interpretation.schema.v0.1.json"
EXPECTED = {
    "correct-mcp-agent.json": "PASS",
    "correct-http-agent.json": "PASS",
    "result-overinterpretation-agent.json": "FAIL",
    "wrong-capability-agent.json": "FAIL",
    "authorization-confusion-agent.json": "FAIL",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    files = {path.name for path in SCENARIOS.glob("*.json")}
    require(files == set(EXPECTED), "integration scenario set drift")
    results = {}
    for filename, expected in EXPECTED.items():
        value = load(SCENARIOS / filename)
        result = evaluate_integration_scenario(value)
        require(result["result"] == expected and value["expected_outcome"] == expected, f"unexpected result: {filename}")
        results[filename] = result
    require(sum(result["result"] == "PASS" for result in results.values()) == 2, "valid case count invalid")
    require(sum(result["result"] == "FAIL" for result in results.values()) == 3, "boundary case count invalid")

    correct = load(SCENARIOS / "correct-mcp-agent.json")
    mutations = []
    candidate = copy.deepcopy(correct); candidate.pop("transport"); mutations.append(candidate)
    candidate = copy.deepcopy(correct); candidate["transport"] = "PUBLIC_HTTP"; mutations.append(candidate)
    candidate = copy.deepcopy(correct); candidate["discovered_capability_id"] = "unknown"; mutations.append(candidate)
    candidate = copy.deepcopy(correct); candidate["selected_operation"] = "authorize_deployment"; mutations.append(candidate)
    candidate = copy.deepcopy(correct); candidate["interpretation"]["certified"] = True; mutations.append(candidate)
    invalid_results = [evaluate_integration_scenario(value) for value in mutations]
    require(all(result["result"] == "FAIL" for result in invalid_results), "invalid mutation accepted")

    required_example_files = [
        "README.md",
        "mcp-client-example/README.md", "mcp-client-example/example_config.json", "mcp-client-example/client_flow.md",
        "http-agent-example/README.md", "http-agent-example/request.json", "http-agent-example/response.json", "http-agent-example/client_flow.md",
        "framework-agent-example/README.md", "framework-agent-example/generic_agent_adapter.py", "framework-agent-example/client_flow.md",
    ]
    require(all((EXAMPLES / ref).is_file() for ref in required_example_files), "integration example file missing")
    mcp = load(EXAMPLES / "mcp-client-example/example_config.json")
    require(mcp["transport"] == "stdio" and mcp["external_server"] is False, "MCP example boundary invalid")
    request = load(EXAMPLES / "http-agent-example/request.json")
    http_status, http_response = process_http_request("/capabilities/evaluate-evidence", request, invoked_at="2026-07-12T15:10:10Z")
    require(http_status == 200 and http_response["result"]["claim_assessment"] == "SUPPORTED", "HTTP example not callable")
    projection = load(EXAMPLES / "http-agent-example/response.json")
    require(projection["runtime_status"] == http_response["status"] and projection["assessment"] == http_response["result"]["claim_assessment"], "HTTP response projection drift")

    module_path = EXAMPLES / "framework-agent-example/generic_agent_adapter.py"
    spec = importlib.util.spec_from_file_location("saee_generic_agent_adapter", module_path)
    require(spec is not None and spec.loader is not None, "framework example import failed")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    supported = module.interpret_saee_result({"status": "SUCCESS", "result": {"assessment": "SUPPORTED"}})
    insufficient = module.interpret_saee_result({"status": "SUCCESS", "result": {"assessment": "INSUFFICIENT_EVIDENCE"}})
    rejected = module.interpret_saee_result({"status": "REJECTED", "result": {}})
    unknown = module.interpret_saee_result({"status": "SUCCESS", "result": {}})
    require([supported["recommended_action"], insufficient["recommended_action"], unknown["recommended_action"], rejected["recommended_action"]] == ["CONTINUE", "REPLAN", "HUMAN_REVIEW_REQUIRED", "STOP"], "framework action mapping invalid")
    for value in (supported, insufficient, rejected, unknown):
        require(all(value[field] is False for field in ("approved", "certified", "safe", "deployed", "authorization_granted")), "framework overclaim")

    canonical = json.dumps(evaluate_integration_scenario(correct), sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(json.dumps(evaluate_integration_scenario(copy.deepcopy(correct)), sort_keys=True, separators=(",", ":")) == canonical, "integration evaluation non-deterministic")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in EXAMPLES.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".py"})
    for forbidden in ("adoption_validated=true", "marketplace_listed=true", "production_ready=true", "SAEE guarantees safety", "SAEE certifies"):
        require(forbidden not in combined, f"unsupported claim in examples: {forbidden}")

    print("SAEE_AGENT_ECOSYSTEM_INTEGRATION_SMOKE: PASS")
    print("examples=3/3")
    print("transports=2/2")
    print("scenario_cases=5/5")
    print("valid_cases=2/2")
    print("boundary_failures=3/3")
    print(f"invalid_cases={len(mutations)}/{len(mutations)}")
    print("deterministic_runs=5/5")
    print("interpretation_actions=4/4")
    print("external_agents_connected=false")
    print("customer_data=false")
    print("marketplace_listed=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
