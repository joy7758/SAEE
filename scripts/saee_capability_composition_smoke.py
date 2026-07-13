#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 16."""

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

from saee_backend.services.capability_composition_validator import (  # noqa: E402
    CONTEXT_SCHEMA_PATH,
    load_current_composition,
    validate_capability_composition,
    validate_current_capability_composition,
)


SERVICE = ROOT / "saee_backend/services/capability_composition_validator.py"


def main() -> int:
    schema = json.loads(CONTEXT_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    model, matrix, scenarios, docs = load_current_composition()
    result = validate_current_capability_composition()
    assert result["valid"] is True and result["capability_layer_count"] >= 5 and result["scenario_count"] >= 5
    assert {item["expected_result"] for item in scenarios} == {"VALID_COMPOSITION", "REJECTED_BOUNDARY_VIOLATION", "ALLOWED_INCOMPLETE_CONTEXT", "MISSING_CONTEXT_FLAGGED"}

    invalid = []
    values = copy.deepcopy((model, matrix, scenarios, docs)); values[0]["role"] = "authorization_authority"; invalid.append(values)
    for boundary in ("SAEE_NOT_AUTHORIZATION", "SAEE_NOT_POLICY_ENFORCEMENT", "SAEE_NOT_OBSERVABILITY", "SAEE_NOT_EXECUTION"):
        values = copy.deepcopy((model, matrix, scenarios, docs)); values[0]["replacement_boundary"].remove(boundary); invalid.append(values)
    for field in ("external_agents_connected", "agent_adoption_validated", "marketplace_listed", "interoperability_claimed", "standards_claimed", "production_ready"):
        values = copy.deepcopy((model, matrix, scenarios, docs)); values[0]["truth_boundary"][field] = True; invalid.append(values)
    for field in ("external_interoperability_tested", "external_systems_connected", "standards_compliance_claimed", "production_ready"):
        values = copy.deepcopy((model, matrix, scenarios, docs)); values[1]["truth_boundary"][field] = True; invalid.append(values)
    values = copy.deepcopy((model, matrix, scenarios, docs)); values[1]["invalid_relation"]["relation"] = "COMPLEMENT"; invalid.append(values)
    values = copy.deepcopy((model, matrix, scenarios, docs)); values[2][0]["decision_context"]["ownership_boundary"]["saee_authority"] = True; invalid.append(values)
    values = copy.deepcopy((model, matrix, scenarios, docs)); values[2][0]["expected_result"] = "SAEE_AUTHORIZED_EXECUTION"; invalid.append(values)
    values = list(copy.deepcopy((model, matrix, scenarios, docs))); values[2] = values[2][:2]; invalid.append(values)
    for key, claim in (("integration", "SAEE replaces IAM."), ("integration", "SAEE replaces policy."), ("integration", "SAEE controls execution."), ("integration", "SAEE is universal authority."), ("integration", "SAEE interoperability is established.")):
        values = copy.deepcopy((model, matrix, scenarios, docs)); values[3][key] += "\n" + claim; invalid.append(values)
    assert len(invalid) >= 15 and all(validate_capability_composition(*values)["valid"] is False for values in invalid)

    baseline = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_current_capability_composition(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline
    tree = ast.parse(SERVICE.read_text(encoding="utf-8")); imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"})

    print("SAEE_CAPABILITY_COMPOSITION_SMOKE: PASS")
    print("composition_model=true")
    print("boundary_model=true")
    print("interop_matrix=true")
    print("decision_context_separation=true")
    print(f"capability_layers={result['capability_layer_count']}/{result['capability_layer_count']}")
    print(f"scenarios={len(scenarios)}/{len(scenarios)}")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field in ("capability_composition_strategy", "external_agents_connected", "agent_adoption_validated", "marketplace_listed", "interoperability_claimed", "production_ready"):
        print(f"{field}={str(result[field]).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
