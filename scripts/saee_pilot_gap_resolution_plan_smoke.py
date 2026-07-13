#!/usr/bin/env python3
"""Offline smoke for SAEE Pilot Gap Resolution Planning v0.1."""

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

from saee_backend.services.pilot_gap_resolution_planner import (  # noqa: E402
    GAP_PLAN_DEPENDENCY_INVALID,
    GAP_PLAN_EXECUTION_CLAIM_FORBIDDEN,
    GAP_PLAN_FAKE_CLOSURE_FORBIDDEN,
    GAP_PLAN_FAKE_EVIDENCE_FORBIDDEN,
    GAP_PLAN_PILOT_AUTHORIZATION_FORBIDDEN,
    GAP_PLAN_READINESS_UPGRADE_FORBIDDEN,
    GAP_PLAN_REASSESSMENT_FORBIDDEN,
    GAP_PLAN_SOURCE_BLOCKER_COVERAGE_INVALID,
    validate_gap_resolution_result_truth,
    validate_pilot_gap_resolution_plan,
)


SCHEMA_PATH = ROOT / "agent-interface/integration/saee-pilot-gap-resolution-plan.schema.v0.1.json"
PLAN_PATH = ROOT / "agent-interface/integration/saee-pilot-gap-resolution-plan.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/integration/saee-pilot-gap-resolution-result.v0.1.json"
DOC_PATH = ROOT / "docs/commercial/SAEE_PILOT_GAP_RESOLUTION_PLAN.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PILOT_GAP_RESOLUTION_PLAN_RECOMMENDATION_GATE.md"
READINESS_DOC_PATH = ROOT / "docs/commercial/SAEE_EXTERNAL_AGENT_PILOT_READINESS_REVIEW.md"
VALIDATOR_PATH = ROOT / "saee_backend/services/pilot_gap_resolution_planner.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(candidate: dict, reason: str) -> None:
    result = validate_pilot_gap_resolution_plan(candidate)
    assert result["plan_valid"] is False
    assert result["reason_codes"] == [reason], result


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def _forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "system", "popen", "run", "Popen", "write_text", "write_bytes", "listen", "bind", "connect"
        }:
            found.add(node.func.attr)
    return found


