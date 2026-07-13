#!/usr/bin/env python3
"""Offline adversarial smoke for SAEE Internal Agent Pilot Plan v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.internal_agent_pilot_validator import (  # noqa: E402
    SCENARIO_DIR,
    synthetic_evidence_for_scenario,
    validate_internal_pilot_evidence,
    validate_internal_pilot_repository,
    validate_internal_pilot_scenario,
)


SERVICE_PATHS = [
    ROOT / "saee_backend/services/internal_agent_pilot.py",
    ROOT / "saee_backend/services/internal_agent_pilot_validator.py",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_no_runtime_escape() -> None:
    forbidden = {"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"}
    for path in SERVICE_PATHS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        assert not (imports & forbidden), f"forbidden import in {path.name}: {sorted(imports & forbidden)}"


def main() -> int:
    result = validate_internal_pilot_repository()
    assert result["valid"] is True, result
    assert result["scenario_count"] >= 4 and result["agent_type_count"] >= 4
    assert all(result[key] is True for key in ("internal_only", "scope_defined", "evidence_boundary", "recommendation_boundary"))
    assert result["pilot_executed"] is True and result["real_internal_execution"] is True
    assert all(result[key] is False for key in ("external_validation", "external_participants", "customer_data", "production_execution", "adoption_validated", "production_ready"))

    scenarios = [load(path) for path in sorted(SCENARIO_DIR.glob("*.json"))]
    evidences = [synthetic_evidence_for_scenario(scenario) for scenario in scenarios]
    assert all(validate_internal_pilot_evidence(value)["valid"] for value in evidences)
    assert all(value["execution_observation"]["status"] == "NOT_EXECUTED" for value in evidences)
    assert all(value["recommendation"] == "HUMAN_REVIEW_REQUIRED" for value in evidences)

    invalid_scenarios = []
    base = scenarios[0]
    for key in ("customer_data", "production_execution", "adoption_validated", "production_ready", "external_validation", "external_participants", "pilot_executed"):
        value = copy.deepcopy(base); value["truth_boundary"][key] = True; invalid_scenarios.append(value)
    for key in ("network_access", "external_world_actions", "customer_data"):
        value = copy.deepcopy(base); value["execution_environment"][key] = True; invalid_scenarios.append(value)
    value = copy.deepcopy(base); value["agent_type"] = "generic_agent"; invalid_scenarios.append(value)
    value = copy.deepcopy(base); value["workflow_scope"]["forbidden"].remove("customer_data"); invalid_scenarios.append(value)
    value = copy.deepcopy(base); value["evidence_policy"]["raw_secret_storage"] = True; invalid_scenarios.append(value)
    value = copy.deepcopy(base); value["scenario"]["evaluation_dimensions"] = ["execution"]; invalid_scenarios.append(value)
    value = copy.deepcopy(base); value["limitations"] = []; invalid_scenarios.append(value)

    invalid_evidences = []
    evidence = evidences[0]
    for key in ("external_validation_claim", "customer_claim", "adoption_claim", "production_claim", "deployment_authorized"):
        value = copy.deepcopy(evidence); value["truth_boundary"][key] = True; invalid_evidences.append(value)
    value = copy.deepcopy(evidence); value["recommendation"] = "DEPLOY"; invalid_evidences.append(value)
    value = copy.deepcopy(evidence); value["limitations"] = []; invalid_evidences.append(value)

    invalid_cases = len(invalid_scenarios) + len(invalid_evidences)
    assert invalid_cases >= 15
    assert all(validate_internal_pilot_scenario(value)["valid"] is False for value in invalid_scenarios)
    assert all(validate_internal_pilot_evidence(value)["valid"] is False for value in invalid_evidences)

    baseline = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_internal_pilot_repository(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline
    assert_no_runtime_escape()

    print("SAEE_INTERNAL_AGENT_PILOT_SMOKE: PASS")
    print("scenarios=4/4")
    print("agent_types=4/4")
    print("scenario_template_not_executed_evidence=4/4")
    print(f"invalid_cases={invalid_cases}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("internal_agent_pilot=true")
    print("pilot_executed=true")
    print("real_internal_execution=true")
    print("external_validation=false")
    print("external_participants=false")
    print("customer_data=false")
    print("production_execution=false")
    print("adoption_validated=false")
    print("production_ready=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
