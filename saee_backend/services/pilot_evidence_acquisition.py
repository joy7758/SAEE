"""Offline validator for the SAEE pilot evidence acquisition plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EXPECTED_GAP_IDS = (
    "DATA_SOURCE",
    "DATA_OWNERSHIP",
    "DATA_PERMISSIONS",
    "PRIVACY_REVIEW",
    "RETENTION_POLICY",
    "DELETION_PROCESS",
    "ACCESS_CONTROL",
    "SCHEMA_FREEZE",
    "APPROVED_SAMPLE",
    "ANNOTATION_APPROVAL",
    "PILOT_ENVIRONMENT",
    "SAFETY_AND_EXECUTION_APPROVAL",
)
ARTIFACT_STATUSES = {"MISSING", "PRESENT_UNVERIFIED", "VERIFIED", "CLOSED"}
ROLE_FIELDS = {"creator_role", "reviewer_role", "approver_role", "verifier_role"}
CLOSURE_FIELDS = ("artifact_identifier", "artifact_source", "artifact_timestamp", "verification_method", "evidence_reference")


class PilotEvidenceAcquisitionError(ValueError):
    """Stable acquisition-plan validation error."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise PilotEvidenceAcquisitionError(code, detail)


def evaluate_evidence_acquisition_plan(document: dict[str, Any]) -> dict[str, Any]:
    """Check plan consistency without acquiring, verifying, or approving evidence."""

    _require(isinstance(document, dict), "EVIDENCE_ACQUISITION_INPUT_INVALID", "JSON object required")
    _require(document.get("saee_pilot_evidence_acquisition_plan_v0_1") is True, "EVIDENCE_ACQUISITION_IDENTITY_INVALID", "root marker")
    _require(document.get("plan_version") == "0.1", "EVIDENCE_ACQUISITION_VERSION_INVALID", "plan version")
    _require(document.get("current_readiness") == "NO_GO", "EVIDENCE_ACQUISITION_READINESS_CHANGED", "current_readiness must remain NO_GO")
    boundary_codes = {
        "evidence_acquisition_started": "EVIDENCE_ACQUISITION_STARTED_FORBIDDEN",
        "evidence_records_created": "EVIDENCE_RECORD_CREATION_FORBIDDEN",
        "pilot_authorized": "EVIDENCE_ACQUISITION_PILOT_AUTHORIZATION_FORBIDDEN",
        "data_collected": "EVIDENCE_ACQUISITION_DATA_COLLECTION_FORBIDDEN",
        "external_parties_contacted": "EVIDENCE_ACQUISITION_EXTERNAL_CONTACT_FORBIDDEN",
        "privacy_decisions_created": "EVIDENCE_ACQUISITION_PRIVACY_DECISION_FORBIDDEN",
        "approvals_created": "EVIDENCE_ACQUISITION_APPROVAL_CREATION_FORBIDDEN",
        "external_validation_completed": "EVIDENCE_ACQUISITION_EXTERNAL_VALIDATION_FORBIDDEN",
    }
    for field, code in boundary_codes.items():
        _require(type(document.get(field)) is bool, "EVIDENCE_ACQUISITION_BOUNDARY_INVALID", field)
        _require(document[field] is False, code, f"{field} must remain false")

    requirements = document.get("artifact_requirements")
    _require(isinstance(requirements, list), "EVIDENCE_ACQUISITION_REQUIREMENTS_INVALID", "artifact_requirements")
    _require(tuple(item.get("gap_id") for item in requirements) == EXPECTED_GAP_IDS, "EVIDENCE_ACQUISITION_GAP_COVERAGE_INVALID", "exact ordered gap coverage required")
    for item in requirements:
        gap_id = item["gap_id"]
        _require(item.get("artifact_status") in ARTIFACT_STATUSES, "EVIDENCE_ACQUISITION_STATUS_INVALID", gap_id)
        for field in ("required_artifact_type", "purpose", "verification_rule"):
            _require(isinstance(item.get(field), str) and item[field], "EVIDENCE_ACQUISITION_REQUIREMENT_INVALID", f"{gap_id}.{field}")
        ownership = item.get("ownership")
        _require(isinstance(ownership, dict) and set(ownership) == ROLE_FIELDS, "EVIDENCE_ACQUISITION_OWNERSHIP_INVALID", gap_id)
        _require(all(isinstance(value, str) and value for value in ownership.values()), "EVIDENCE_ACQUISITION_OWNERSHIP_INVALID", gap_id)
        if item["artifact_status"] == "MISSING":
            _require(all(item.get(field) is None for field in CLOSURE_FIELDS), "EVIDENCE_ACQUISITION_MISSING_ARTIFACT_CLAIM", gap_id)
        if item["artifact_status"] in {"VERIFIED", "CLOSED"}:
            _require(all(isinstance(item.get(field), str) and item[field] for field in CLOSURE_FIELDS), "EVIDENCE_ACQUISITION_CLOSED_WITHOUT_REFERENCE", gap_id)

    addressed = sum(item["artifact_status"] == "CLOSED" for item in requirements)
    _require(document.get("gaps_addressed") == addressed, "EVIDENCE_ACQUISITION_GAP_COUNT_MISMATCH", "gaps_addressed")
    _require(isinstance(document.get("artifact_closure_requirements"), list) and len(document["artifact_closure_requirements"]) == 5, "EVIDENCE_ACQUISITION_CLOSURE_RULES_INVALID", "closure rules")
    _require(isinstance(document.get("limitations"), list) and document["limitations"], "EVIDENCE_ACQUISITION_LIMITATIONS_REQUIRED", "limitations")

    missing = [item["gap_id"] for item in requirements if item["artifact_status"] == "MISSING"]
    open_requirements = [item["gap_id"] for item in requirements if item["artifact_status"] != "CLOSED"]
    return {
        "result_type": "SAEE_EVIDENCE_ACQUISITION_PLAN_RESULT",
        "plan_version": "0.1",
        "current_readiness": "NO_GO",
        "pilot_status": "not_authorized",
        "open_artifact_requirements": open_requirements,
        "open_artifact_requirement_count": len(open_requirements),
        "missing_evidence": missing,
        "missing_evidence_count": len(missing),
        "gaps_addressed": addressed,
        "evidence_acquisition_started": False,
        "evidence_records_created": False,
        "pilot_authorized": False,
        "data_collected": False,
        "external_parties_contacted": False,
        "external_validation_completed": False,
        "production_ready": False,
    }


def review_evidence_acquisition_plan_path(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return evaluate_evidence_acquisition_plan(raw)
