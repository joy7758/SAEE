"""Offline consistency review for the SAEE pilot readiness gap plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BLOCKING_LEVELS = ("CRITICAL", "HIGH", "MEDIUM")
GAP_STATUSES = {"OPEN", "EVIDENCE_READY", "CLOSED"}


class PilotGapTrackingError(ValueError):
    """Stable gap-plan validation error."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise PilotGapTrackingError(code, detail)


def evaluate_pilot_gap_plan(document: dict[str, Any]) -> dict[str, Any]:
    """Validate gap metadata and compute whether a future re-review may start."""

    _require(isinstance(document, dict), "PILOT_GAP_INPUT_INVALID", "JSON object required")
    _require(document.get("saee_pilot_readiness_gap_plan_v0_1") is True, "PILOT_GAP_IDENTITY_INVALID", "root marker")
    _require(document.get("plan_version") == "0.1", "PILOT_GAP_VERSION_INVALID", "plan version")
    _require(document.get("current_readiness") in {"NO_GO", "CONDITIONAL_GO", "GO"}, "PILOT_GAP_READINESS_INVALID", "current_readiness")
    for field in ("future_reassessment_allowed", "pilot_authorized", "execution_started", "data_created", "approvals_created", "external_validation_completed"):
        _require(type(document.get(field)) is bool, "PILOT_GAP_BOUNDARY_INVALID", field)
    _require(document["pilot_authorized"] is False, "PILOT_GAP_AUTHORIZATION_FORBIDDEN", "pilot_authorized must remain false")
    _require(document["execution_started"] is False, "PILOT_GAP_EXECUTION_FORBIDDEN", "execution_started must remain false")
    _require(document["data_created"] is False, "PILOT_GAP_DATA_CREATION_FORBIDDEN", "data_created must remain false")
    _require(document["approvals_created"] is False, "PILOT_GAP_APPROVAL_CREATION_FORBIDDEN", "approvals_created must remain false")
    _require(document["external_validation_completed"] is False, "PILOT_GAP_EXTERNAL_VALIDATION_FORBIDDEN", "external validation unsupported")

    gaps = document.get("gaps")
    _require(isinstance(gaps, list) and gaps, "PILOT_GAPS_REQUIRED", "non-empty gaps")
    seen: set[str] = set()
    for gap in gaps:
        _require(isinstance(gap, dict), "PILOT_GAP_RECORD_INVALID", "gap object")
        gap_id = gap.get("id")
        _require(isinstance(gap_id, str) and gap_id, "PILOT_GAP_RECORD_INVALID", "gap id")
        _require(gap_id not in seen, "PILOT_GAP_RECORD_INVALID", f"duplicate {gap_id}")
        seen.add(gap_id)
        _require(gap.get("blocking") in BLOCKING_LEVELS, "PILOT_GAP_BLOCKING_INVALID", gap_id)
        _require(gap.get("status") in GAP_STATUSES, "PILOT_GAP_STATUS_INVALID", gap_id)
        for field in ("title", "current_state", "required_action", "required_artifact", "completion_criteria"):
            _require(isinstance(gap.get(field), str) and gap[field], "PILOT_GAP_RECORD_INVALID", f"{gap_id}.{field}")
        _require(isinstance(gap.get("required_future_evidence"), list) and gap["required_future_evidence"], "PILOT_GAP_FUTURE_EVIDENCE_REQUIRED", gap_id)
        _require(isinstance(gap.get("evidence_refs"), list), "PILOT_GAP_EVIDENCE_REFS_INVALID", gap_id)
        if gap["status"] in {"EVIDENCE_READY", "CLOSED"}:
            _require(bool(gap["evidence_refs"]), "PILOT_GAP_COMPLETED_WITHOUT_EVIDENCE", gap_id)

    open_gaps = [gap["id"] for gap in gaps if gap["status"] == "OPEN"]
    critical_open = [gap["id"] for gap in gaps if gap["status"] == "OPEN" and gap["blocking"] == "CRITICAL"]
    evidence_pending = [gap["id"] for gap in gaps if gap["status"] == "EVIDENCE_READY"]
    computed_reassessment = not open_gaps and all(gap["evidence_refs"] for gap in gaps)

    if critical_open:
        _require(document["current_readiness"] == "NO_GO", "PILOT_GAP_CRITICAL_READINESS_MISMATCH", "critical gaps require NO_GO")
    _require(document["current_readiness"] == "NO_GO", "PILOT_GAP_CURRENT_READINESS_CHANGED", "this plan must remain NO_GO")
    _require(document["future_reassessment_allowed"] == computed_reassessment, "PILOT_GAP_REASSESSMENT_MISMATCH", "future_reassessment_allowed")
    _require(isinstance(document.get("limitations"), list) and document["limitations"], "PILOT_GAP_LIMITATIONS_REQUIRED", "limitations")

    highest = "NONE"
    for level in BLOCKING_LEVELS:
        if any(gap["status"] == "OPEN" and gap["blocking"] == level for gap in gaps):
            highest = level
            break
    return {
        "result_type": "SAEE_PILOT_GAP_REVIEW_RESULT",
        "plan_version": "0.1",
        "current_readiness": "NO_GO",
        "open_gaps": open_gaps,
        "open_gap_count": len(open_gaps),
        "critical_open_gaps": critical_open,
        "critical_open_gap_count": len(critical_open),
        "evidence_ready_pending_rereview": evidence_pending,
        "blocking_level": highest,
        "reassessment_allowed": computed_reassessment,
        "pilot_authorized": False,
        "execution_started": False,
        "gap_resolution_claimed": False,
        "external_validation_completed": False,
        "production_ready": False,
    }


def review_pilot_gap_plan_path(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return evaluate_pilot_gap_plan(raw)