def main() -> int:
    for path in (SCHEMA_PATH, PLAN_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, READINESS_DOC_PATH, VALIDATOR_PATH):
        assert path.is_file(), path

    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    plan = _load(PLAN_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(plan))
    assert not errors, [error.message for error in errors]

    valid = validate_pilot_gap_resolution_plan(plan)
    assert valid["plan_valid"] is True
    assert valid["gaps_total"] == 15
    assert valid["gaps_open"] == 15
    assert valid["gaps_closed"] == 0
    assert valid["evidence_acquired"] is False
    assert valid["reassessment_allowed"] is False

    gaps = plan["gaps"]
    assert len(gaps) == 15
    assert all(gap["current_status"] == "OPEN" for gap in gaps)
    assert all(gap["evidence_refs"] == [] for gap in gaps)
    assert len({gap["required_artifact_type"] for gap in gaps}) == 15
    assert {gap["category"] for gap in gaps} == {"IDENTITY", "SECURITY", "DATA", "RUNTIME", "HUMAN_GOVERNANCE"}

    invalid_cases: list[tuple[dict, str]] = []

    fake_closed = copy.deepcopy(plan)
    fake_closed["gaps"][0]["current_status"] = "CLOSED"
    invalid_cases.append((fake_closed, GAP_PLAN_FAKE_CLOSURE_FORBIDDEN))

    fake_evidence = copy.deepcopy(plan)
    fake_evidence["gaps"][0]["evidence_refs"] = ["synthetic:evidence:not-acquired"]
    invalid_cases.append((fake_evidence, GAP_PLAN_FAKE_EVIDENCE_FORBIDDEN))

    upgraded = copy.deepcopy(plan)
    upgraded["readiness_status"] = "READY"
    invalid_cases.append((upgraded, GAP_PLAN_READINESS_UPGRADE_FORBIDDEN))

    authorized = copy.deepcopy(plan)
    authorized["pilot_authorized"] = True
    invalid_cases.append((authorized, GAP_PLAN_PILOT_AUTHORIZATION_FORBIDDEN))

    execution = copy.deepcopy(plan)
    execution["execution_authorized"] = True
    invalid_cases.append((execution, GAP_PLAN_EXECUTION_CLAIM_FORBIDDEN))

    evidence_claim = copy.deepcopy(plan)
    evidence_claim["evidence_acquired"] = True
    invalid_cases.append((evidence_claim, GAP_PLAN_FAKE_EVIDENCE_FORBIDDEN))

    reassessment = copy.deepcopy(plan)
    reassessment["reassessment_rules"]["reassessment_allowed"] = True
    invalid_cases.append((reassessment, GAP_PLAN_REASSESSMENT_FORBIDDEN))

    closed_count = copy.deepcopy(plan)
    closed_count["gaps_closed"] = 1
    invalid_cases.append((closed_count, GAP_PLAN_FAKE_CLOSURE_FORBIDDEN))

    for candidate, reason in invalid_cases:
        _expect_invalid(candidate, reason)

    cycle = copy.deepcopy(plan)
    cycle["gaps"][0]["dependencies"] = ["GAP_IDENTITY_EXTERNAL_IDENTITY_VERIFICATION"]
    _expect_invalid(cycle, GAP_PLAN_DEPENDENCY_INVALID)

    source_gap = copy.deepcopy(plan)
    source_gap["gaps"][-1]["source_blocker_ids"] = ["UNKNOWN_SOURCE_BLOCKER"]
    _expect_invalid(source_gap, GAP_PLAN_SOURCE_BLOCKER_COVERAGE_INVALID)

    result_document = _load(RESULT_PATH)
    assert validate_gap_resolution_result_truth(result_document)["valid"] is True
    assert result_document["source_blockers_covered"] == 15
    assert result_document["artifact_requirements_defined"] == 15
    assert result_document["recommended_next_pr"] == "SAEE Pilot Gap Evidence Readiness Simulation v0.1"

    fake_result_fields = (
        "gaps_closed",
        "evidence_acquired",
        "readiness_changed",
        "reassessment_allowed",
        "pilot_authorized",
        "execution_authorized",
        "production_ready",
    )
    for field in fake_result_fields:
        candidate = copy.deepcopy(result_document)
        candidate[field] = 1 if field == "gaps_closed" else True
        rejected = validate_gap_resolution_result_truth(candidate)
        assert rejected["valid"] is False
        assert rejected["reason_codes"] == [f"GAP_PLAN_RESULT_OVERCLAIM:{field}"]

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3"}
    for path in (VALIDATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "Gap plans identify future work. They do not prove that work is complete." in document
    assert "evidence_refs=[]" in document
    assert "Pilot Gap Resolution Plan Reference" in READINESS_DOC_PATH.read_text(encoding="utf-8")
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_pilot_gap_resolution_plan(copy.deepcopy(plan))
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    print("SAEE_PILOT_GAP_RESOLUTION_PLAN_SMOKE: PASS")
    print("gap_count=15/15")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("adversarial_cases=2/2")
    print("invalid_result_claims=7/7")
    print("deterministic_runs=5/5")
    print("source_blockers_covered=15/15")
    print("artifact_requirements_defined=15/15")
    print("dependency_graph_valid=true")
    print("all_gap_statuses=OPEN")
    print("all_evidence_refs_empty=true")
    print("readiness_status=NOT_READY")
    print("gaps_closed=0")
    print("evidence_acquired=false")
    print("reassessment_allowed=false")
    print("pilot_authorized=false")
    print("execution_authorized=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
