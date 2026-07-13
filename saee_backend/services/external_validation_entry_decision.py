"""Deterministic Phase 14 entry-decision gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
GAPS_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-gaps.v0.1.json"
READINESS_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-review.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-entry-decision.v0.1.json"
DECISION_SCHEMA = ROOT / "schemas/saee-external-validation-entry-decision.schema.v0.1.json"
CLOSURE_SCHEMA = ROOT / "schemas/saee-gap-closure-evidence.schema.v0.1.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def build_entry_decision(gaps: dict[str, Any] | None = None, closure_records: list[dict[str, Any]] | None = None, *, independent_review_completed: bool = False) -> dict[str, Any]:
    gaps = gaps or _load(GAPS_PATH)
    closure_records = closure_records or []
    closure_schema = _load(CLOSURE_SCHEMA)
    validator = Draft202012Validator(closure_schema)
    if any(list(validator.iter_errors(record)) for record in closure_records):
        raise ValueError("GAP_CLOSURE_EVIDENCE_INVALID")
    gap_items = gaps.get("gaps", [])
    gap_ids = {item.get("gap_id") for item in gap_items}
    if any(record["gap_id"] not in gap_ids for record in closure_records):
        raise ValueError("GAP_CLOSURE_REFERENCE_INVALID")
    verified = {record["gap_id"] for record in closure_records if record["review_status"] == "VERIFIED_CLOSED" and record["independent_review"] is True}
    required_open = [item for item in gap_items if item.get("required_before_external_validation") is True and item.get("gap_id") not in verified]
    critical_open = [item for item in required_open if item.get("severity") == "CRITICAL"]
    if critical_open:
        decision = "HOLD"
        rationale = ["Critical required gaps remain open.", "No entry decision may rely on self-declared or simulated closure evidence."]
    elif required_open or not independent_review_completed:
        decision = "CONDITIONAL_ENTRY_REVIEW"
        rationale = ["No critical gap remains, but required preparation or independent review is incomplete."]
    else:
        decision = "ENTRY_READY"
        rationale = ["All required gaps have independently verified closure evidence.", "ENTRY_READY does not authorize or start external validation."]
    return {
        "review_version": "0.1",
        "readiness_reference": "agent-interface/ecosystem/saee-external-validation-readiness-review.v0.1.json",
        "entry_decision_simulation_reference": "agent-interface/ecosystem/saee-entry-decision-simulation-result.v0.1.json",
        "gap_summary": {"required": len(required_open), "critical": len(critical_open), "verified_closed": len(verified)},
        "evidence_summary": {"closure_records": len(closure_records), "independently_verified_records": len(verified)},
        "independent_review_required": True,
        "independent_review_completed": independent_review_completed,
        "decision": decision,
        "decision_rationale": rationale,
        "current_gaps": [item["gap_id"] for item in required_open],
        "limitations": [
            "This review does not execute or authorize external validation.",
            "ENTRY_READY would permit only a separate entry review and explicit authorization process.",
            "No customer, adoption, marketplace, production or certification conclusion is established.",
        ],
        "truth_boundary": {"entry_decision_review": True, "external_validation": False, "execution_authorized": False, "participants_invited": 0, "external_agents_connected": False, "customer_validated": False, "adoption_validated": False, "production_ready": False},
    }


def validate_entry_decision(value: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["ENTRY_DECISION_INVALID"]}
    if list(Draft202012Validator(_load(DECISION_SCHEMA)).iter_errors(value)):
        reasons.append("ENTRY_DECISION_SCHEMA_INVALID")
    truth = value.get("truth_boundary", {})
    if isinstance(truth, dict) and (truth.get("external_validation") is not False or truth.get("execution_authorized") is not False):
        reasons.append("ENTRY_DECISION_EXTERNAL_STATE_FORBIDDEN")
    if value.get("decision") == "ENTRY_READY" and (value.get("current_gaps") or value.get("independent_review_completed") is not True):
        reasons.append("ENTRY_DECISION_READY_WITHOUT_EVIDENCE")
    if value.get("decision") in {"HOLD", "CONDITIONAL_ENTRY_REVIEW"} and not value.get("current_gaps"):
        reasons.append("ENTRY_DECISION_OPEN_STATE_WITHOUT_GAPS")
    if value.get("gap_summary", {}).get("verified_closed", 0) > value.get("evidence_summary", {}).get("independently_verified_records", 0):
        reasons.append("ENTRY_DECISION_FAKE_GAP_CLOSURE")
    return {"valid": not reasons, "reason_codes": list(dict.fromkeys(reasons))}


def validate_current_entry_decision() -> dict[str, Any]:
    stored = _load(RESULT_PATH)
    if stored != build_entry_decision():
        return {"valid": False, "reason_codes": ["ENTRY_DECISION_RESULT_DRIFT"]}
    return validate_entry_decision(stored)
