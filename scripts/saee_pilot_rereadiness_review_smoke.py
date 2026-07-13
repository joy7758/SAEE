#!/usr/bin/env python3
"""Offline smoke for SAEE Pilot Re-readiness Review Simulation v0.1."""

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

from saee_backend.services.pilot_rereadiness_review import (  # noqa: E402
    REREADINESS_EXTERNAL_VALIDATION_REJECTED,
    REREADINESS_REAL_STATE_CLAIM_FORBIDDEN,
    evaluate_pilot_rereadiness_review,
    validate_rereadiness_result_truth,
)


SCHEMA_PATH = ROOT / "agent-interface/integration/saee-pilot-rereadiness-review.schema.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/integration/rereadiness-simulation"
RESULT_PATH = ROOT / "agent-interface/integration/saee-pilot-rereadiness-result.v0.1.json"
DOC_PATH = ROOT / "docs/commercial/SAEE_PILOT_REREADINESS_REVIEW_SIMULATION.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PILOT_REREADINESS_REVIEW_SIMULATION_RECOMMENDATION_GATE.md"
EVIDENCE_DOC_PATH = ROOT / "docs/commercial/SAEE_PILOT_GAP_EVIDENCE_READINESS_SIMULATION.md"
READINESS_DOC_PATH = ROOT / "docs/commercial/SAEE_EXTERNAL_AGENT_PILOT_READINESS_REVIEW.md"
EVALUATOR_PATH = ROOT / "saee_backend/services/pilot_rereadiness_review.py"
EXPECTED = {
    "COMPLETE_SYNTHETIC_EVIDENCE_PACKAGE": ("ELIGIBLE_FOR_REVIEW", True, []),
    "SYNTHETIC_AS_REAL_CLAIM": ("REJECT", False, ["REREADINESS_SYNTHETIC_AS_REAL_REJECTED"]),
    "READINESS_STATUS_ESCALATION": ("REJECT", False, ["REREADINESS_READINESS_ESCALATION_REJECTED"]),
    "DECISION_GATE_CONFUSION": ("REJECT", False, ["REREADINESS_AUTHORIZATION_CONFUSION_REJECTED"]),
    "PARTIAL_ARTIFACT_PACKAGE": ("NOT_ELIGIBLE_FOR_REVIEW", False, ["REREADINESS_PACKAGE_NOT_ELIGIBLE"]),
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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
    for path in (SCHEMA_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, EVIDENCE_DOC_PATH, READINESS_DOC_PATH, EVALUATOR_PATH):
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
        result = evaluate_pilot_rereadiness_review(scenario)
        assert result["scenario_valid"] is True, result
        expected_result, expected_eligible, expected_reasons = EXPECTED[scenario["scenario_type"]]
        assert result["simulation_result"] == expected_result
        assert result["reassessment_eligible"] is expected_eligible
        assert result["reason_codes"] == expected_reasons
        assert result["real_readiness_status"] == "NOT_READY"
        assert result["real_readiness_changed"] is False
        assert result["gaps_closed"] is False
        assert result["pilot_authorized"] is False
        assert result["execution_authorized"] is False
        results.append(result)

    valid_cases = sum(result["reassessment_eligible"] is True for result in results)
    invalid_cases = len(results) - valid_cases
    assert valid_cases == 1
    assert invalid_cases == 4

    complete = next(item for item in scenarios if item["scenario_type"] == "COMPLETE_SYNTHETIC_EVIDENCE_PACKAGE")
    external_validation = copy.deepcopy(complete)
    external_validation["scenario_id"] = "rereadiness:external-validation-confusion"
    external_validation["scenario_type"] = "DECISION_GATE_CONFUSION"
    external_validation["reassessment_result"] = "NOT_ELIGIBLE_FOR_REVIEW"
    external_validation["expected_simulation_result"] = "REJECT"
    external_validation["attempted_external_validation_completed"] = True
    external_result = evaluate_pilot_rereadiness_review(external_validation)
    assert external_result["scenario_valid"] is True
    assert external_result["simulation_result"] == "REJECT"
    assert external_result["reason_codes"] == [REREADINESS_EXTERNAL_VALIDATION_REJECTED]

    invalid_truth_fields = {
        "synthetic_only": False,
        "real_readiness_status": "READY",
        "gaps_closed": True,
        "pilot_authorized": True,
        "execution_authorized": True,
        "production_ready": True,
    }
    for field, value in invalid_truth_fields.items():
        candidate = copy.deepcopy(complete)
        candidate[field] = value
        rejected = evaluate_pilot_rereadiness_review(candidate)
        assert rejected["scenario_valid"] is False
        assert rejected["simulation_result"] == "REJECT"
        assert rejected["reason_codes"] == [REREADINESS_REAL_STATE_CLAIM_FORBIDDEN]

    result_document = _load(RESULT_PATH)
    assert validate_rereadiness_result_truth(result_document)["valid"] is True
    assert result_document["scenario_cases"] == 5
    assert result_document["valid_cases"] == 1
    assert result_document["invalid_cases"] == 4
    assert result_document["complete_synthetic_package_eligible_for_review"] is True
    assert result_document["recommended_next_pr"] == "SAEE Controlled External Pilot Execution Framework Design v0.1"

    fake_result_fields = {
        "synthetic_only": False,
        "real_readiness_changed": True,
        "real_readiness_status": "READY",
        "gaps_closed": True,
        "reassessment_eligible": True,
        "pilot_authorized": True,
        "execution_authorized": True,
        "external_validation_completed": True,
        "production_ready": True,
    }
    for field, value in fake_result_fields.items():
        candidate = copy.deepcopy(result_document)
        candidate[field] = value
        rejected = validate_rereadiness_result_truth(candidate)
        assert rejected["valid"] is False
        assert rejected["reason_codes"] == [f"REREADINESS_RESULT_OVERCLAIM:{field}"]

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3"}
    for path in (EVALUATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "This simulation tests re-readiness review logic. It does not establish operational readiness or authorize a pilot." in document
    assert "该模拟测试重新审查逻辑，不建立运营就绪状态或授权 Pilot。" in document
    assert "Re-readiness Review Simulation Reference" in EVIDENCE_DOC_PATH.read_text(encoding="utf-8")
    assert "Re-readiness Simulation Boundary" in READINESS_DOC_PATH.read_text(encoding="utf-8")
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = [json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for result in results]
    for _ in range(5):
        repeated = [
            json.dumps(evaluate_pilot_rereadiness_review(copy.deepcopy(scenario)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            for scenario in scenarios
        ]
        assert repeated == canonical

    print("SAEE_PILOT_REREADINESS_REVIEW_SMOKE: PASS")
    print("scenario_cases=5/5")
    print("valid_cases=1/1")
    print("invalid_cases=4/4")
    print("external_validation_confusion_rejected=true")
    print("invalid_truth_cases=6/6")
    print("invalid_result_claims=9/9")
    print("deterministic_runs=5/5")
    print("complete_synthetic_eligible_for_review=true")
    print("synthetic_as_real_rejected=true")
    print("readiness_escalation_rejected=true")
    print("authorization_confusion_rejected=true")
    print("real_readiness_changed=false")
    print("real_readiness_status=NOT_READY")
    print("gaps_closed=false")
    print("current_reassessment_eligible=false")
    print("pilot_authorized=false")
    print("execution_authorized=false")
    print("external_validation_completed=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
