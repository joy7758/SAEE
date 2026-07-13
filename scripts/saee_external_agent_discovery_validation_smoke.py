#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 10.7 discovery validation."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.external_agent_discovery_validator import (  # noqa: E402
    ExternalAgentDiscoveryValidationError,
    build_discovery_validation_result,
    evaluate_adversarial_claim,
    evaluate_discovery_scenario,
)


SCENARIO_SCHEMA = ROOT / "schemas/saee-external-agent-discovery-validation.schema.v0.1.json"
RESULT_SCHEMA = ROOT / "schemas/saee-external-agent-discovery-validation-result.schema.v0.1.json"
SCENARIO_ROOT = ROOT / "agent-interface/discovery/external-agent-validation"
ADVERSARIAL_PATH = SCENARIO_ROOT / "adversarial-cases.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/discovery/saee-external-agent-discovery-validation-result.v0.1.json"
DOC_PATH = ROOT / "docs/research/SAEE_EXTERNAL_AGENT_DISCOVERY_VALIDATION.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_EXTERNAL_AGENT_DISCOVERY_VALIDATION_ALPHA_RECOMMENDATION_GATE.md"
SERVICE_PATH = ROOT / "saee_backend/services/external_agent_discovery_validator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expect_error(value: dict) -> None:
    try:
        evaluate_discovery_scenario(value)
    except ExternalAgentDiscoveryValidationError:
        return
    raise AssertionError("invalid discovery scenario accepted")


def main() -> int:
    required = (SCENARIO_SCHEMA, RESULT_SCHEMA, ADVERSARIAL_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, SERVICE_PATH)
    assert all(path.is_file() for path in required)
    scenario_schema = load(SCENARIO_SCHEMA)
    result_schema = load(RESULT_SCHEMA)
    Draft202012Validator.check_schema(scenario_schema)
    Draft202012Validator.check_schema(result_schema)

    scenario_files = sorted(path for path in SCENARIO_ROOT.glob("*.json") if path.name != ADVERSARIAL_PATH.name)
    scenarios = [load(path) for path in scenario_files]
    assert len(scenarios) >= 6
    assert all(not list(Draft202012Validator(scenario_schema).iter_errors(item)) for item in scenarios)
    generated = build_discovery_validation_result(scenarios)
    checked = load(RESULT_PATH)
    assert generated == checked
    assert not list(Draft202012Validator(result_schema).iter_errors(checked))
    assert all(item["result"] == "PASS" for item in generated["scenario_results"])
    assert generated["discovery_success"] == {"passed": 6, "total": 6, "rate": 1.0}
    assert generated["understanding_success"] == {"passed": 6, "total": 6, "rate": 1.0}
    assert generated["selection_accuracy"] == {"passed": 6, "total": 6, "rate": 1.0}
    assert generated["boundary_preservation"] == {"passed": 6, "total": 6, "rate": 1.0}

    adversarial = load(ADVERSARIAL_PATH)["cases"]
    assert len(adversarial) >= 10
    rejected = [evaluate_adversarial_claim(case) for case in adversarial]
    assert all(item["rejected"] is True for item in rejected)
    required_cases = {"SAEE_IS_CERTIFICATION_AGENT", "SAEE_APPROVES_DEPLOYMENT", "SAEE_IS_SECURITY_AUTHORITY", "SAEE_REQUIRED_FOR_ALL_TASKS"}
    assert required_cases.issubset({item["case_id"] for item in rejected})

    invalid_contracts: list[dict] = []
    mutation = copy.deepcopy(scenarios[0]); mutation["agent_context"]["saee_memory"] = True; invalid_contracts.append(mutation)
    mutation = copy.deepcopy(scenarios[0]); mutation["agent_context"]["real_external_agent"] = True; invalid_contracts.append(mutation)
    mutation = copy.deepcopy(scenarios[0]); mutation["available_public_materials"].append("README.md"); invalid_contracts.append(mutation)
    mutation = copy.deepcopy(scenarios[0]); mutation["expected_action"] = "CONSIDER_SAEE"; invalid_contracts.append(mutation)
    for value in invalid_contracts[:3]:
        expect_error(value)
    mismatch = evaluate_discovery_scenario(invalid_contracts[3])
    assert mismatch["result"] == "FAIL" and "DISCOVERY_ACTION_SELECTION_MISMATCH" in mismatch["reason_codes"]
    invalid_cases = len(adversarial) + len(invalid_contracts)
    assert invalid_cases >= 10

    false_fields = ("external_agents_connected", "real_external_agent", "customer_data", "market_validation", "adoption_validated", "external_agent_preference_validated", "production_ready")
    assert generated["truth_boundary"]["external_agent_discovery_validation"] is True
    assert generated["truth_boundary"]["synthetic_agent_like_callers"] is True
    assert all(generated["truth_boundary"][field] is False for field in false_fields)

    doc = DOC_PATH.read_text(encoding="utf-8")
    assert "This validation evaluates discovery and interpretation behavior of synthetic agent-like callers. It does not establish external adoption." in doc
    assert "该验证评估合成智能体调用者的发现和理解行为，不代表外部采用。" in doc
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        repeated = build_discovery_validation_result([copy.deepcopy(item) for item in scenarios])
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "openai", "anthropic"} & imported)

    print("SAEE_EXTERNAL_AGENT_DISCOVERY_VALIDATION_SMOKE: PASS")
    print(f"scenario_cases={len(scenarios)}/6")
    print(f"adversarial_cases={len(adversarial)}/10")
    print(f"invalid_cases={invalid_cases}/{invalid_cases}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("discovery_success=6/6")
    print("understanding_success=6/6")
    print("selection_accuracy=6/6")
    print("boundary_preservation=6/6")
    print("external_agent_discovery_validation=true")
    print("external_agents_connected=false")
    print("real_external_agent=false")
    print("customer_data=false")
    print("market_validation=false")
    print("adoption_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
