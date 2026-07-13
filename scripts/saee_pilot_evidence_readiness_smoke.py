#!/usr/bin/env python3
"""Offline smoke for SAEE Pilot Gap Evidence Readiness Simulation v0.1."""

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

from saee_backend.services.pilot_evidence_readiness import (  # noqa: E402
    EVIDENCE_READINESS_EXECUTION_CLAIM_FORBIDDEN,
    EVIDENCE_READINESS_GAP_CLOSURE_CLAIM_FORBIDDEN,
    EVIDENCE_READINESS_PILOT_AUTHORIZATION_FORBIDDEN,
    EVIDENCE_READINESS_READINESS_UPGRADE_FORBIDDEN,
    EVIDENCE_READINESS_REAL_EVIDENCE_CLAIM_FORBIDDEN,
    evaluate_pilot_evidence_readiness,
    validate_evidence_readiness_result_truth,
)


SCHEMA_PATH = ROOT / "agent-interface/integration/saee-pilot-evidence-artifact.schema.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/integration/evidence-readiness-simulation"
COMPLETE_PATH = SCENARIO_DIR / "complete-synthetic-artifact-package.json"
REGISTRY_PATH = SCENARIO_DIR / "synthetic-artifact-reference-registry.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/integration/saee-pilot-evidence-readiness-result.v0.1.json"
DOC_PATH = ROOT / "docs/commercial/SAEE_PILOT_GAP_EVIDENCE_READINESS_SIMULATION.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PILOT_GAP_EVIDENCE_READINESS_SIMULATION_RECOMMENDATION_GATE.md"
PLAN_DOC_PATH = ROOT / "docs/commercial/SAEE_PILOT_GAP_RESOLUTION_PLAN.md"
EVALUATOR_PATH = ROOT / "saee_backend/services/pilot_evidence_readiness.py"
SCENARIO_NAMES = (
    "complete-synthetic-artifact-package.json",
    "missing-security-artifact.json",
    "unverified-artifact-package.json",
    "invalid-artifact-reference.json",
    "artifact-version-mismatch.json",
)
EXPECTED = {
    "COMPLETE_SYNTHETIC_ARTIFACT_PACKAGE": (True, []),
    "MISSING_SECURITY_ARTIFACT": (False, ["EVIDENCE_READINESS_GAP_COVERAGE_INCOMPLETE"]),
    "UNVERIFIED_ARTIFACT_PACKAGE": (False, ["EVIDENCE_READINESS_VERIFICATION_INCOMPLETE"]),
    "INVALID_ARTIFACT_REFERENCE": (False, ["EVIDENCE_READINESS_REFERENCE_INVALID"]),
    "ARTIFACT_VERSION_MISMATCH": (False, ["EVIDENCE_READINESS_VERSION_MISMATCH"]),
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(candidate: dict, reason: str) -> None:
    result = evaluate_pilot_evidence_readiness(candidate)
    assert result["evaluation_valid"] is False
    assert result["reassessment_eligible"] is False
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
    for path in (SCHEMA_PATH, COMPLETE_PATH, REGISTRY_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, PLAN_DOC_PATH, EVALUATOR_PATH):
        assert path.is_file(), path

    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    artifact_validator = Draft202012Validator(schema)
    complete = _load(COMPLETE_PATH)
    assert len(complete["artifacts"]) == 15
    for artifact in complete["artifacts"]:
        errors = list(artifact_validator.iter_errors(artifact))
        assert not errors, [error.message for error in errors]

    registry = _load(REGISTRY_PATH)
    assert registry["synthetic_reference_only"] is True
    assert registry["real_evidence"] is False
    assert len(registry["entries"]) == 15
    assert len({entry["artifact_id"] for entry in registry["entries"]}) == 15

    scenarios = [_load(SCENARIO_DIR / name) for name in SCENARIO_NAMES]
    results: list[dict] = []
    for scenario in scenarios:
        result = evaluate_pilot_evidence_readiness(scenario)
        assert result["evaluation_valid"] is True, result
        expected_eligible, expected_reasons = EXPECTED[scenario["scenario_type"]]
        assert result["reassessment_eligible"] is expected_eligible
        assert result["reason_codes"] == expected_reasons
        assert result["real_evidence_acquired"] is False
        assert result["gaps_closed"] is False
        assert result["readiness_status"] == "NOT_READY"
        assert result["pilot_authorized"] is False
        results.append(result)

    valid_cases = sum(result["reassessment_eligible"] is True for result in results)
    invalid_cases = len(results) - valid_cases
    assert valid_cases == 1
    assert invalid_cases == 4
    assert results[0]["artifact_count"] == 15
    assert results[0]["covered_gap_count"] == 15
    assert results[0]["verified_artifact_count"] == 15

    invalid_requests: list[tuple[dict, str]] = []

    fake_closure = copy.deepcopy(complete)
    fake_closure["gaps_closed"] = True
    invalid_requests.append((fake_closure, EVIDENCE_READINESS_GAP_CLOSURE_CLAIM_FORBIDDEN))

    real_evidence = copy.deepcopy(complete)
    real_evidence["real_evidence_acquired"] = True
    invalid_requests.append((real_evidence, EVIDENCE_READINESS_REAL_EVIDENCE_CLAIM_FORBIDDEN))

    upgraded = copy.deepcopy(complete)
    upgraded["readiness_status"] = "READY"
    invalid_requests.append((upgraded, EVIDENCE_READINESS_READINESS_UPGRADE_FORBIDDEN))

    pilot = copy.deepcopy(complete)
    pilot["pilot_authorized"] = True
    invalid_requests.append((pilot, EVIDENCE_READINESS_PILOT_AUTHORIZATION_FORBIDDEN))

    execution = copy.deepcopy(complete)
    execution["execution_authorized"] = True
    invalid_requests.append((execution, EVIDENCE_READINESS_EXECUTION_CLAIM_FORBIDDEN))

    production = copy.deepcopy(complete)
    production["production_ready"] = True
    invalid_requests.append((production, EVIDENCE_READINESS_EXECUTION_CLAIM_FORBIDDEN))

    for candidate, reason in invalid_requests:
        _expect_invalid(candidate, reason)

    result_document = _load(RESULT_PATH)
    assert validate_evidence_readiness_result_truth(result_document)["valid"] is True
    assert result_document["scenario_cases"] == 5
    assert result_document["valid_cases"] == 1
    assert result_document["invalid_cases"] == 4
    assert result_document["complete_synthetic_package_reassessment_eligible"] is True
    assert result_document["recommended_next_pr"] == "SAEE Pilot Re-readiness Review Simulation v0.1"

    fake_result_fields = {
        "synthetic_artifacts_only": False,
        "real_evidence_acquired": True,
        "gaps_closed": True,
        "reassessment_eligible": True,
        "readiness_status": "READY",
        "pilot_authorized": True,
        "execution_authorized": True,
        "production_ready": True,
    }
    for field, value in fake_result_fields.items():
        candidate = copy.deepcopy(result_document)
        candidate[field] = value
        rejected = validate_evidence_readiness_result_truth(candidate)
        assert rejected["valid"] is False
        assert rejected["reason_codes"] == [f"EVIDENCE_READINESS_RESULT_OVERCLAIM:{field}"]

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3"}
    for path in (EVALUATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "This simulation evaluates evidence readiness logic. It does not establish real evidence or pilot approval." in document
    assert "该模拟验证证据就绪逻辑，不形成真实证据或 Pilot 批准。" in document
    assert "Evidence Readiness Simulation Reference" in PLAN_DOC_PATH.read_text(encoding="utf-8")
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = [json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for result in results]
    for _ in range(5):
        repeated = [
            json.dumps(evaluate_pilot_evidence_readiness(copy.deepcopy(scenario)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            for scenario in scenarios
        ]
        assert repeated == canonical

    print("SAEE_PILOT_EVIDENCE_READINESS_SMOKE: PASS")
    print("scenario_cases=5/5")
    print("valid_cases=1/1")
    print("invalid_cases=4/4")
    print(f"invalid_request_cases={len(invalid_requests)}/{len(invalid_requests)}")
    print("invalid_result_claims=8/8")
    print("deterministic_runs=5/5")
    print("synthetic_artifact_count=15/15")
    print("complete_package_coverage=15/15")
    print("complete_package_verified=15/15")
    print("complete_synthetic_reassessment_eligible=true")
    print("real_evidence_acquired=false")
    print("gaps_closed=false")
    print("current_reassessment_eligible=false")
    print("readiness_status=NOT_READY")
    print("pilot_authorized=false")
    print("execution_authorized=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
