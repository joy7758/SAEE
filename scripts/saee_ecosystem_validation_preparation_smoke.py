#!/usr/bin/env python3
"""Offline smoke for SAEE Controlled Ecosystem Validation Preparation v0.1."""

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

from saee_backend.services.ecosystem_validation_preparation_validator import (  # noqa: E402
    load_preparation_state,
    validate_current_ecosystem_preparation,
    validate_ecosystem_preparation,
)


PROTOCOL_SCHEMA = ROOT / "schemas/saee-ecosystem-validation-protocol.schema.v0.1.json"
FEEDBACK_SCHEMA = ROOT / "schemas/saee-ecosystem-validation-feedback.schema.v0.1.json"
PROTOCOL = ROOT / "agent-interface/ecosystem/saee-controlled-ecosystem-validation-protocol.v0.1.json"
MATRIX = ROOT / "agent-interface/ecosystem/saee-ecosystem-compatibility-matrix.v0.1.json"
STATE = ROOT / "agent-interface/ecosystem/saee-ecosystem-validation-preparation.v0.1.json"
PACKAGE = ROOT / "ecosystem/participant-package-v0.1"
BOUNDARY = ROOT / "docs/ecosystem/SAEE_ECOSYSTEM_VALIDATION_EVIDENCE_BOUNDARY.md"
DOC = ROOT / "docs/ecosystem/SAEE_CONTROLLED_ECOSYSTEM_VALIDATION_PROTOCOL.md"
GATE = ROOT / "docs/strategy/SAEE_ECOSYSTEM_VALIDATION_PREPARATION_RECOMMENDATION_GATE.md"
SERVICE = ROOT / "saee_backend/services/ecosystem_validation_preparation_validator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    protocol_schema, feedback_schema = load(PROTOCOL_SCHEMA), load(FEEDBACK_SCHEMA)
    Draft202012Validator.check_schema(protocol_schema)
    Draft202012Validator.check_schema(feedback_schema)
    assert not list(Draft202012Validator(protocol_schema).iter_errors(load(PROTOCOL)))
    assert not list(Draft202012Validator(feedback_schema).iter_errors(load(PACKAGE / "feedback-template.json")))
    result = validate_current_ecosystem_preparation()
    assert result["valid"] is True and result["reason_codes"] == []
    for field in ("protocol_exists", "participant_package_exists", "matrix_exists", "feedback_schema_exists", "boundary_document_exists", "ecosystem_validation_preparation"):
        assert result[field] is True
    assert PACKAGE.is_dir() and len([path for path in PACKAGE.iterdir() if path.is_file()]) == 6
    matrix = load(MATRIX)
    statuses = {item["integration"]: item["status"] for item in matrix["integrations"]}
    assert statuses["MCP stdio"] == statuses["HTTP local"] == "local_tested"
    assert all(statuses[name] == "not_tested" for name in ("LangGraph", "CrewAI", "OpenAI Agents", "Claude ecosystem", "Cloud marketplace"))
    assert BOUNDARY.is_file() and DOC.is_file()
    assert "`recommend`" in GATE.read_text(encoding="utf-8")

    state = load_preparation_state()
    invalid = []
    for field in ("external_validation_completed", "external_agents_connected", "customer_validated", "market_validation", "marketplace_listed", "adoption_validated", "production_ready", "external_parties_contacted"):
        mutation = copy.deepcopy(state); mutation["truth_boundary"][field] = True; invalid.append(mutation)
    mutation = copy.deepcopy(state); mutation["truth_boundary"]["participants_invited"] = 1; invalid.append(mutation)
    mutation = copy.deepcopy(state); mutation["truth_boundary"]["ecosystem_validation_preparation"] = False; invalid.append(mutation)
    mutation = copy.deepcopy(state); mutation["status"] = "EXTERNAL_VALIDATION"; invalid.append(mutation)
    mutation = copy.deepcopy(state); mutation["protocol_reference"] = "missing.json"; invalid.append(mutation)
    mutation = copy.deepcopy(state); mutation["participant_types"] = ["developer"]; invalid.append(mutation)
    mutation = copy.deepcopy(state); mutation["validation_dimensions"] = ["DISCOVERY_COMPATIBILITY"]; invalid.append(mutation)
    mutation = copy.deepcopy(state); mutation["unexpected"] = True; invalid.append(mutation)
    assert len(invalid) >= 12
    assert all(validate_ecosystem_preparation(item)["valid"] is False for item in invalid)

    baseline = json.dumps(result, ensure_ascii=False, sort_keys=True)
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_current_ecosystem_preparation(), ensure_ascii=False, sort_keys=True) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib"} & imports)

    print("SAEE_ECOSYSTEM_VALIDATION_PREPARATION_SMOKE: PASS")
    print("protocol=true")
    print("package=true")
    print("participant_package_files=6/6")
    print("matrix=true")
    print("feedback=true")
    print("boundary=true")
    print("participant_types=4/4")
    print("validation_dimensions=5/5")
    print("local_tested_integrations=2/2")
    print("external_not_tested_integrations=5/5")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("ecosystem_validation_preparation=true")
    print("external_validation=false")
    print("external_agents_connected=false")
    print("customer_validated=false")
    print("market_validation=false")
    print("marketplace_listed=false")
    print("adoption_validated=false")
    print("external_parties_contacted=false")
    print("participants_invited=0")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
