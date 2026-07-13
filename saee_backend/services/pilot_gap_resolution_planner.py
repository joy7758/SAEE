"""Offline consistency validator for SAEE Pilot Gap Resolution Planning v0.1.

The validator checks a remediation roadmap. It never creates evidence, assigns
real owners, closes a gap, changes readiness, or authorizes a Pilot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_TOP_LEVEL = {
    "gap_plan_version",
    "plan_stage",
    "readiness_status",
    "source_readiness_result_ref",
    "documentation_ref",
    "gaps",
    "dependency_order",
    "reassessment_rules",
    "gaps_closed",
    "evidence_acquired",
    "readiness_changed",
    "pilot_authorized",
    "execution_authorized",
    "external_validation_completed",
    "production_ready",
    "network_accessed",
    "external_execution",
}
EXPECTED_GAP_IDS = {
    "GAP_IDENTITY_AUTHENTICATION_DESIGN",
    "GAP_IDENTITY_EXTERNAL_IDENTITY_VERIFICATION",
    "GAP_SECURITY_FORMAL_REVIEW",
    "GAP_SECURITY_CREDENTIAL_POLICY",
    "GAP_SECURITY_INCIDENT_HANDLING",
    "GAP_DATA_OWNERSHIP",
    "GAP_DATA_USAGE_PERMISSION",
    "GAP_DATA_RETENTION_APPROVAL",
    "GAP_DATA_DELETION_PROCESS",
    "GAP_RUNTIME_ISOLATION_EVIDENCE",
    "GAP_RUNTIME_MONITORING_EVIDENCE",
    "GAP_RUNTIME_RECOVERY_EVIDENCE",
    "GAP_RUNTIME_ROLLBACK_EVIDENCE",
    "GAP_HUMAN_RESPONSIBLE_OWNER",
    "GAP_HUMAN_ESCALATION_OWNER",
}
EXPECTED_CATEGORY_COUNTS = {"IDENTITY": 2, "SECURITY": 3, "DATA": 4, "RUNTIME": 4, "HUMAN_GOVERNANCE": 2}
EXPECTED_OWNER_ROLES = {
    "IDENTITY": "IDENTITY_SECURITY_LEAD",
    "SECURITY": "SECURITY_REVIEWER",
    "DATA": "DATA_GOVERNANCE_OWNER",
    "RUNTIME": "RUNTIME_OPERATOR",
    "HUMAN_GOVERNANCE": "HUMAN_GOVERNANCE_OWNER",
}
EXPECTED_DEPENDENCY_ORDER = ["IDENTITY", "SECURITY", "DATA", "RUNTIME", "HUMAN_GOVERNANCE", "RE_READINESS_REVIEW"]

GAP_PLAN_INVALID = "GAP_PLAN_INVALID"
GAP_PLAN_STRUCTURE_INVALID = "GAP_PLAN_STRUCTURE_INVALID"
GAP_PLAN_FAKE_CLOSURE_FORBIDDEN = "GAP_PLAN_FAKE_CLOSURE_FORBIDDEN"
GAP_PLAN_FAKE_EVIDENCE_FORBIDDEN = "GAP_PLAN_FAKE_EVIDENCE_FORBIDDEN"
GAP_PLAN_READINESS_UPGRADE_FORBIDDEN = "GAP_PLAN_READINESS_UPGRADE_FORBIDDEN"
GAP_PLAN_PILOT_AUTHORIZATION_FORBIDDEN = "GAP_PLAN_PILOT_AUTHORIZATION_FORBIDDEN"
GAP_PLAN_EXECUTION_CLAIM_FORBIDDEN = "GAP_PLAN_EXECUTION_CLAIM_FORBIDDEN"
GAP_PLAN_REASSESSMENT_FORBIDDEN = "GAP_PLAN_REASSESSMENT_FORBIDDEN"
GAP_PLAN_GAP_COVERAGE_INVALID = "GAP_PLAN_GAP_COVERAGE_INVALID"
GAP_PLAN_SOURCE_BLOCKER_COVERAGE_INVALID = "GAP_PLAN_SOURCE_BLOCKER_COVERAGE_INVALID"
GAP_PLAN_ARTIFACT_REQUIREMENT_INVALID = "GAP_PLAN_ARTIFACT_REQUIREMENT_INVALID"
GAP_PLAN_DEPENDENCY_INVALID = "GAP_PLAN_DEPENDENCY_INVALID"
GAP_PLAN_REFERENCE_INVALID = "GAP_PLAN_REFERENCE_INVALID"


def _result(value: Any, valid: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "saee_pilot_gap_resolution_plan_validation_result_v0_1": True,
        "plan_valid": valid,
        "plan_version": value.get("gap_plan_version", "") if isinstance(value, dict) else "",
        "readiness_status": "NOT_READY",
        "gaps_total": 15,
        "gaps_open": 15,
        "gaps_closed": 0,
        "evidence_acquired": False,
        "readiness_changed": False,
        "reassessment_allowed": False,
        "pilot_authorized": False,
        "execution_authorized": False,
        "reason_codes": reasons,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _has_cycle(dependencies: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for dependency in dependencies[node]:
            if visit(dependency):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in dependencies)


def validate_pilot_gap_resolution_plan(value: Any) -> dict[str, Any]:
    """Validate a planning-only roadmap against current readiness truth."""

    if not isinstance(value, dict):
        return _result(value, False, [GAP_PLAN_INVALID])
    if value.get("readiness_status") != "NOT_READY" or value.get("readiness_changed") is not False:
        return _result(value, False, [GAP_PLAN_READINESS_UPGRADE_FORBIDDEN])
    if value.get("pilot_authorized") is not False:
        return _result(value, False, [GAP_PLAN_PILOT_AUTHORIZATION_FORBIDDEN])
    if value.get("execution_authorized") is not False or value.get("external_execution") is not False:
        return _result(value, False, [GAP_PLAN_EXECUTION_CLAIM_FORBIDDEN])
    if value.get("gaps_closed") != 0:
        return _result(value, False, [GAP_PLAN_FAKE_CLOSURE_FORBIDDEN])
    if value.get("evidence_acquired") is not False:
        return _result(value, False, [GAP_PLAN_FAKE_EVIDENCE_FORBIDDEN])
    rules = value.get("reassessment_rules")
    if isinstance(rules, dict) and (rules.get("reassessment_allowed") is not False or rules.get("go_authorized") is not False):
        return _result(value, False, [GAP_PLAN_REASSESSMENT_FORBIDDEN])
    if set(value) != EXPECTED_TOP_LEVEL or value.get("gap_plan_version") != "0.1" or value.get("plan_stage") != "planning_only":
        return _result(value, False, [GAP_PLAN_STRUCTURE_INVALID])

    gaps = value.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != 15:
        return _result(value, False, [GAP_PLAN_GAP_COVERAGE_INVALID])
    gap_ids = [gap.get("gap_id") for gap in gaps if isinstance(gap, dict)]
    if len(gap_ids) != 15 or set(gap_ids) != EXPECTED_GAP_IDS:
        return _result(value, False, [GAP_PLAN_GAP_COVERAGE_INVALID])

    category_counts = {category: 0 for category in EXPECTED_CATEGORY_COUNTS}
    dependencies: dict[str, list[str]] = {}
    source_blockers: set[str] = set()
    artifacts: set[str] = set()
    for gap in gaps:
        if not isinstance(gap, dict):
            return _result(value, False, [GAP_PLAN_STRUCTURE_INVALID])
        if gap.get("current_status") != "OPEN":
            return _result(value, False, [GAP_PLAN_FAKE_CLOSURE_FORBIDDEN])
        if gap.get("evidence_refs") != []:
            return _result(value, False, [GAP_PLAN_FAKE_EVIDENCE_FORBIDDEN])
        category = gap.get("category")
        if category not in EXPECTED_CATEGORY_COUNTS or gap.get("owner_role") != EXPECTED_OWNER_ROLES[category]:
            return _result(value, False, [GAP_PLAN_ARTIFACT_REQUIREMENT_INVALID])
        category_counts[category] += 1
        artifact = gap.get("required_artifact_type")
        verification = gap.get("verification_method")
        if not isinstance(artifact, str) or not artifact or artifact in artifacts or not isinstance(verification, str) or not verification:
            return _result(value, False, [GAP_PLAN_ARTIFACT_REQUIREMENT_INVALID])
        artifacts.add(artifact)
        blockers = gap.get("source_blocker_ids")
        if not isinstance(blockers, list) or not blockers or any(not isinstance(blocker, str) or not blocker for blocker in blockers):
            return _result(value, False, [GAP_PLAN_SOURCE_BLOCKER_COVERAGE_INVALID])
        source_blockers.update(blockers)
        deps = gap.get("dependencies")
        if not isinstance(deps, list) or len(deps) != len(set(deps)) or gap["gap_id"] in deps:
            return _result(value, False, [GAP_PLAN_DEPENDENCY_INVALID])
        dependencies[gap["gap_id"]] = deps

    if category_counts != EXPECTED_CATEGORY_COUNTS:
        return _result(value, False, [GAP_PLAN_GAP_COVERAGE_INVALID])
    if any(dependency not in EXPECTED_GAP_IDS for deps in dependencies.values() for dependency in deps) or _has_cycle(dependencies):
        return _result(value, False, [GAP_PLAN_DEPENDENCY_INVALID])
    if value.get("dependency_order") != EXPECTED_DEPENDENCY_ORDER:
        return _result(value, False, [GAP_PLAN_DEPENDENCY_INVALID])

    source_ref = value.get("source_readiness_result_ref")
    doc_ref = value.get("documentation_ref")
    if not isinstance(source_ref, str) or not (ROOT / source_ref).is_file() or not isinstance(doc_ref, str) or not (ROOT / doc_ref).is_file():
        return _result(value, False, [GAP_PLAN_REFERENCE_INVALID])
    try:
        source = json.loads((ROOT / source_ref).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _result(value, False, [GAP_PLAN_REFERENCE_INVALID])
    if source.get("readiness_status") != "NOT_READY" or set(source.get("blocking_gaps", [])) != source_blockers:
        return _result(value, False, [GAP_PLAN_SOURCE_BLOCKER_COVERAGE_INVALID])

    if (
        not isinstance(rules, dict)
        or rules.get("all_gaps_closed_required") is not True
        or rules.get("all_artifacts_verified_required") is not True
        or rules.get("evidence_refs_required_for_future_closure") is not True
        or rules.get("independent_re_review_required") is not True
        or rules.get("reassessment_allowed") is not False
        or rules.get("go_authorized") is not False
        or value.get("external_validation_completed") is not False
        or value.get("production_ready") is not False
        or value.get("network_accessed") is not False
    ):
        return _result(value, False, [GAP_PLAN_STRUCTURE_INVALID])
    return _result(value, True, [])


def validate_gap_resolution_result_truth(value: Any) -> dict[str, Any]:
    """Reject machine results that overclaim evidence acquisition or closure."""

    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": [GAP_PLAN_INVALID]}
    expected = {
        "gaps_total": 15,
        "gaps_closed": 0,
        "evidence_acquired": False,
        "readiness_changed": False,
        "reassessment_allowed": False,
        "pilot_authorized": False,
        "execution_authorized": False,
        "production_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            return {"valid": False, "reason_codes": [f"GAP_PLAN_RESULT_OVERCLAIM:{field}"]}
    return {"valid": True, "reason_codes": []}


def validate_pilot_gap_resolution_plan_path(path: Path) -> dict[str, Any]:
    """Validate one checked-in local plan without external actions."""

    return validate_pilot_gap_resolution_plan(json.loads(path.read_text(encoding="utf-8")))
