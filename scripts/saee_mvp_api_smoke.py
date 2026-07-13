#!/usr/bin/env python3
"""Smoke check for the SAEE MVP real evaluation service layer."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.models.request import EnvironmentConfig, EvaluationConfig, ScenarioBatchRequest
from saee_backend.services.experiment_service import ExperimentService
from saee_backend.storage.memory_db import MemoryExperimentStore


def build_request(agent_b_config) -> ScenarioBatchRequest:
    return ScenarioBatchRequest(
        experiment_id="smoke-agent-stability",
        agents=[
            {
                "agent_id": "agent-a",
                "config": {"policy": "aggressive-experimental-risky-unguarded-fragile"},
                "type": "llm",
            },
            {
                "agent_id": "agent-b",
                "config": agent_b_config,
                "type": "workflow",
            },
            {"agent_id": "agent-c", "config": "rule-conservative-bounded-retry", "type": "rule"},
        ],
        environment=EnvironmentConfig(
            scenario_type="rag_policy_stress_test",
            noise_level=0.25,
            competition_intensity=0.55,
            time_horizon=60,
        ),
        evaluation_config=EvaluationConfig(
            metrics=["stability", "survival", "failure_mode", "ranking"],
            repeat_runs=5,
        ),
    )


def score_by_agent(summary) -> dict[str, float]:
    return {item.agent_id: item.final_score for item in summary.agents}


def main() -> None:
    service = ExperimentService(MemoryExperimentStore())
    req = build_request({"workflow": "guarded-stable-monitor-retry-bounded-safe"})

    first_summary = service.run_experiment(req)
    listed = service.list_experiments()
    first_stability = service.get_stability(first_summary.experiment_id)
    first_failures = service.get_failures(first_summary.experiment_id)
    first_ranking = service.get_ranking(first_summary.experiment_id)
    first_survival = service.get_survival(first_summary.experiment_id)

    second_summary = service.run_experiment(req)
    second_ranking = service.get_ranking(second_summary.experiment_id)

    assert first_summary.model_dump() == second_summary.model_dump()
    assert first_ranking.model_dump() == second_ranking.model_dump()
    assert first_summary.status == "completed"
    assert listed.count == 1
    assert listed.experiments[0].experiment_id == first_summary.experiment_id
    assert listed.experiments[0].status == "completed"
    assert listed.experiments[0].recommended_agent == first_summary.recommended_agent
    assert listed.experiments[0].confidence_score == first_summary.confidence_score
    assert first_summary.decision_result is not None
    assert first_summary.recommended_agent == first_summary.decision_result.recommended_agent
    assert first_summary.confidence_score == first_summary.decision_result.confidence_score
    assert first_summary.recommended_agent == first_ranking.ranking[0].agent_id
    assert first_summary.confidence_score == first_ranking.ranking[0].score
    assert len(first_summary.agents) == 3
    assert len(first_stability) == 3
    assert len(first_failures) == 3
    assert len(first_ranking.ranking) == 3
    assert len(first_summary.decision_result.ranking) == 3
    assert set(first_summary.decision_result.failure_modes_summary) == {
        "agent-a",
        "agent-b",
        "agent-c",
    }
    assert len(first_survival) == 3
    assert all(curve.curve for curve in first_survival)
    assert all(0.0 <= item.final_score <= 1.0 for item in first_summary.agents)
    assert len(service.store.get_runs(first_summary.experiment_id)) == 15
    assert len(service.store.get_metrics(first_summary.experiment_id)) == 3

    changed_service = ExperimentService(MemoryExperimentStore())
    changed_req = build_request({"workflow": "aggressive-experimental-risky-unguarded-fragile"})
    changed_summary = changed_service.run_experiment(changed_req)
    original_scores = score_by_agent(first_summary)
    changed_scores = score_by_agent(changed_summary)
    assert original_scores["agent-b"] != changed_scores["agent-b"]
    assert first_ranking.ranking != changed_service.get_ranking(changed_summary.experiment_id).ranking

    fastapi_available = importlib.util.find_spec("fastapi") is not None
    print(
        "SAEE_MVP_API_SMOKE: PASS "
        f"experiment_id={first_summary.experiment_id} "
        f"agents={len(first_summary.agents)} "
        "deterministic=true "
        "multi_run=true "
        "decision_result=true "
        "experiment_listing=true "
        "config_sensitive=true "
        f"fastapi_available={str(fastapi_available).lower()}"
    )


if __name__ == "__main__":
    main()
