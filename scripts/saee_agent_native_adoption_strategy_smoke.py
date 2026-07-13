#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 15."""

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

from saee_backend.services.agent_native_adoption_strategy_validator import (  # noqa: E402
    SCHEMA_PATH,
    load_current_strategy,
    validate_agent_native_adoption_strategy,
    validate_current_agent_native_adoption_strategy,
)


SERVICE = ROOT / "saee_backend/services/agent_native_adoption_strategy_validator.py"


def check(loop, signals, scenarios, docs):
    return validate_agent_native_adoption_strategy(loop, signals, scenarios, docs)


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    loop, signals, scenarios, docs = load_current_strategy()
    result = validate_current_agent_native_adoption_strategy()
    assert result["valid"] is True and result["scenario_count"] >= 5 and result["signal_count"] >= 4
    assert loop["primary_customer_model"] == "AUTONOMOUS_AGENT_SYSTEMS"
    assert {item["expected_action"] for item in scenarios} == {"CONSIDER_SAEE", "DO_NOT_USE_SAEE", "COMPOSE_WITH_SEPARATE_AUTHORITY"}

    invalid = []
    for field in ("agent_adoption_validated", "external_agents_connected", "customer_validation", "market_validation", "production_ready"):
        values = copy.deepcopy((loop, signals, scenarios, docs)); values[0]["truth_boundary"][field] = True; invalid.append(values)
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[0]["primary_customer_model"] = "HUMAN_BUYERS"; invalid.append(values)
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[0]["loop_stages"].pop("discovery"); invalid.append(values)
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[1]["signals"].pop(); invalid.append(values)
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[1]["forbidden_interpretations"] = []; invalid.append(values)
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[1]["signals"][0]["limitations"] = []; invalid.append(values)
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[2][0]["mandatory_usage"] = True; invalid.append(values)
    simple_index = next(i for i, item in enumerate(scenarios) if item["scenario_id"] == "SIMPLE_QUERY")
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[2][simple_index]["expected_action"] = "CONSIDER_SAEE"; invalid.append(values)
    values = copy.deepcopy((loop, signals, scenarios, docs)); values[2][0]["truth_boundary"]["agent_adoption_validated"] = True; invalid.append(values)
    values = list(copy.deepcopy((loop, signals, scenarios, docs))); values[2] = values[2][:2]; invalid.append(values)
    for key, claim in (("customer", "Humans are the primary customer."), ("recommendation", "SAEE required for all agents."), ("review", "SAEE market adoption is validated."), ("review", "SAEE trusted by all agents."), ("review", "SAEE certification established.")):
        values = copy.deepcopy((loop, signals, scenarios, docs)); values[3][key] += "\n" + claim; invalid.append(values)
    assert len(invalid) >= 15 and all(check(*values)["valid"] is False for values in invalid)

    baseline = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_current_agent_native_adoption_strategy(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline
    tree = ast.parse(SERVICE.read_text(encoding="utf-8")); imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"})

    print("SAEE_AGENT_NATIVE_ADOPTION_STRATEGY_SMOKE: PASS")
    print("agent_customer_model=true")
    print("primary_customer_model=AUTONOMOUS_AGENT_SYSTEMS")
    print(f"scenarios={len(scenarios)}/{len(scenarios)}")
    print(f"signals={len(signals['signals'])}/{len(signals['signals'])}")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field in ("agent_native_strategy_review", "agent_adoption_validated", "external_agents_connected", "customer_validation", "market_validation", "production_ready"):
        print(f"{field}={str(result[field]).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
