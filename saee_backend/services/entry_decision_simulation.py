"""Deterministic local simulation for the Phase 14 entry-decision gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from saee_backend.services.external_validation_entry_decision import build_entry_decision


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "agent-interface/ecosystem/entry-decision-simulation"
GAPS_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-readiness-gaps.v0.1.json"
SCHEMA_PATH = ROOT / "schemas/saee-entry-decision-simulation.schema.v0.1.json"
CLOSURE_SCHEMA_PATH = ROOT / "schemas/saee-gap-closure-evidence.schema.v0.1.json"
ENTRY_REFERENCE = "agent-interface/ecosystem/saee-external-validation-entry-decision.v0.1.json"
LIMITATIONS = [
    "This is a deterministic local simulation and does not alter the current HOLD decision.",
    "No result authorizes or executes external validation.",
    "Synthetic closure records do not establish real gap closure, adoption, customer validation or production readiness.",
]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def _scenario_validator() -> Draft202012Validator:
    schema, closure = _load(SCHEMA_PATH), _load(CLOSURE_SCHEMA_PATH)
    registry = Registry().with_resource(closure["$id"], Resource.from_contents(closure))
    return Draft202012Validator(schema, registry=registry)


def _safe_local_ref(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or ref.startswith("/") or "://" in ref or ".." in Path(ref).parts:
        return False
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def simulate_entry_decision(scenario: dict[str, Any], gaps: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply canonical Phase 14 rules to one inert synthetic state."""

    if list(_scenario_validator().iter_errors(scenario)):
        raise ValueError("ENTRY_DECISION_SIMULATION_SCENARIO_INVALID")
    readiness = scenario["input_readiness"]
    gap_state = scenario["gap_state"]
    evidence = scenario["evidence_state"]
    review = scenario["independent_review_state"]
    records = gap_state["closure_records"]
    claimed_ids = set(gap_state["claimed_closed_gap_ids"])
    record_ids = {record["gap_id"] for record in records}
    rejected: list[str] = []
    if readiness["requested_execution_authorized"] or evidence["external_approval_claimed"]:
        rejected.append("ENTRY_DECISION_SIMULATION_AUTHORIZATION_FORBIDDEN")
    if any(evidence[field] for field in ("customer_validated", "adoption_claim", "market_validation", "production_ready")):
        rejected.append("ENTRY_DECISION_SIMULATION_EXTERNAL_CLAIM_FORBIDDEN")
    if claimed_ids != record_ids or (claimed_ids and (not evidence["closure_evidence_present"] or not evidence["evidence_verified"])):
        rejected.append("ENTRY_DECISION_SIMULATION_FAKE_CLOSURE")
    if review["completed"] and not _safe_local_ref(review["review_reference"]):
        rejected.append("ENTRY_DECISION_SIMULATION_FAKE_INDEPENDENT_REVIEW")
    if rejected:
        actual = "REJECTED"
    else:
        gaps = gaps or _load(GAPS_PATH)
        verified_ids = {record["gap_id"] for record in records if record["review_status"] == "VERIFIED_CLOSED" and record["independent_review"] is True}
        open_items = [item for item in gaps["gaps"] if item["required_before_external_validation"] is True and item["gap_id"] not in verified_ids]
        critical_open = sum(item["severity"] == "CRITICAL" for item in open_items)
        expected_input = (len(open_items), critical_open, not open_items)
        declared_input = (readiness["required_gaps_open"], readiness["critical_gaps_open"], readiness["all_required_gaps_closed"])
        if declared_input != expected_input:
            rejected.append("ENTRY_DECISION_SIMULATION_READINESS_MISMATCH")
            actual = "REJECTED"
        else:
            actual = build_entry_decision(gaps, records, independent_review_completed=review["completed"])["decision"]
    return {
        "simulation_id": scenario["simulation_id"],
        "decision_result": actual,
        "expected_result": scenario["decision_result"],
        "matched_expected": actual == scenario["decision_result"],
        "reason_codes": rejected or [f"ENTRY_DECISION_SIMULATION_{actual}"],
        "execution_authorized": False,
    }


def run_entry_decision_simulation() -> dict[str, Any]:
    scenarios = [_load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    results = [simulate_entry_decision(scenario) for scenario in scenarios]
    decisions = {name: sum(item["decision_result"] == name for item in results) for name in ("HOLD", "CONDITIONAL_ENTRY_REVIEW", "ENTRY_READY", "REJECTED")}
    return {
        "simulation_version": "0.1",
        "entry_decision_reference": ENTRY_REFERENCE,
        "scenario_results": results,
        "decision_distribution": decisions,
        "authorization_distribution": {"execution_authorized_count": 0, "execution_not_authorized_count": len(results)},
        "limitations": list(LIMITATIONS),
        "truth_boundary": {
            "entry_decision_simulation": True,
            "external_validation": False,
            "execution_authorized": False,
            "real_participants": False,
            "participants_invited": 0,
            "customer_validated": False,
            "adoption_validated": False,
            "production_ready": False,
            "network_accessed": False,
            "subprocess_started": False,
            "external_execution": False,
        },
    }

