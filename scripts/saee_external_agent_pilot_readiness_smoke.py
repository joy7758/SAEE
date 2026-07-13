#!/usr/bin/env python3
"""Offline smoke for SAEE External Agent Pilot Readiness Review v0.1."""

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

from saee_backend.services.external_agent_pilot_readiness import (  # noqa: E402
    PILOT_READINESS_APPROVAL_CLAIM_FORBIDDEN,
    PILOT_READINESS_DIMENSION_STATUS_INVALID,
    PILOT_READINESS_EXTERNAL_VALIDATION_CLAIM_FORBIDDEN,
    PILOT_READINESS_HUMAN_BOUNDARY_REQUIRED,
    PILOT_READINESS_PRODUCTION_CLAIM_FORBIDDEN,
    PILOT_READINESS_SCORE_INVALID,
    PILOT_READINESS_SECURITY_GATE_REQUIRED,
    evaluate_external_agent_pilot_readiness,
    validate_readiness_result_truth,
)


SCHEMA_PATH = ROOT / "agent-interface/integration/saee-external-agent-pilot-readiness.schema.v0.1.json"
MATRIX_PATH = ROOT / "agent-interface/integration/saee-external-agent-pilot-readiness.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/integration/saee-external-agent-pilot-readiness-result.v0.1.json"
DOC_PATH = ROOT / "docs/commercial/SAEE_EXTERNAL_AGENT_PILOT_READINESS_REVIEW.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_EXTERNAL_AGENT_PILOT_READINESS_RECOMMENDATION_GATE.md"
DESIGN_PATH = ROOT / "docs/commercial/SAEE_CONTROLLED_EXTERNAL_AGENT_PILOT_DESIGN.md"
EVALUATOR_PATH = ROOT / "saee_backend/services/external_agent_pilot_readiness.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(candidate: dict, reason: str) -> None:
    result = evaluate_external_agent_pilot_readiness(candidate)
    assert result["review_valid"] is False
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
    for path in (SCHEMA_PATH, MATRIX_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, DESIGN_PATH, EVALUATOR_PATH):
        assert path.is_file(), path

    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    matrix = _load(MATRIX_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(matrix))
    assert not errors, [error.message for error in errors]

    valid = evaluate_external_agent_pilot_readiness(matrix)
    assert valid["review_valid"] is True
    assert valid["readiness_result"] == "NOT_READY"
    assert valid["readiness_score"] == 19
    assert valid["dimension_status"] == {
        "data": "NOT_READY",
        "human_governance": "PARTIAL",
        "identity": "PARTIAL",
        "runtime": "NOT_READY",
        "security": "NOT_READY",
    }
    assert len(valid["blocking_gaps"]) == 15
    assert len(valid["missing_evidence"]) == 15

    invalid_cases: list[tuple[dict, str]] = []

    approved = copy.deepcopy(matrix)
    approved["pilot_authorized"] = True
    invalid_cases.append((approved, PILOT_READINESS_APPROVAL_CLAIM_FORBIDDEN))

    externally_validated = copy.deepcopy(matrix)
    externally_validated["external_validation_completed"] = True
    invalid_cases.append((externally_validated, PILOT_READINESS_EXTERNAL_VALIDATION_CLAIM_FORBIDDEN))

    connected = copy.deepcopy(matrix)
    connected["external_agent_connected"] = True
    invalid_cases.append((connected, PILOT_READINESS_EXTERNAL_VALIDATION_CLAIM_FORBIDDEN))

    production = copy.deepcopy(matrix)
    production["production_ready"] = True
    invalid_cases.append((production, PILOT_READINESS_PRODUCTION_CLAIM_FORBIDDEN))

    no_human_boundary = copy.deepcopy(matrix)
    no_human_boundary["human_boundary"]["human_review_required"] = False
    invalid_cases.append((no_human_boundary, PILOT_READINESS_HUMAN_BOUNDARY_REQUIRED))

    no_security_gate = copy.deepcopy(matrix)
    no_security_gate["dimensions"]["security"]["checks"].pop()
    invalid_cases.append((no_security_gate, PILOT_READINESS_SECURITY_GATE_REQUIRED))

    fake_identity_ready = copy.deepcopy(matrix)
    fake_identity_ready["dimensions"]["identity"]["status"] = "READY"
    invalid_cases.append((fake_identity_ready, PILOT_READINESS_DIMENSION_STATUS_INVALID))

    fake_score = copy.deepcopy(matrix)
    fake_score["readiness_score"]["percentage"] = 100
    invalid_cases.append((fake_score, PILOT_READINESS_SCORE_INVALID))

    for candidate, reason in invalid_cases:
        _expect_invalid(candidate, reason)

    result_document = _load(RESULT_PATH)
    assert validate_readiness_result_truth(result_document)["valid"] is True
    assert result_document["blocking_gaps"] == valid["blocking_gaps"]
    assert result_document["missing_evidence"] == valid["missing_evidence"]
    assert result_document["recommended_next_pr"] == "SAEE Controlled Pilot Execution Decision Gate v0.1"

    fake_result_fields = (
        "pilot_authorized",
        "external_agent_connected",
        "external_validation_completed",
        "customer_validated",
        "production_ready",
    )
    for field in fake_result_fields:
        candidate = copy.deepcopy(result_document)
        candidate[field] = True
        rejected = validate_readiness_result_truth(candidate)
        assert rejected["valid"] is False
        assert rejected["reason_codes"] == [f"PILOT_READINESS_REAL_WORLD_CLAIM_FORBIDDEN:{field}"]
    approved_status = copy.deepcopy(result_document)
    approved_status["readiness_status"] = "APPROVED"
    assert validate_readiness_result_truth(approved_status)["reason_codes"] == ["PILOT_READINESS_STATUS_OVERCLAIM"]

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3"}
    for path in (EVALUATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "This read-only review identifies evidence still missing before a real external Agent Pilot could be considered. It does not approve or start a Pilot." in document
    assert "readiness_status=NOT_READY" in document
    assert "External Agent Pilot Readiness Review Reference" in DESIGN_PATH.read_text(encoding="utf-8")
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = evaluate_external_agent_pilot_readiness(copy.deepcopy(matrix))
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    print("SAEE_EXTERNAL_AGENT_PILOT_READINESS_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("invalid_result_claims=6/6")
    print("deterministic_runs=5/5")
    print("readiness_status=NOT_READY")
    print("readiness_score=19")
    print("score_is_probability=false")
    print("blocking_gaps=15")
    print("missing_evidence=15")
    print("identity_status=PARTIAL")
    print("security_status=NOT_READY")
    print("data_status=NOT_READY")
    print("runtime_status=NOT_READY")
    print("human_governance_status=PARTIAL")
    print("pilot_authorized=false")
    print("external_agent_connected=false")
    print("external_validation_completed=false")
    print("customer_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
