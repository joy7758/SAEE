#!/usr/bin/env python3
"""Offline smoke for SAEE Controlled Pilot Execution Decision Gate v0.1."""

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

from saee_backend.services.pilot_execution_decision_gate import (  # noqa: E402
    DECISION_GATE_APPROVAL_EVIDENCE_REQUIRED,
    DECISION_GATE_CUSTOMER_VALIDATION_CLAIM_FORBIDDEN,
    DECISION_GATE_DESIGN_DOCUMENT_APPROVAL_FORBIDDEN,
    DECISION_GATE_EXECUTION_CLAIM_FORBIDDEN,
    DECISION_GATE_HUMAN_BOUNDARY_REQUIRED,
    DECISION_GATE_PRODUCTION_CLAIM_FORBIDDEN,
    DECISION_GATE_REAL_APPROVAL_CLAIM_FORBIDDEN,
    evaluate_pilot_execution_decision,
    validate_decision_result_truth,
)


SCHEMA_PATH = ROOT / "agent-interface/integration/saee-pilot-execution-decision-gate.schema.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/integration/decision-gate-scenarios"
RESULT_PATH = ROOT / "agent-interface/integration/saee-pilot-execution-decision-result.v0.1.json"
DOC_PATH = ROOT / "docs/commercial/SAEE_CONTROLLED_PILOT_EXECUTION_DECISION_GATE.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_CONTROLLED_PILOT_EXECUTION_DECISION_GATE_RECOMMENDATION_GATE.md"
READINESS_DOC_PATH = ROOT / "docs/commercial/SAEE_EXTERNAL_AGENT_PILOT_READINESS_REVIEW.md"
EVALUATOR_PATH = ROOT / "saee_backend/services/pilot_execution_decision_gate.py"

