"""Offline validator for SAEE First Real Ecosystem Validation Decision Gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .real_ecosystem_validation_entry_gate import evaluate_entry_gate, readiness_from_matrix


ROOT = Path(__file__).resolve().parents[2]
GATE_SCHEMA_PATH = ROOT / "schemas/saee-real-ecosystem-validation-entry-gate.schema.v0.1.json"
BLOCKER_SCHEMA_PATH = ROOT / "schemas/saee-real-validation-blocker.schema.v0.1.json"
MATRIX_PATH = ROOT / "agent-interface/ecosystem/saee-real-validation-readiness-matrix.v0.1.json"
DECISION_PATH = ROOT / "agent-interface/ecosystem/saee-real-ecosystem-validation-entry-decision.v0.1.json"
BLOCKERS_PATH = ROOT / "agent-interface/ecosystem/saee-real-validation-blockers.v0.1.json"
FIXTURE_DIR = ROOT / "agent-interface/ecosystem/real-validation-entry-fixtures"
EXPECTED_DIMENSIONS = {"technical", "candidate", "scope", "risk", "operational"}
FORBIDDEN_KEYS = {
    "external_validation_started", "real_candidate_connected", "customer_validated",
    "adoption_claim", "validation_started", "execution_authorized",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _local_ref_exists(reference: str) -> bool:
    path = (ROOT / reference).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def _truth_overclaim(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_KEYS and child is True:
                return True
            if _truth_overclaim(child):
                return True
    elif isinstance(value, list):
        return any(_truth_overclaim(child) for child in value)
    return False


def validate_gate_artifacts(matrix: Any, decision: Any, blocker_set: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not all(isinstance(item, dict) for item in (matrix, decision, blocker_set)):
        return {"valid": False, "reason_codes": ["REAL_VALIDATION_GATE_DATA_INVALID"]}

    dimensions = matrix.get("dimensions")
    if not isinstance(dimensions, list) or {item.get("dimension") for item in dimensions if isinstance(item, dict)} != EXPECTED_DIMENSIONS:
        reasons.append("REAL_VALIDATION_DIMENSIONS_INVALID")
    else:
        for dimension in dimensions:
            if dimension.get("status") not in {"READY", "GAP", "UNVERIFIED"}:
                reasons.append("REAL_VALIDATION_MATRIX_STATUS_INVALID")
                break
            checks = dimension.get("checks")
            if not isinstance(checks, list) or not checks:
                reasons.append("REAL_VALIDATION_MATRIX_CHECKS_REQUIRED")
                break
            if any(item.get("status") not in {"VERIFIED", "UNVERIFIED", "GAP"} or not _local_ref_exists(item.get("evidence_ref", "")) for item in checks):
                reasons.append("REAL_VALIDATION_MATRIX_EVIDENCE_INVALID")
                break

    gate_schema = _load(GATE_SCHEMA_PATH)
    if list(Draft202012Validator(gate_schema).iter_errors(decision)):
        reasons.append("REAL_VALIDATION_DECISION_SCHEMA_INVALID")

    blocker_schema = _load(BLOCKER_SCHEMA_PATH)
    blocker_validator = Draft202012Validator(blocker_schema)
    blockers = blocker_set.get("blockers")
    if not isinstance(blockers, list) or not blockers or any(list(blocker_validator.iter_errors(item)) for item in blockers):
        reasons.append("REAL_VALIDATION_BLOCKERS_INVALID")
        blocker_ids: set[str] = set()
    else:
        blocker_ids = {item["blocker_id"] for item in blockers}
    if set(decision.get("blocking_conditions", [])) != {item["blocker_id"] for item in blockers if item.get("status") == "OPEN"}:
        reasons.append("REAL_VALIDATION_BLOCKER_BINDING_INVALID")
    if decision.get("decision") == "ENTRY_READY" and blocker_ids:
        reasons.append("REAL_VALIDATION_ENTRY_READY_WITH_BLOCKERS")
    if _truth_overclaim({"matrix": matrix, "decision": decision, "blockers": blocker_set}):
        reasons.append("REAL_VALIDATION_BOUNDARY_OVERCLAIM")

    if isinstance(dimensions, list) and {item.get("dimension") for item in dimensions if isinstance(item, dict)} == EXPECTED_DIMENSIONS:
        summaries = readiness_from_matrix(matrix)
        for key in EXPECTED_DIMENSIONS:
            if decision.get(f"{key}_readiness") != summaries.get(key):
                reasons.append("REAL_VALIDATION_READINESS_BINDING_INVALID")
                break
    if decision.get("decision") != "HOLD":
        reasons.append("REAL_VALIDATION_CURRENT_DECISION_MUST_HOLD")

    return {
        "valid": not reasons,
        "reason_codes": reasons,
        "technical_matrix": "PASS" if "REAL_VALIDATION_DIMENSIONS_INVALID" not in reasons else "FAIL",
        "candidate_matrix": "PASS" if "REAL_VALIDATION_DIMENSIONS_INVALID" not in reasons else "FAIL",
        "risk_matrix": "PASS" if "REAL_VALIDATION_MATRIX_EVIDENCE_INVALID" not in reasons else "FAIL",
        "decision_logic": "PASS" if decision.get("decision") == "HOLD" else "FAIL",
        "boundary_preserved": "REAL_VALIDATION_BOUNDARY_OVERCLAIM" not in reasons,
        "external_validation": False,
        "participant_contact": False,
        "adoption_validated": False,
        "production_ready": False,
    }


def validate_gate_repository() -> dict[str, Any]:
    for schema_path in (GATE_SCHEMA_PATH, BLOCKER_SCHEMA_PATH):
        Draft202012Validator.check_schema(_load(schema_path))
    return validate_gate_artifacts(_load(MATRIX_PATH), _load(DECISION_PATH), _load(BLOCKERS_PATH))


def evaluate_fixture(path: Path) -> dict[str, Any]:
    fixture = _load(path)
    result = evaluate_entry_gate(fixture)
    result["matched_expected"] = result["decision"] == fixture.get("expected_decision")
    return result
