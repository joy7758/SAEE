#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 12 design contracts."""

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

from saee_backend.services.external_validation_design_validator import (  # noqa: E402
    validate_current_external_validation_design,
    validate_external_validation_design,
)


DESIGN = ROOT / "agent-interface/ecosystem/saee-controlled-external-validation-design.v0.1.json"
SCHEMAS = [
    ROOT / "schemas/saee-external-validation-participant.schema.v0.1.json",
    ROOT / "schemas/saee-external-validation-scope.schema.v0.1.json",
    ROOT / "schemas/saee-external-validation-evidence.schema.v0.1.json",
]
DOCUMENTS = [
    ROOT / "docs/ecosystem/SAEE_CONTROLLED_EXTERNAL_VALIDATION_DESIGN.md",
    ROOT / "docs/ecosystem/SAEE_EXTERNAL_VALIDATION_EXIT_CRITERIA.md",
    ROOT / "docs/ecosystem/SAEE_EXTERNAL_VALIDATION_TERMINATION_POLICY.md",
    ROOT / "docs/ecosystem/SAEE_ECOSYSTEM_VALIDATION_EVIDENCE_BOUNDARY.md",
]
SERVICE = ROOT / "saee_backend/services/external_validation_design_validator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    validators = []
    for path in SCHEMAS:
        schema = load(path); Draft202012Validator.check_schema(schema); validators.append(Draft202012Validator(schema))
    participant = {"participant_id": "participant:future-example", "participant_type": "developer", "authorization_status": "NOT_AUTHORIZED", "validation_scope": "scope:future-example", "allowed_operations": ["capability_discovery_test"], "limitations": ["Design fixture only; not an invitation or authorization."]}
    scope = {"scope_id": "scope:future-example", "allowed": ["capability_discovery_test", "integration_test", "interpretation_test", "compatibility_feedback"], "forbidden": ["production_execution", "customer_data_access", "private_system_access", "external_side_effects"], "external_side_effects": False, "customer_data_allowed": False, "permission_expansion_allowed": False}
    evidence = {"evidence_id": "external-validation-evidence:future-example", "participant_ref": "participant:future-example", "scope_ref": "scope:future-example", "evidence_type": "compatibility_result", "version_information": "synthetic-design-fixture-v0.1", "limitations": ["No external observation exists."], "contains_private_data": False, "claim_boundary": "compatibility_observation_only"}
    assert not list(validators[0].iter_errors(participant))
    assert not list(validators[1].iter_errors(scope))
    assert not list(validators[2].iter_errors(evidence))
    assert len(DOCUMENTS) >= 4 and all(path.is_file() for path in DOCUMENTS)

    design = load(DESIGN)
    result = validate_current_external_validation_design()
    assert result["valid"] is True and result["reason_codes"] == []

    invalid = []
    for field in ("external_validation", "external_agents_connected", "customer_validated", "market_validation", "adoption_validated", "production_ready", "external_parties_contacted", "customer_data_received", "external_execution"):
        item = copy.deepcopy(design); item["truth_boundary"][field] = True; invalid.append(item)
    item = copy.deepcopy(design); item["truth_boundary"]["participants_invited"] = 1; invalid.append(item)
    item = copy.deepcopy(design); item["truth_boundary"]["participants_authorized"] = 1; invalid.append(item)
    item = copy.deepcopy(design); item["participant_model"]["participants_authorized"] = 1; invalid.append(item)
    item = copy.deepcopy(design); item["scope_model"]["allowed"].append("production_execution"); invalid.append(item)
    item = copy.deepcopy(design); item["evidence_model"]["allowed"].append("adoption_claim"); invalid.append(item)
    item = copy.deepcopy(design); item["exit_criteria"]["criteria_met"] = True; invalid.append(item)
    item = copy.deepcopy(design); item["termination_policy"]["immediate_stop_conditions"].remove("CREDENTIAL_EXPOSURE"); invalid.append(item)
    item = copy.deepcopy(design); item["participant_model"]["schema_reference"] = "https://example.invalid/schema.json"; invalid.append(item)
    item = copy.deepcopy(design); item["unexpected"] = True; invalid.append(item)
    assert len(invalid) >= 15
    assert all(validate_external_validation_design(item)["valid"] is False for item in invalid)

    baseline = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_current_external_validation_design(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"})

    print("SAEE_EXTERNAL_VALIDATION_DESIGN_SMOKE: PASS")
    print(f"documents={len(DOCUMENTS)}/{len(DOCUMENTS)}")
    print(f"schemas={len(SCHEMAS)}/{len(SCHEMAS)}")
    print("design_object=true")
    print("participant_schema_valid=true")
    print("scope_schema_valid=true")
    print("evidence_schema_valid=true")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("external_validation_design=true")
    print("external_validation=false")
    print("participants_invited=0")
    print("participants_authorized=0")
    print("external_agents_connected=false")
    print("customer_validated=false")
    print("market_validation=false")
    print("adoption_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

