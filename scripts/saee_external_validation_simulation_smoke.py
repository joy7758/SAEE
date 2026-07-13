#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 12.1 simulation."""

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

from saee_backend.services.external_validation_simulation import run_external_validation_simulation  # noqa: E402
from saee_backend.services.external_validation_simulation_validator import (  # noqa: E402
    validate_current_external_validation_simulation,
    validate_external_validation_simulation,
)


PARTICIPANTS = ROOT / "agent-interface/ecosystem/external-validation-simulation"
SCENARIOS = ROOT / "agent-interface/ecosystem/external-validation-scenarios"
RESULT = ROOT / "agent-interface/ecosystem/saee-external-validation-simulation-result.v0.1.json"
SCHEMAS = [
    ROOT / "schemas/saee-external-validation-simulation-participant.schema.v0.1.json",
    ROOT / "schemas/saee-external-validation-simulation-evidence.schema.v0.1.json",
    ROOT / "schemas/saee-external-validation-simulation-feedback.schema.v0.1.json",
]
SERVICES = [ROOT / "saee_backend/services/external_validation_simulation.py", ROOT / "saee_backend/services/external_validation_simulation_validator.py"]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in SCHEMAS:
        Draft202012Validator.check_schema(load(path))
    participant_schema = load(SCHEMAS[0])
    participants = [load(path) for path in sorted(PARTICIPANTS.glob("sim-*.json"))]
    scenarios = [load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    assert len(participants) >= 3 and len({item["participant_type"] for item in participants}) >= 3
    assert all(not list(Draft202012Validator(participant_schema).iter_errors(item)) for item in participants)
    assert len(scenarios) >= 6 and all(item["external_execution"] is False for item in scenarios)

    generated, stored = run_external_validation_simulation(), load(RESULT)
    assert generated == stored
    current = validate_current_external_validation_simulation()
    assert current["valid"] is True and current["reason_codes"] == []
    assert len(stored["feedback_records"]) >= 3 and len(stored["evidence_records"]) == 6
    outcomes = {item["scenario_id"]: item["result"] for item in stored["scenario_results"]}
    assert outcomes == {"ADOPTION_CLAIM_ATTEMPT":"REJECTED", "AUTHORIZED_SUCCESS_FLOW":"PASS", "CREDENTIAL_EXPOSURE_ATTEMPT":"TERMINATED", "CUSTOMER_DATA_ATTEMPT":"TERMINATED", "SCOPE_VIOLATION_REQUEST":"REJECTED", "UNAUTHORIZED_PARTICIPANT":"BLOCKED"}

    invalid = []
    for field in ("external_validation", "real_participants", "external_agents_connected", "customer_data", "customer_validated", "adoption_validated", "marketplace_listed", "market_validation", "production_ready", "network_accessed", "subprocess_started", "external_execution"):
        item = copy.deepcopy(stored); item["truth_boundary"][field] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["truth_boundary"]["participants_invited"] = 1; invalid.append(item)
    item = copy.deepcopy(stored); item["exit_review"]["real_validation_exit_criteria_met"] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["feedback_records"][0]["credentials"] = "forbidden"; invalid.append(item)
    item = copy.deepcopy(stored); item["scenario_results"][0]["matched_expected"] = False; invalid.append(item)
    item = copy.deepcopy(stored); item["unexpected"] = True; invalid.append(item)
    assert len(invalid) >= 15
    assert all(validate_external_validation_simulation(item)["valid"] is False for item in invalid)

    baseline = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(run_external_validation_simulation(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    forbidden = {"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"}
    for path in SERVICES:
        tree = ast.parse(path.read_text(encoding="utf-8")); imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
        assert not imports.intersection(forbidden)

    print("SAEE_EXTERNAL_VALIDATION_SIMULATION_SMOKE: PASS")
    print(f"participants={len(participants)}/{len(participants)}")
    print(f"participant_types={len({item['participant_type'] for item in participants})}/3")
    print(f"scenario_cases={len(scenarios)}/{len(scenarios)}")
    print(f"feedback_records={len(stored['feedback_records'])}/{len(stored['feedback_records'])}")
    print(f"evidence_records={len(stored['evidence_records'])}/{len(stored['evidence_records'])}")
    print("authorized_success=1/1")
    print("blocked=1/1")
    print("rejected=2/2")
    print("terminated=2/2")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field, value in stored["truth_boundary"].items():
        print(f"{field}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
