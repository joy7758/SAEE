#!/usr/bin/env python3
"""Offline deterministic smoke for Phase 13.1 execution controls."""

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

from saee_backend.services.external_validation_execution_simulation_validator import (  # noqa: E402
    validate_current_execution_simulation,
    validate_execution_simulation,
)
from saee_backend.services.external_validation_execution_simulator import run_execution_simulation_suite  # noqa: E402


RESULT = ROOT / "agent-interface/ecosystem/saee-external-validation-execution-simulation-result.v0.1.json"
READINESS = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-review.v0.1.json"
SCENARIOS = ROOT / "agent-interface/ecosystem/execution-simulation"
SCHEMAS = [ROOT / "schemas/saee-external-validation-execution-request.schema.v0.1.json", ROOT / "schemas/saee-external-validation-execution-simulation.schema.v0.1.json", ROOT / "schemas/saee-external-validation-execution-evidence.schema.v0.1.json"]
SERVICES = [ROOT / "saee_backend/services/external_validation_execution_simulator.py", ROOT / "saee_backend/services/external_validation_execution_simulation_validator.py"]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in SCHEMAS: Draft202012Validator.check_schema(load(path))
    readiness = load(READINESS)
    assert readiness["decision"] == "HOLD" and readiness["truth_boundary"]["execution_authorized"] is False
    scenarios = [load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    assert len(scenarios) >= 6
    generated, stored = run_execution_simulation_suite(), load(RESULT)
    assert generated == stored and validate_current_execution_simulation()["valid"] is True
    results = [item["result"] for item in stored["scenario_results"]]
    assert results.count("BLOCKED") >= 2 and results.count("TERMINATED") >= 2 and results.count("SIMULATION_ALLOWED") == 1
    current = next(item for item in stored["scenario_results"] if item["scenario_id"] == "CURRENT_HOLD_BLOCK")
    assert current["result"] == "BLOCKED" and current["reason_code"] == "READINESS_HOLD"
    simulated_go = next(item for item in stored["scenario_results"] if item["scenario_id"] == "SIMULATED_GO_PATH")
    assert simulated_go["result"] == "SIMULATION_ALLOWED" and simulated_go["truth_boundary"]["execution_authorized"] is False
    assert all(item["external_validation_completed"] is False for item in stored["evidence_records"])

    invalid = []
    for field in ("external_validation", "execution_authorized", "real_participants", "customer_data", "adoption_validated", "production_ready", "network_accessed", "subprocess_started", "external_execution"):
        item = copy.deepcopy(stored); item["truth_boundary"][field] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["truth_boundary"]["participants_invited"] = 1; invalid.append(item)
    item = copy.deepcopy(stored); item["scenario_results"][0]["truth_boundary"]["execution_authorized"] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["scenario_results"][0]["matched_expected"] = False; invalid.append(item)
    item = copy.deepcopy(stored); item["evidence_records"][0]["external_validation_completed"] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["scenario_results"] = item["scenario_results"][:1]; invalid.append(item)
    item = copy.deepcopy(stored); item["evidence_records"] = []; invalid.append(item)
    item = copy.deepcopy(stored); item["unexpected"] = True; invalid.append(item)
    assert len(invalid) >= 15 and all(validate_execution_simulation(item)["valid"] is False for item in invalid)

    baseline = json.dumps(stored, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(run_execution_simulation_suite(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    forbidden = {"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"}
    for path in SERVICES:
        tree = ast.parse(path.read_text(encoding="utf-8")); imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
        assert not imports.intersection(forbidden)

    print("SAEE_EXTERNAL_VALIDATION_EXECUTION_SIMULATION_SMOKE: PASS")
    print(f"scenario_cases={len(scenarios)}/{len(scenarios)}")
    print(f"blocked_cases={results.count('BLOCKED')}/{results.count('BLOCKED')}")
    print(f"terminated_cases={results.count('TERMINATED')}/{results.count('TERMINATED')}")
    print("simulation_allowed_cases=1/1")
    print("current_hold_blocked=true")
    print("fake_authorization_blocked=true")
    print("external_execution_blocked=true")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field, value in stored["truth_boundary"].items():
        print(f"{field}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