EXPECTED = {
    "CURRENT_NOT_READY": "HOLD",
    "MISSING_DATA_APPROVAL": "HOLD",
    "MISSING_HUMAN_OWNER": "HOLD",
    "ALL_REQUIREMENTS_SYNTHETICALLY_MET": "APPROVED_FOR_EXECUTION",
    "SAFETY_VIOLATION": "TERMINATED",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(candidate: dict, reason: str) -> None:
    result = evaluate_pilot_execution_decision(candidate)
    assert result["scenario_valid"] is False
    assert result["decision"] == "HOLD"
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
    for path in (SCHEMA_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, READINESS_DOC_PATH, EVALUATOR_PATH):
        assert path.is_file(), path

    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    scenario_paths = sorted(SCENARIO_DIR.glob("*.json"))
    assert len(scenario_paths) == 5
    scenarios = [_load(path) for path in scenario_paths]
    results: list[dict] = []
    for scenario in scenarios:
        errors = list(validator.iter_errors(scenario))
        assert not errors, [error.message for error in errors]
        result = evaluate_pilot_execution_decision(scenario)
        assert result["scenario_valid"] is True, result
        assert result["decision"] == EXPECTED[scenario["scenario_type"]]
        assert result["execution_authorized"] is False
        assert result["real_approval_exists"] is False
        results.append(result)

    valid_cases = sum(result["decision"] in {"APPROVED_FOR_EXECUTION", "TERMINATED"} for result in results)
    invalid_cases = sum(result["decision"] == "HOLD" for result in results)
    assert valid_cases == 2
    assert invalid_cases == 3

    synthetic_met = next(item for item in scenarios if item["scenario_type"] == "ALL_REQUIREMENTS_SYNTHETICALLY_MET")
    conditional = copy.deepcopy(synthetic_met)
    conditional["scenario_id"] = "decision:pilot:conditional-hold-check"
    conditional["scenario_type"] = "MISSING_DATA_APPROVAL"
    conditional["readiness_status"] = "PARTIAL"
    conditional["decision"] = "CONDITIONAL_HOLD"
    conditional["synthetic_approval"] = False
    conditional_result = evaluate_pilot_execution_decision(conditional)
    assert conditional_result["scenario_valid"] is True
    assert conditional_result["decision"] == "CONDITIONAL_HOLD"
    assert conditional_result["execution_authorized"] is False

    invalid_requests: list[tuple[dict, str]] = []

    no_evidence = copy.deepcopy(synthetic_met)
    no_evidence["approval_evidence"]["execution_authorization"]["evidence_reference"] = None
    invalid_requests.append((no_evidence, DECISION_GATE_APPROVAL_EVIDENCE_REQUIRED))

    execution_claim = copy.deepcopy(synthetic_met)
    execution_claim["execution_authorized"] = True
    invalid_requests.append((execution_claim, DECISION_GATE_EXECUTION_CLAIM_FORBIDDEN))

    production_claim = copy.deepcopy(synthetic_met)
    production_claim["production_ready"] = True
    invalid_requests.append((production_claim, DECISION_GATE_PRODUCTION_CLAIM_FORBIDDEN))

    customer_claim = copy.deepcopy(synthetic_met)
    customer_claim["customer_validated"] = True
    invalid_requests.append((customer_claim, DECISION_GATE_CUSTOMER_VALIDATION_CLAIM_FORBIDDEN))

    missing_human = copy.deepcopy(synthetic_met)
    missing_human["human_approval_required"] = False
    invalid_requests.append((missing_human, DECISION_GATE_HUMAN_BOUNDARY_REQUIRED))

    design_as_approval = copy.deepcopy(synthetic_met)
    design_as_approval["design_documents_as_approval"] = True
    invalid_requests.append((design_as_approval, DECISION_GATE_DESIGN_DOCUMENT_APPROVAL_FORBIDDEN))

    real_approval = copy.deepcopy(synthetic_met)
    real_approval["real_approval_exists"] = True
    invalid_requests.append((real_approval, DECISION_GATE_REAL_APPROVAL_CLAIM_FORBIDDEN))

    for candidate, reason in invalid_requests:
        _expect_invalid(candidate, reason)

    result_document = _load(RESULT_PATH)
    assert validate_decision_result_truth(result_document)["valid"] is True
    assert result_document["decision"] == "HOLD"
    assert result_document["blocking_gap_count"] == 15
    assert result_document["recommended_next_pr"] == "SAEE Pilot Gap Resolution Planning v0.1"

    fake_result_fields = (
        "execution_authorized",
        "real_approval_exists",
        "pilot_executed",
        "customer_validated",
        "external_validation_completed",
        "production_ready",
    )
    for field in fake_result_fields:
        candidate = copy.deepcopy(result_document)
        candidate[field] = True
        rejected = validate_decision_result_truth(candidate)
        assert rejected["valid"] is False
        assert rejected["reason_codes"] == [f"DECISION_GATE_REAL_WORLD_CLAIM_FORBIDDEN:{field}"]

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3"}
    for path in (EVALUATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "默认原则：未知或缺失关键证据即 `HOLD`。" in document
    assert "execution_authorized=false" in document
    assert "Controlled Pilot Execution Decision Gate Reference" in READINESS_DOC_PATH.read_text(encoding="utf-8")
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = [json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for result in results]
    for _ in range(5):
        repeated = [
            json.dumps(evaluate_pilot_execution_decision(copy.deepcopy(scenario)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            for scenario in scenarios
        ]
        assert repeated == canonical

    print("SAEE_PILOT_EXECUTION_DECISION_GATE_SMOKE: PASS")
    print("scenario_cases=5/5")
    print("valid_cases=2/2")
    print("invalid_cases=3/3")
    print(f"invalid_request_cases={len(invalid_requests)}/{len(invalid_requests)}")
    print("invalid_result_claims=6/6")
    print("deterministic_runs=5/5")
    print("current_decision=HOLD")
    print("conditional_hold_reachable=true")
    print("synthetic_approved_state_reachable=true")
    print("safety_termination_precedence=true")
    print("execution_authorized=false")
    print("real_approval_exists=false")
    print("pilot_executed=false")
    print("customer_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
