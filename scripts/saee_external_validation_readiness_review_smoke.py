#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 13 readiness review."""

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

from saee_backend.services.external_validation_readiness_review import (  # noqa: E402
    build_readiness_review,
    validate_current_readiness_review,
    validate_readiness_review,
)


REVIEW_SCHEMA = ROOT / "schemas/saee-external-validation-readiness-review.schema.v0.1.json"
EVIDENCE_SCHEMA = ROOT / "schemas/saee-external-validation-readiness-evidence.schema.v0.1.json"
MATRIX = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-matrix.v0.1.json"
GAPS = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-gaps.v0.1.json"
RESULT = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-review.v0.1.json"
FIXTURES = ROOT / "agent-interface/ecosystem/readiness-review-fixtures"
SERVICE = ROOT / "saee_backend/services/external_validation_readiness_review.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def apply_fixture(review, fixture):
    item = copy.deepcopy(review); mutation = fixture["mutation"]
    for key, value in mutation.items():
        if key.startswith("truth_boundary."):
            item["truth_boundary"][key.split(".", 1)[1]] = value
        elif key == "remove_review_dimension":
            item["review_dimensions"].remove(value)
        elif key == "remove_evidence_ref":
            item["evidence_refs"].remove(value)
    return item


def main() -> int:
    review_schema, evidence_schema = load(REVIEW_SCHEMA), load(EVIDENCE_SCHEMA)
    Draft202012Validator.check_schema(review_schema); Draft202012Validator.check_schema(evidence_schema)
    matrix, gaps, stored = load(MATRIX), load(GAPS), load(RESULT)
    assert len(matrix["dimensions"]) >= 5 and {item["dimension"] for item in matrix["dimensions"]} == {"TECHNICAL_CAPABILITY", "DOCUMENTATION", "VALIDATION_PROCESS", "SECURITY_BOUNDARY", "OPERATIONAL_READINESS"}
    assert len(gaps["gaps"]) == 5 and gaps["critical_open_gap_count"] == 3 and gaps["open_required_gap_count"] == 5
    assert stored == build_readiness_review(matrix, gaps)
    assert stored["decision"] == "HOLD" and stored["truth_boundary"]["execution_authorized"] is False
    assert validate_current_readiness_review()["valid"] is True

    evidence = {"evidence_id":"readiness-evidence:simulation-result","evidence_type":"validation_simulation_result","reference":"agent-interface/ecosystem/saee-external-validation-simulation-result.v0.1.json","supports_dimension":"VALIDATION_PROCESS","limitations":["Synthetic simulation only."],"external_claim":False}
    assert not list(Draft202012Validator(evidence_schema).iter_errors(evidence))
    fake_adoption = copy.deepcopy(evidence); fake_adoption["evidence_type"] = "adoption_claim"
    assert list(Draft202012Validator(evidence_schema).iter_errors(fake_adoption))

    fixtures = [load(path) for path in sorted(FIXTURES.glob("*.json"))]
    assert len(fixtures) >= 6
    invalid = [apply_fixture(stored, fixture) for fixture in fixtures]
    for field in ("external_validation_execution", "execution_authorized", "external_agents_connected", "customer_validated", "adoption_validated", "marketplace_listed", "production_ready"):
        item = copy.deepcopy(stored); item["truth_boundary"][field] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["truth_boundary"]["participants_invited"] = 1; invalid.append(item)
    item = copy.deepcopy(stored); item["decision"] = "GO"; invalid.append(item)
    item = copy.deepcopy(stored); item["evidence_refs"] = ["https://example.invalid/fake.json", *item["evidence_refs"]]; invalid.append(item)
    item = copy.deepcopy(stored); item["unexpected"] = True; invalid.append(item)
    assert len(invalid) >= 15 and all(validate_readiness_review(item)["valid"] is False for item in invalid)

    no_critical = copy.deepcopy(gaps)
    for gap in no_critical["gaps"]:
        if gap["severity"] == "CRITICAL": gap["status"] = "RESOLVED"
    assert build_readiness_review(matrix, no_critical)["decision"] == "CONDITIONAL_GO"
    all_clear = copy.deepcopy(no_critical)
    for gap in all_clear["gaps"]: gap["status"] = "RESOLVED"
    all_pass = copy.deepcopy(matrix)
    for dimension in all_pass["dimensions"]: dimension["status"] = "PASS"
    go = build_readiness_review(all_pass, all_clear)
    assert go["decision"] == "GO" and go["truth_boundary"]["execution_authorized"] is False

    baseline = json.dumps(stored, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(build_readiness_review(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8")); imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"})

    print("SAEE_EXTERNAL_VALIDATION_READINESS_REVIEW_SMOKE: PASS")
    print(f"dimensions={len(matrix['dimensions'])}/{len(matrix['dimensions'])}")
    print("evidence_rules=true")
    print("gap_model=true")
    print("decision_engine=true")
    print("decision=HOLD")
    print("blocking_gaps=5/5")
    print("critical_blocking_gaps=3/3")
    print(f"fixtures={len(fixtures)}/{len(fixtures)}")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("go_authorizes_execution=false")
    for field, value in stored["truth_boundary"].items():
        print(f"{field}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
