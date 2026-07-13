#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 14.1."""

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

from saee_backend.services.entry_decision_simulation import (  # noqa: E402
    _scenario_validator,
    run_entry_decision_simulation,
)
from saee_backend.services.entry_decision_simulation_validator import (  # noqa: E402
    validate_current_entry_decision_simulation,
    validate_entry_decision_simulation,
)


SCHEMA = ROOT / "schemas/saee-entry-decision-simulation.schema.v0.1.json"
SCENARIOS = ROOT / "agent-interface/ecosystem/entry-decision-simulation"
FIXTURES = ROOT / "agent-interface/ecosystem/entry-decision-simulation-fixtures"
RESULT = ROOT / "agent-interface/ecosystem/saee-entry-decision-simulation-result.v0.1.json"
CURRENT = ROOT / "agent-interface/ecosystem/saee-external-validation-entry-decision.v0.1.json"
SERVICES = [ROOT / "saee_backend/services/entry_decision_simulation.py", ROOT / "saee_backend/services/entry_decision_simulation_validator.py"]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def mutate(source, path, value):
    item = copy.deepcopy(source)
    target = item
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return item


def main() -> int:
    Draft202012Validator.check_schema(load(SCHEMA))
    scenarios = [load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    validator = _scenario_validator()
    assert len(scenarios) >= 7 and all(not list(validator.iter_errors(item)) for item in scenarios)
    stored, generated = load(RESULT), run_entry_decision_simulation()
    assert stored == generated and validate_current_entry_decision_simulation()["valid"] is True
    results = stored["scenario_results"]
    assert {"HOLD", "CONDITIONAL_ENTRY_REVIEW", "ENTRY_READY"}.issubset({item["decision_result"] for item in results})
    assert stored["authorization_distribution"]["execution_authorized_count"] == 0
    assert all(item["execution_authorized"] is False for item in results)
    current = load(CURRENT)
    assert current["decision"] == "HOLD" and current["truth_boundary"]["execution_authorized"] is False

    fixtures = [load(path) for path in sorted(FIXTURES.glob("*.json"))]
    invalid = [mutate(stored, fixture["path"], fixture["value"]) for fixture in fixtures]
    item = copy.deepcopy(stored); item.pop("limitations"); invalid.append(item)
    item = copy.deepcopy(stored); item["simulation_version"] = "9.9"; invalid.append(item)
    item = copy.deepcopy(stored); item["entry_decision_reference"] = "https://example.invalid/fake"; invalid.append(item)
    item = copy.deepcopy(stored); item["scenario_results"] = item["scenario_results"][:2]; invalid.append(item)
    item = copy.deepcopy(stored); item["scenario_results"][0]["matched_expected"] = False; invalid.append(item)
    item = copy.deepcopy(stored); item["decision_distribution"].pop("HOLD"); invalid.append(item)
    item = copy.deepcopy(stored); item["authorization_distribution"]["execution_authorized_count"] = 1; invalid.append(item)
    item = copy.deepcopy(stored); item["authorization_distribution"]["execution_not_authorized_count"] = 6; invalid.append(item)
    item = copy.deepcopy(stored); item["limitations"] = []; invalid.append(item)
    item = copy.deepcopy(stored); item["truth_boundary"]["real_participants"] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["unexpected"] = True; invalid.append(item)
    assert len(invalid) >= 15 and all(validate_entry_decision_simulation(item)["valid"] is False for item in invalid)

    baseline = json.dumps(stored, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(run_entry_decision_simulation(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline
    imports = set()
    for path in SERVICES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"})

    print("SAEE_ENTRY_DECISION_SIMULATION_SMOKE: PASS")
    print(f"scenario_cases={len(scenarios)}/{len(scenarios)}")
    print("decision_branches=3/3")
    print("hold_behavior=true")
    print("conditional_behavior=true")
    print("entry_ready_authorizes_execution=false")
    print(f"negative_fixtures={len(fixtures)}/{len(fixtures)}")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field, value in stored["truth_boundary"].items(): print(f"{field}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
