"""Local synthetic evaluator for SAEE Pilot Gap Evidence Readiness v0.1.

Artifact metadata and reference matching in this module do not establish real
evidence, close gaps, change readiness, or authorize a Pilot.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "agent-interface/integration/saee-pilot-gap-resolution-plan.v0.1.json"
DIRECT_TOP_LEVEL = {
    "simulation_version",
    "scenario_id",
    "scenario_type",
    "synthetic_only",
    "artifacts",
    "expected_reassessment_eligible",
    "real_evidence_acquired",
    "gaps_closed",
    "readiness_status",
    "pilot_authorized",
    "execution_authorized",
    "production_ready",
}
DERIVED_TOP_LEVEL = {
    "simulation_version",
    "scenario_id",
    "scenario_type",
    "synthetic_only",
    "base_package_ref",
    "mutation",
    "expected_reassessment_eligible",
    "real_evidence_acquired",
    "gaps_closed",
    "readiness_status",
    "pilot_authorized",
    "execution_authorized",
    "production_ready",
}
MUTATION_OPERATIONS = {
    "REMOVE_ARTIFACT",
    "SET_VERIFICATION_STATUS",
    "SET_EVIDENCE_REFERENCE",
    "SET_ARTIFACT_VERSION",
}

EVIDENCE_READINESS_INVALID = "EVIDENCE_READINESS_INVALID"
EVIDENCE_READINESS_STRUCTURE_INVALID = "EVIDENCE_READINESS_STRUCTURE_INVALID"
EVIDENCE_READINESS_REAL_EVIDENCE_CLAIM_FORBIDDEN = "EVIDENCE_READINESS_REAL_EVIDENCE_CLAIM_FORBIDDEN"
EVIDENCE_READINESS_GAP_CLOSURE_CLAIM_FORBIDDEN = "EVIDENCE_READINESS_GAP_CLOSURE_CLAIM_FORBIDDEN"
EVIDENCE_READINESS_READINESS_UPGRADE_FORBIDDEN = "EVIDENCE_READINESS_READINESS_UPGRADE_FORBIDDEN"
EVIDENCE_READINESS_PILOT_AUTHORIZATION_FORBIDDEN = "EVIDENCE_READINESS_PILOT_AUTHORIZATION_FORBIDDEN"
EVIDENCE_READINESS_EXECUTION_CLAIM_FORBIDDEN = "EVIDENCE_READINESS_EXECUTION_CLAIM_FORBIDDEN"
EVIDENCE_READINESS_BASE_PACKAGE_INVALID = "EVIDENCE_READINESS_BASE_PACKAGE_INVALID"
EVIDENCE_READINESS_MUTATION_INVALID = "EVIDENCE_READINESS_MUTATION_INVALID"
EVIDENCE_READINESS_GAP_COVERAGE_INCOMPLETE = "EVIDENCE_READINESS_GAP_COVERAGE_INCOMPLETE"
EVIDENCE_READINESS_ARTIFACT_INTEGRITY_INVALID = "EVIDENCE_READINESS_ARTIFACT_INTEGRITY_INVALID"
EVIDENCE_READINESS_VERSION_MISMATCH = "EVIDENCE_READINESS_VERSION_MISMATCH"
EVIDENCE_READINESS_VERIFICATION_INCOMPLETE = "EVIDENCE_READINESS_VERIFICATION_INCOMPLETE"
EVIDENCE_READINESS_REFERENCE_INVALID = "EVIDENCE_READINESS_REFERENCE_INVALID"
EVIDENCE_READINESS_EXPECTATION_MISMATCH = "EVIDENCE_READINESS_EXPECTATION_MISMATCH"


def _result(value: Any, valid: bool, eligible: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "saee_pilot_gap_evidence_readiness_result_v0_1": True,
        "evaluation_valid": valid,
        "scenario_id": value.get("scenario_id", "") if isinstance(value, dict) else "",
        "scenario_type": value.get("scenario_type", "") if isinstance(value, dict) else "",
        "reassessment_eligible": eligible,
        "artifact_count": 0,
        "covered_gap_count": 0,
        "verified_artifact_count": 0,
        "reason_codes": reasons,
        "synthetic_artifacts_only": True,
        "real_evidence_acquired": False,
        "gaps_closed": False,
        "readiness_status": "NOT_READY",
        "pilot_authorized": False,
        "execution_authorized": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _truth_boundary_error(value: dict[str, Any]) -> str | None:
    if value.get("synthetic_only") is not True or value.get("real_evidence_acquired") is not False:
        return EVIDENCE_READINESS_REAL_EVIDENCE_CLAIM_FORBIDDEN
    if value.get("gaps_closed") is not False:
        return EVIDENCE_READINESS_GAP_CLOSURE_CLAIM_FORBIDDEN
    if value.get("readiness_status") != "NOT_READY":
        return EVIDENCE_READINESS_READINESS_UPGRADE_FORBIDDEN
    if value.get("pilot_authorized") is not False:
        return EVIDENCE_READINESS_PILOT_AUTHORIZATION_FORBIDDEN
    if value.get("execution_authorized") is not False or value.get("production_ready") is not False:
        return EVIDENCE_READINESS_EXECUTION_CLAIM_FORBIDDEN
    return None


def _resolve_artifacts(value: dict[str, Any]) -> tuple[list[dict[str, Any]] | None, str | None]:
    if set(value) == DIRECT_TOP_LEVEL:
        artifacts = value.get("artifacts")
        return (copy.deepcopy(artifacts), None) if isinstance(artifacts, list) else (None, EVIDENCE_READINESS_STRUCTURE_INVALID)
    if set(value) != DERIVED_TOP_LEVEL:
        return None, EVIDENCE_READINESS_STRUCTURE_INVALID

    base_ref = value.get("base_package_ref")
    if not isinstance(base_ref, str) or not (ROOT / base_ref).is_file():
        return None, EVIDENCE_READINESS_BASE_PACKAGE_INVALID
    try:
        base = json.loads((ROOT / base_ref).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, EVIDENCE_READINESS_BASE_PACKAGE_INVALID
    if set(base) != DIRECT_TOP_LEVEL or base.get("synthetic_only") is not True or not isinstance(base.get("artifacts"), list):
        return None, EVIDENCE_READINESS_BASE_PACKAGE_INVALID
    artifacts = copy.deepcopy(base["artifacts"])

    mutation = value.get("mutation")
    if not isinstance(mutation, dict) or set(mutation) != {"operation", "source_gap_id", "value"}:
        return None, EVIDENCE_READINESS_MUTATION_INVALID
    operation = mutation.get("operation")
    gap_id = mutation.get("source_gap_id")
    if operation not in MUTATION_OPERATIONS or not isinstance(gap_id, str):
        return None, EVIDENCE_READINESS_MUTATION_INVALID
    targets = [artifact for artifact in artifacts if artifact.get("source_gap_id") == gap_id]
    if len(targets) != 1:
        return None, EVIDENCE_READINESS_MUTATION_INVALID
    if operation == "REMOVE_ARTIFACT":
        if mutation.get("value") is not None:
            return None, EVIDENCE_READINESS_MUTATION_INVALID
        artifacts.remove(targets[0])
    elif operation == "SET_VERIFICATION_STATUS":
        if mutation.get("value") not in {"PENDING", "VERIFIED", "REJECTED"}:
            return None, EVIDENCE_READINESS_MUTATION_INVALID
        targets[0]["verification_status"] = mutation["value"]
    elif operation == "SET_EVIDENCE_REFERENCE":
        if not isinstance(mutation.get("value"), str):
            return None, EVIDENCE_READINESS_MUTATION_INVALID
        targets[0]["evidence_reference"] = mutation["value"]
    elif operation == "SET_ARTIFACT_VERSION":
        if not isinstance(mutation.get("value"), str):
            return None, EVIDENCE_READINESS_MUTATION_INVALID
        targets[0]["artifact_version"] = mutation["value"]
    return artifacts, None


def _reference_matches(artifact: dict[str, Any]) -> bool:
    reference = artifact.get("evidence_reference")
    if not isinstance(reference, str) or "#" not in reference:
        return False
    path_text, fragment = reference.split("#", 1)
    path = ROOT / path_text
    if fragment != artifact.get("artifact_id") or not path.is_file():
        return False
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if registry.get("synthetic_reference_only") is not True or registry.get("real_evidence") is not False:
        return False
    entries = registry.get("entries")
    if not isinstance(entries, list):
        return False
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("artifact_id") == fragment]
    if len(matches) != 1:
        return False
    entry = matches[0]
    return all(entry.get(field) == artifact.get(field) for field in ("artifact_id", "artifact_type", "artifact_version", "verification_method"))


def evaluate_pilot_evidence_readiness(value: Any) -> dict[str, Any]:
    """Evaluate synthetic artifact metadata against the current gap plan."""

    if not isinstance(value, dict):
        return _result(value, False, False, [EVIDENCE_READINESS_INVALID])
    boundary_error = _truth_boundary_error(value)
    if boundary_error:
        return _result(value, False, False, [boundary_error])
    if value.get("simulation_version") != "0.1" or not isinstance(value.get("expected_reassessment_eligible"), bool):
        return _result(value, False, False, [EVIDENCE_READINESS_STRUCTURE_INVALID])

    artifacts, resolution_error = _resolve_artifacts(value)
    if resolution_error:
        return _result(value, False, False, [resolution_error])
    assert artifacts is not None

    try:
        plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _result(value, False, False, [EVIDENCE_READINESS_STRUCTURE_INVALID])
    gap_requirements = {
        gap["gap_id"]: (gap["required_artifact_type"], gap["verification_method"])
        for gap in plan.get("gaps", [])
        if isinstance(gap, dict)
    }
    source_gap_ids = [artifact.get("source_gap_id") for artifact in artifacts if isinstance(artifact, dict)]
    base = _result(value, True, False, [])
    base["artifact_count"] = len(artifacts)
    base["covered_gap_count"] = len(set(source_gap_ids) & set(gap_requirements))
    base["verified_artifact_count"] = sum(
        isinstance(artifact, dict) and artifact.get("verification_status") == "VERIFIED" for artifact in artifacts
    )

    if len(source_gap_ids) != len(set(source_gap_ids)) or set(source_gap_ids) != set(gap_requirements):
        base["reason_codes"] = [EVIDENCE_READINESS_GAP_COVERAGE_INCOMPLETE]
    else:
        for artifact in artifacts:
            if not isinstance(artifact, dict) or set(artifact) != {
                "artifact_id", "artifact_type", "source_gap_id", "artifact_version", "verification_method", "verification_status", "evidence_reference"
            }:
                base["reason_codes"] = [EVIDENCE_READINESS_ARTIFACT_INTEGRITY_INVALID]
                break
            expected_type, expected_method = gap_requirements[artifact["source_gap_id"]]
            if artifact.get("artifact_type") != expected_type or artifact.get("verification_method") != expected_method:
                base["reason_codes"] = [EVIDENCE_READINESS_ARTIFACT_INTEGRITY_INVALID]
                break
            if artifact.get("artifact_version") != "0.1":
                base["reason_codes"] = [EVIDENCE_READINESS_VERSION_MISMATCH]
                break
            if artifact.get("verification_status") != "VERIFIED":
                base["reason_codes"] = [EVIDENCE_READINESS_VERIFICATION_INCOMPLETE]
                break
            if not _reference_matches(artifact):
                base["reason_codes"] = [EVIDENCE_READINESS_REFERENCE_INVALID]
                break

    eligible = not base["reason_codes"]
    if value.get("expected_reassessment_eligible") is not eligible:
        return _result(value, False, False, [EVIDENCE_READINESS_EXPECTATION_MISMATCH])
    base["reassessment_eligible"] = eligible
    return base


def validate_evidence_readiness_result_truth(value: Any) -> dict[str, Any]:
    """Reject aggregate results that promote synthetic eligibility into real state."""

    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": [EVIDENCE_READINESS_INVALID]}
    expected = {
        "synthetic_artifacts_only": True,
        "real_evidence_acquired": False,
        "gaps_closed": False,
        "reassessment_eligible": False,
        "readiness_status": "NOT_READY",
        "pilot_authorized": False,
        "execution_authorized": False,
        "production_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            return {"valid": False, "reason_codes": [f"EVIDENCE_READINESS_RESULT_OVERCLAIM:{field}"]}
    return {"valid": True, "reason_codes": []}


def evaluate_pilot_evidence_readiness_path(path: Path) -> dict[str, Any]:
    """Evaluate one checked-in local synthetic package scenario."""

    return evaluate_pilot_evidence_readiness(json.loads(path.read_text(encoding="utf-8")))
