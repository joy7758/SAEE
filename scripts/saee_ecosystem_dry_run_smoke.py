#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 11.1 ecosystem dry run."""

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

from saee_backend.services.ecosystem_dry_run import run_ecosystem_dry_run  # noqa: E402
from saee_backend.services.ecosystem_dry_run_validator import (  # noqa: E402
    validate_current_ecosystem_dry_run,
    validate_ecosystem_dry_run,
)


PARTICIPANT_SCHEMA = ROOT / "schemas/saee-synthetic-ecosystem-participant.schema.v0.1.json"
FEEDBACK_SCHEMA = ROOT / "schemas/saee-ecosystem-dry-run-feedback.schema.v0.1.json"
PARTICIPANTS = ROOT / "agent-interface/ecosystem/dry-run-participants"
SCENARIOS = ROOT / "agent-interface/ecosystem/dry-run-scenarios"
RESULT = ROOT / "agent-interface/ecosystem/saee-ecosystem-dry-run-result.v0.1.json"
SERVICES = [ROOT / "saee_backend/services/ecosystem_dry_run.py", ROOT / "saee_backend/services/ecosystem_dry_run_validator.py"]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    participant_schema, feedback_schema = load(PARTICIPANT_SCHEMA), load(FEEDBACK_SCHEMA)
    Draft202012Validator.check_schema(participant_schema)
    Draft202012Validator.check_schema(feedback_schema)
    participants = [load(path) for path in sorted(PARTICIPANTS.glob("*.json"))]
    scenarios = [load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    assert len(participants) >= 3 and len({item["participant_type"] for item in participants}) >= 3
    assert all(not list(Draft202012Validator(participant_schema).iter_errors(item)) for item in participants)
    assert len(scenarios) >= 5 and all(item["external_execution"] is False for item in scenarios)

    generated = run_ecosystem_dry_run()
    stored = load(RESULT)
    assert generated == stored
    current = validate_current_ecosystem_dry_run()
    assert current["valid"] is True and current["reason_codes"] == []
    assert len(stored["feedback_records"]) >= 3
    assert all(not list(Draft202012Validator(feedback_schema).iter_errors(item)) for item in stored["feedback_records"])
    assert sum(item["result"] == "PASS" for item in stored["scenario_results"]) == 3
    assert sum(item["result"] == "REJECTED" for item in stored["scenario_results"]) == 2

    invalid = []
    for field in ("external_validation", "external_agents_connected", "customer_validated", "market_validation", "marketplace_listed", "adoption_validated", "production_ready", "external_parties_contacted", "network_accessed", "subprocess_started", "external_execution"):
        item = copy.deepcopy(stored); item["truth_boundary"][field] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["truth_boundary"]["participants_invited"] = 1; invalid.append(item)
    item = copy.deepcopy(stored); item["synthetic_only"] = False; invalid.append(item)
    item = copy.deepcopy(stored); item["evidence_boundary"]["dry_run_is_adoption"] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["feedback_records"][0]["credentials"] = "forbidden"; invalid.append(item)
    assert len(invalid) >= 12
    assert all(validate_ecosystem_dry_run(item)["valid"] is False for item in invalid)

    baseline = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(run_ecosystem_dry_run(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    forbidden_imports = {"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"}
    for path in SERVICES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
        assert not imports.intersection(forbidden_imports)

    print("SAEE_ECOSYSTEM_DRY_RUN_SMOKE: PASS")
    print(f"participants={len(participants)}/{len(participants)}")
    print(f"participant_types={len({item['participant_type'] for item in participants})}/3")
    print(f"scenarios={len(scenarios)}/{len(scenarios)}")
    print(f"feedback_records={len(stored['feedback_records'])}/{len(stored['feedback_records'])}")
    print("scenario_pass=3/3")
    print("scenario_rejected=2/2")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field, value in stored["truth_boundary"].items():
        print(f"{field}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

