#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 15.1."""

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

from saee_backend.services.agent_capability_marketplace_position_validator import (  # noqa: E402
    SCHEMA_PATH,
    load_current_positioning,
    validate_current_marketplace_positioning,
    validate_marketplace_positioning,
)


SERVICE = ROOT / "saee_backend/services/agent_capability_marketplace_position_validator.py"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    category, matrix, scenarios, docs, adoption = load_current_positioning()
    result = validate_current_marketplace_positioning()
    assert result["valid"] is True and result["category_count"] >= 1 and result["scenario_count"] >= 5
    assert {item["recommended_capability"] for item in scenarios} == {"SAEE", "AUTHORIZATION_SYSTEM", "OBSERVABILITY", "NONE"}

    invalid = []
    values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[0]["capability_type"] = "security_product"; invalid.append(values)
    values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[0]["composition_role"] = "authorization_authority"; invalid.append(values)
    values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[0]["not_replacements"].remove("AUTHORIZATION"); invalid.append(values)
    for field in ("marketplace_listed", "agent_adoption_validated", "external_agents_connected", "market_validation", "industry_standard_claimed", "production_ready"):
        values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[0]["truth_boundary"][field] = True; invalid.append(values)
    for field in ("marketplace_created", "marketplace_listed", "ranking_generated", "ecosystem_support_established", "agent_adoption_validated", "production_ready"):
        values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[1]["truth_boundary"][field] = True; invalid.append(values)
    values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[2][0]["discovery_trigger_mandatory"] = True; invalid.append(values)
    auth_index = next(i for i, item in enumerate(scenarios) if item["scenario_id"] == "AGENT_NEEDS_AUTHORIZATION")
    values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[2][auth_index]["recommended_capability"] = "SAEE"; invalid.append(values)
    values = list(copy.deepcopy((category, matrix, scenarios, docs, adoption))); values[2] = values[2][:2]; invalid.append(values)
    for key, claim in (("category", "SAEE replaces authorization."), ("review", "SAEE is marketplace leader."), ("review", "SAEE is industry standard."), ("review", "SAEE is trusted by all agents."), ("review", "SAEE ranked first.")):
        values = copy.deepcopy((category, matrix, scenarios, docs, adoption)); values[3][key] += "\n" + claim; invalid.append(values)
    assert len(invalid) >= 15 and all(validate_marketplace_positioning(*values)["valid"] is False for values in invalid)

    baseline = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_current_marketplace_positioning(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline
    tree = ast.parse(SERVICE.read_text(encoding="utf-8")); imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"})

    print("SAEE_AGENT_CAPABILITY_MARKETPLACE_POSITION_SMOKE: PASS")
    print("category_defined=true")
    print("capability_type=agent_reliability_layer")
    print("composition_role=decision_context_provider")
    print(f"categories={result['category_count']}/{result['category_count']}")
    print(f"scenarios={len(scenarios)}/{len(scenarios)}")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field in ("marketplace_position_review", "marketplace_listed", "agent_adoption_validated", "external_agents_connected", "market_validation", "production_ready"):
        print(f"{field}={str(result[field]).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
