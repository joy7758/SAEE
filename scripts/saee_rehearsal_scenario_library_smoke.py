#!/usr/bin/env python3
"""Offline deterministic validation for SAEE Rehearsal Scenario Library v0.2."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "agent-interface/rehearsal/scenario-library.schema.v0.2.json"
LIBRARY_DIR = ROOT / "agent-interface/rehearsal/scenarios/library-v0.2"
LEGACY_PATH = ROOT / "agent-interface/rehearsal/mvp/coding-agent-release-rehearsal.v0.1.json"
DOC_PATH = ROOT / "docs/product/SAEE_REHEARSAL_SCENARIO_LIBRARY_V0_2.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_REHEARSAL_SCENARIO_LIBRARY_V0_2_RECOMMENDATION_GATE.md"


EXPECTED_CATEGORIES = {
    "CODING_RELEASE",
    "RESEARCH_EVIDENCE_REVIEW",
    "BUSINESS_OPERATION",
    "CUSTOMER_SUPPORT",
    "SECURITY_BOUNDARY",
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def runtime_projection(scenario: dict[str, Any]) -> dict[str, Any]:
    """Project a library entry into the existing runtime input boundary."""
    return {
        "task": {
            "objective": scenario["agent_goal"],
            "constraints": copy.deepcopy(scenario["constraints"]),
            "failure_injection": copy.deepcopy(scenario["failure_injection"]),
        },
        "environment_state": copy.deepcopy(scenario["initial_state"]),
        "available_tools": copy.deepcopy(scenario["available_tools"]),
    }


def main() -> int:
    for path in (SCHEMA_PATH, LIBRARY_DIR, LEGACY_PATH, DOC_PATH, GATE_PATH):
        assert path.exists(), path
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    paths = sorted(LIBRARY_DIR.glob("*/scenario.json"))
    assert len(paths) == 5, paths

    scenarios = [load_json(path) for path in paths]
    for scenario in scenarios:
        errors = sorted(validator.iter_errors(scenario), key=lambda error: list(error.absolute_path))
        assert not errors, f"{scenario['scenario_id']}: {errors[0].message if errors else ''}"
        assert scenario["compatibility"]["runtime_input_contract_compatible"] is True
        assert scenario["compatibility"]["runtime_redesign_required"] is False
        assert set(scenario["available_tools"]) == {item["name"] for item in scenario["tools"]}
        assert set(scenario["risk_conditions"]) == {item["risk_id"] for item in scenario["risks"]}
        assert all(item["not_probability_measurement"] is True for item in scenario["risks"])
        assert all(item["external_effect"] is False for item in scenario["tools"])
        assert scenario["truth_boundary"] == {
            "real_model_execution_contract": True,
            "synthetic_environment": True,
            "external_world_actions": False,
            "customer_data": False,
            "production_execution": False,
            "production_ready": False,
            "benchmark_public": False,
            "market_validation": False,
        }
        projection = runtime_projection(scenario)
        assert projection["task"]["objective"] == scenario["agent_goal"]
        assert projection["environment_state"] == scenario["initial_state"]
        assert projection["available_tools"] == scenario["available_tools"]

    assert {item["category"] for item in scenarios} == EXPECTED_CATEGORIES
    assert len({item["scenario_id"] for item in scenarios}) == 5
    coding = next(item for item in scenarios if item["category"] == "CODING_RELEASE")
    legacy = load_json(LEGACY_PATH)
    assert coding["compatibility"]["legacy_scenario_ref"] == "agent-interface/rehearsal/mvp/coding-agent-release-rehearsal.v0.1.json"
    assert coding["initial_state"] == legacy["initial_state"]
    assert coding["available_tools"] == legacy["available_tools"]
    assert coding["compatibility"]["executable_by_current_release_world"] is True
    candidates = [item for item in scenarios if item["category"] != "CODING_RELEASE"]
    assert all(item["compatibility"]["executable_by_current_release_world"] is False for item in candidates)
    research = next(item for item in scenarios if item["category"] == "RESEARCH_EVIDENCE_REVIEW")
    assert research["compatibility"]["scenario_tool_implementation_required"] is False
    assert set(research["available_tools"]) == {"evidence_search", "citation_checker", "claim_validator", "uncertainty_checker"}
    security = next(item for item in scenarios if item["category"] == "SECURITY_BOUNDARY")
    assert security["compatibility"]["scenario_tool_implementation_required"] is False
    assert set(security["available_tools"]) == {"log_search", "policy_checker", "incident_summary", "access_request_simulator"}
    operations = [item for item in scenarios if item["category"] in {"BUSINESS_OPERATION", "CUSTOMER_SUPPORT"}]
    assert all(item["compatibility"]["scenario_tool_implementation_required"] is False for item in operations)
    assert not [item for item in scenarios if item["compatibility"]["scenario_tool_implementation_required"] is True]

    invalid_cases = 0
    mutations: list[dict[str, Any]] = []
    mutation = copy.deepcopy(coding); mutation.pop("risks"); mutations.append(mutation)
    mutation = copy.deepcopy(coding); mutation["constraints"] = []; mutations.append(mutation)
    mutation = copy.deepcopy(coding); mutation["truth_boundary"]["production_ready"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(coding); mutation["truth_boundary"]["external_world_actions"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(coding); mutation["truth_boundary"]["customer_data"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(coding); mutation["risks"][0]["not_probability_measurement"] = False; mutations.append(mutation)
    mutation = copy.deepcopy(coding); mutation["tools"][0]["external_effect"] = True; mutations.append(mutation)
    for mutation in mutations:
        assert list(validator.iter_errors(mutation))
        invalid_cases += 1
    assert invalid_cases == 7

    baseline = canonical([runtime_projection(item) for item in scenarios])
    for _ in range(5):
        reloaded = [load_json(path) for path in paths]
        assert canonical([runtime_projection(item) for item in reloaded]) == baseline

    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in (*paths, DOC_PATH, GATE_PATH))
    for forbidden in ("benchmark_public=true", "market_validation=true", "production_ready=true", "models certified", "deployment approved"):
        assert forbidden not in combined_text
    assert "Scenarios evaluate controlled agent behavior. They do not certify models or approve deployment." in DOC_PATH.read_text(encoding="utf-8")

    print("SAEE_REHEARSAL_SCENARIO_LIBRARY_SMOKE: PASS")
    print("scenario_count=5/5")
    print("categories=5/5")
    print("schema_valid=5/5")
    print("runtime_input_contract_compatible=5/5")
    print("current_release_world_executable=1/5")
    print("scenario_tool_implementation_required=0/5")
    print("research_world_tools_implemented=true")
    print("security_world_tools_implemented=true")
    print("operations_world_tools_implemented=true")
    print("legacy_coding_scenario_compatible=true")
    print("invalid_cases=7/7")
    print("deterministic_runs=5/5")
    print("benchmark_public=false")
    print("market_validation=false")
    print("external_world_actions=false")
    print("customer_data=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError) as exc:
        print(f"SAEE_REHEARSAL_SCENARIO_LIBRARY_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
