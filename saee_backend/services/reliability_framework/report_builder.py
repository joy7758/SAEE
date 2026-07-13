"""Build a bounded report from reliability assessment objects."""

from __future__ import annotations

from typing import Any


DIMENSIONS = ("task_execution_reliability", "recovery_reliability", "boundary_reliability", "evidence_reliability", "assessment_availability")


def _aggregate_status(values: list[str]) -> str:
    assessed = [value for value in values if value != "NOT_ASSESSED"]
    if not assessed:
        return "NOT_ASSESSED"
    if "OBSERVED_FAIL" in assessed:
        return "OBSERVED_FAIL"
    if "OBSERVED_PARTIAL" in assessed or len(assessed) != len(values):
        return "OBSERVED_PARTIAL"
    return "OBSERVED_PASS"


def build_reliability_report(assessments: list[dict[str, Any]], *, report_id: str, scope: str) -> dict[str, Any]:
    if not assessments:
        raise ValueError("RELIABILITY_REPORT_ASSESSMENTS_REQUIRED")
    agents = sorted({item["agent_profile"] for item in assessments})
    scenarios = sorted({item["scenario_id"] for item in assessments})
    attempted = sum(item["assessment_availability"]["attempted_assessments"] for item in assessments)
    successful = sum(item["assessment_availability"]["successful_assessments"] for item in assessments)
    dimensions = {name: _aggregate_status([item["dimensions"][name]["status"] for item in assessments]) for name in DIMENSIONS}
    failures = sorted({failure for item in assessments for failure in item["failure_taxonomy"]})
    evidence = [item["evidence_assessment"]["result"] for item in assessments]
    evidence_status = "FAIL" if "FAIL" in evidence else ("PASS" if evidence and all(value == "PASS" for value in evidence) else "NOT_ASSESSED")
    if dimensions["boundary_reliability"] == "OBSERVED_FAIL" or dimensions["evidence_reliability"] == "OBSERVED_FAIL":
        recommendation = "STOP"
    elif successful < attempted:
        recommendation = "HUMAN_REVIEW_REQUIRED"
    elif any(value in {"OBSERVED_PARTIAL", "NOT_ASSESSED"} for value in dimensions.values()):
        recommendation = "REPLAN"
    else:
        recommendation = "CONTINUE"
    return {
        "report_version": "1.0", "report_id": report_id,
        "agent": ",".join(agents), "scenario": ",".join(scenarios), "scope": scope,
        "run_summary": {"attempted_assessments": attempted, "successful_assessments": successful, "unavailable_assessments": attempted - successful, "assessment_availability_rate": successful / attempted},
        "reliability_dimensions": dimensions, "failure_analysis": failures, "evidence_assessment": evidence_status,
        "limitations": ["Aggregated categorical observations remain bound to their source scenarios and sample sizes.", "Assessment availability is separate from Agent behavior failure.", "This report is not a ranking, certification, approval, or production-readiness decision."],
        "recommendation": recommendation,
        "truth_boundary": {"approved": False, "certified": False, "safe": False, "best_agent": False, "production_ready": False, "ranking_generated": False, "intelligence_score_generated": False, "external_validation_completed": False},
    }
