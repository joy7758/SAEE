#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Phase 14 entry gate."""

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

from saee_backend.services.external_validation_entry_decision import (  # noqa: E402
    build_entry_decision,
    validate_current_entry_decision,
    validate_entry_decision,
)


DECISION_SCHEMA = ROOT / "schemas/saee-external-validation-entry-decision.schema.v0.1.json"
CLOSURE_SCHEMA = ROOT / "schemas/saee-gap-closure-evidence.schema.v0.1.json"
GAPS = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-gaps.v0.1.json"
RESULT = ROOT / "agent-interface/ecosystem/saee-external-validation-entry-decision.v0.1.json"
FIXTURES = ROOT / "agent-interface/ecosystem/entry-decision-fixtures"
SERVICE = ROOT / "saee_backend/services/external_validation_entry_decision.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verified_records(gaps):
    return [{"gap_id":gap["gap_id"],"previous_status":"OPEN","closure_evidence":[f"synthetic://phase14/{gap['gap_id'].lower()}"],"verification_method":"INDEPENDENT_REVIEW","independent_review":True,"review_status":"VERIFIED_CLOSED"} for gap in gaps["gaps"]]


def main() -> int:
    decision_schema, closure_schema = load(DECISION_SCHEMA), load(CLOSURE_SCHEMA)
    Draft202012Validator.check_schema(decision_schema); Draft202012Validator.check_schema(closure_schema)
    gaps, stored = load(GAPS), load(RESULT)
    assert stored == build_entry_decision() and validate_current_entry_decision()["valid"] is True
    assert stored["decision"] == "HOLD" and stored["gap_summary"] == {"required":5,"critical":3,"verified_closed":0}
    fixtures = [load(path) for path in sorted(FIXTURES.glob("*.json"))]
    assert len(fixtures) >= 6

    records = verified_records(gaps)
    critical_ids = {gap["gap_id"] for gap in gaps["gaps"] if gap["severity"] == "CRITICAL"}
    critical_records = [record for record in records if record["gap_id"] in critical_ids]
    conditional = build_entry_decision(gaps, critical_records, independent_review_completed=False)
    assert conditional["decision"] == "CONDITIONAL_ENTRY_REVIEW" and conditional["truth_boundary"]["execution_authorized"] is False
    ready = build_entry_decision(gaps, records, independent_review_completed=True)
    assert ready["decision"] == "ENTRY_READY" and ready["current_gaps"] == [] and ready["truth_boundary"]["execution_authorized"] is False
    fake_closure = copy.deepcopy(records[0]); fake_closure["closure_evidence"] = []
    try:
        build_entry_decision(gaps, [fake_closure], independent_review_completed=True)
    except ValueError:
        pass
    else:
        raise AssertionError("fake closure accepted")

    invalid = []
    for field in ("external_validation", "execution_authorized", "external_agents_connected", "customer_validated", "adoption_validated", "production_ready"):
        item = copy.deepcopy(stored); item["truth_boundary"][field] = True; invalid.append(item)
    item = copy.deepcopy(stored); item["truth_boundary"]["participants_invited"] = 1; invalid.append(item)
    item = copy.deepcopy(stored); item["decision"] = "ENTRY_READY"; invalid.append(item)
    item = copy.deepcopy(stored); item["gap_summary"]["verified_closed"] = 5; invalid.append(item)
    item = copy.deepcopy(stored); item["independent_review_required"] = False; invalid.append(item)
    item = copy.deepcopy(stored); item["readiness_reference"] = "https://example.invalid/fake.json"; invalid.append(item)
    item = copy.deepcopy(stored); item["evidence_summary"]["independently_verified_records"] = -1; invalid.append(item)
    item = copy.deepcopy(stored); item["current_gaps"] = []; invalid.append(item)
    item = copy.deepcopy(stored); item["limitations"] = []; invalid.append(item)
    item = copy.deepcopy(stored); item["unexpected"] = True; invalid.append(item)
    item = copy.deepcopy(ready); item["truth_boundary"]["execution_authorized"] = True; invalid.append(item)
    assert len(invalid) >= 15 and all(validate_entry_decision(item)["valid"] is False for item in invalid)

    baseline = json.dumps(stored, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(build_entry_decision(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8")); imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"})

    print("SAEE_EXTERNAL_VALIDATION_ENTRY_DECISION_SMOKE: PASS")
    print("decision_engine=true")
    print("gap_model=true")
    print("evidence_model=true")
    print(f"fixtures={len(fixtures)}/{len(fixtures)}")
    print("current_decision=HOLD")
    print("conditional_branch=CONDITIONAL_ENTRY_REVIEW")
    print("ready_branch=ENTRY_READY")
    print("entry_ready_authorizes_execution=false")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    for field, value in stored["truth_boundary"].items(): print(f"{field}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

