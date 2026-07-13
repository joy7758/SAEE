"""Offline adapters for checked-in SAEE study and benchmark artifacts."""

from __future__ import annotations

from typing import Any

from .assessment_adapter import assess_reliability_run


def adapt_reliability_study(study: dict[str, Any], *, source_ref: str) -> list[dict[str, Any]]:
    assessments = []
    for agent in study["agent_profiles"]:
        for run in agent["run_results"]:
            assessments.append(assess_reliability_run(run, agent_profile=agent["agent_profile"], scenario_id=study["scenario_id"], source_ref=source_ref))
    return assessments


def adapt_stateful_business(validation: dict[str, Any], *, source_ref: str) -> list[dict[str, Any]]:
    run = {
        "run_id": validation["run_ref"], "status": "completed", "unavailable_reason": None,
        "missing_evidence": [], "evidence_outcomes": [], "repeated_tool_calls": 0,
        "observed_risk_signals": [],
    }
    return [assess_reliability_run(run, agent_profile=validation["model"], scenario_id=validation["scenario"], source_ref=source_ref, source_type="STATEFUL_BUSINESS_RUN")]


def adapt_recommendation_benchmark(benchmark: dict[str, Any], *, source_ref: str) -> list[dict[str, Any]]:
    assessments = []
    for item in benchmark["per_agent"]:
        available = item["evaluated_scenarios"] > 0
        run = {"run_id": f"run:recommendation:{item['agent_id'].lower()}", "status": "completed" if available else "unavailable", "unavailable_reason": None if available else "benchmark_assessment_unavailable", "missing_evidence": [], "evidence_outcomes": [], "repeated_tool_calls": 0, "observed_risk_signals": []}
        assessments.append(assess_reliability_run(run, agent_profile=item["agent_id"], scenario_id="saee-agent-recommendation-benchmark:v0.1", source_ref=source_ref, source_type="RECOMMENDATION_BENCHMARK_RUN"))
    return assessments
