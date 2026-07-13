"""Deterministic readiness gate for future SAEE external validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-matrix.v0.1.json"
GAPS_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-gaps.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-review.v0.1.json"
SCHEMA_PATH = ROOT / "schemas/saee-external-validation-readiness-review.schema.v0.1.json"
EXPECTED_DIMENSIONS = {"TECHNICAL_CAPABILITY", "DOCUMENTATION", "VALIDATION_PROCESS", "SECURITY_BOUNDARY", "OPERATIONAL_READINESS"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def _safe_ref(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or ref.startswith("/") or "://" in ref or ".." in Path(ref).parts:
        return False
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def build_readiness_review(matrix: dict[str, Any] | None = None, gaps: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a review result. Even GO would not authorize execution."""

    matrix = matrix or _load(MATRIX_PATH)
    gaps = gaps or _load(GAPS_PATH)
    dimensions = matrix.get("dimensions", [])
    if {item.get("dimension") for item in dimensions if isinstance(item, dict)} != EXPECTED_DIMENSIONS:
        raise ValueError("READINESS_DIMENSIONS_INVALID")
    refs = sorted({ref for item in dimensions for ref in item.get("evidence_refs", [])})
    if not refs or not all(_safe_ref(ref) for ref in refs):
        raise ValueError("READINESS_EVIDENCE_REFERENCE_INVALID")
    gap_items = gaps.get("gaps", [])
    required_open = [item for item in gap_items if item.get("required_before_external_validation") is True and item.get("status") == "OPEN"]
    critical_open = [item for item in required_open if item.get("severity") == "CRITICAL"]
    if critical_open:
        decision = "HOLD"
    elif required_open or any(item.get("status") != "PASS" for item in dimensions):
        decision = "CONDITIONAL_GO"
    else:
        decision = "GO"
    return {
        "review_version": "0.1",
        "execution_simulation_reference": "agent-interface/ecosystem/saee-external-validation-execution-simulation-result.v0.1.json",
        "entry_decision_reference": "agent-interface/ecosystem/saee-external-validation-entry-decision.v0.1.json",
        "review_dimensions": sorted(EXPECTED_DIMENSIONS),
        "evidence_refs": refs,
        "status": "REVIEW_COMPLETE",
        "blocking_gaps": [item["gap_id"] for item in required_open],
        "decision": decision,
        "limitations": [
            "The review evaluates preparation artifacts and does not execute external validation.",
            "GO or CONDITIONAL_GO would still require a separate explicit execution authorization.",
            "Local design, simulation and adapter evidence do not establish external compatibility, adoption or production readiness.",
        ],
        "truth_boundary": {
            "readiness_review": True, "external_validation_execution": False,
            "execution_authorized": False, "participants_invited": 0,
            "external_agents_connected": False, "customer_validated": False,
            "adoption_validated": False, "marketplace_listed": False,
            "production_ready": False,
        },
    }


def validate_readiness_review(value: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["READINESS_REVIEW_INVALID"]}
    schema = _load(SCHEMA_PATH)
    if list(Draft202012Validator(schema).iter_errors(value)):
        reasons.append("READINESS_REVIEW_SCHEMA_INVALID")
    if isinstance(value.get("evidence_refs"), list) and any(not _safe_ref(ref) for ref in value["evidence_refs"]):
        reasons.append("READINESS_REVIEW_EVIDENCE_INVALID")
    if "docs/ecosystem/SAEE_EXTERNAL_VALIDATION_TERMINATION_POLICY.md" not in value.get("evidence_refs", []):
        reasons.append("READINESS_REVIEW_TERMINATION_EVIDENCE_MISSING")
    truth = value.get("truth_boundary", {})
    if isinstance(truth, dict) and (truth.get("external_validation_execution") is not False or truth.get("execution_authorized") is not False):
        reasons.append("READINESS_REVIEW_EXECUTION_FORBIDDEN")
    if value.get("decision") == "GO" and value.get("blocking_gaps"):
        reasons.append("READINESS_REVIEW_GO_WITH_BLOCKERS")
    return {"valid": not reasons, "reason_codes": list(dict.fromkeys(reasons))}


def validate_current_readiness_review() -> dict[str, Any]:
    stored = _load(RESULT_PATH)
    if stored != build_readiness_review():
        return {"valid": False, "reason_codes": ["READINESS_REVIEW_RESULT_DRIFT"]}
    return validate_readiness_review(stored)
