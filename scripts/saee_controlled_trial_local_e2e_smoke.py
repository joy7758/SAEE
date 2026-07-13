#!/usr/bin/env python3
"""Local E2E proof for the SAEE controlled trial demo payload.

This script uses the public request models and experiment service only. It does
not start a server, open a browser, call external services, or modify SAEE core
runtime behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.models.request import EnvironmentConfig, EvaluationConfig, ScenarioBatchRequest
from saee_backend.services.experiment_service import ExperimentService
from saee_backend.services.request_limits import validate_scenario_limits
from saee_backend.storage.memory_db import MemoryExperimentStore


def build_landing_demo_request() -> ScenarioBatchRequest:
    return ScenarioBatchRequest(
        experiment_id="controlled-trial-local-e2e",
        agents=[
            {
                "agent_id": "agent-a",
                "config": {"policy": "aggressive-experimental-risky-unguarded-fragile"},
                "type": "llm",
            },
            {
                "agent_id": "agent-b",
                "config": {"workflow": "guarded-stable-monitor-retry-bounded-safe"},
                "type": "workflow",
            },
            {
                "agent_id": "agent-c",
                "config": "rule-conservative-bounded-retry",
                "type": "rule",
            },
        ],
        environment=EnvironmentConfig(
            scenario_type="landing_demo_competition",
            noise_level=0.25,
            competition_intensity=0.55,
            time_horizon=60,
        ),
        evaluation_config=EvaluationConfig(
            metrics=["stability", "survival", "failure_mode", "ranking"],
            repeat_runs=5,
        ),
    )


def main() -> None:
    request = build_landing_demo_request()
    validate_scenario_limits(request)

    service = ExperimentService(MemoryExperimentStore())
    summary = service.run_experiment(request)
    ranking = service.get_ranking(summary.experiment_id)
    failures = service.get_failures(summary.experiment_id)
    survival = service.get_survival(summary.experiment_id)

    assert summary.status == "completed"
    assert summary.decision_result is not None
    assert summary.recommended_agent == "agent-b"
    assert summary.recommended_agent == summary.decision_result.recommended_agent
    assert summary.recommended_agent == ranking.ranking[0].agent_id
    assert len(summary.agents) == 3
    assert len(ranking.ranking) == 3
    assert len(failures) == 3
    assert len(survival) == 3
    assert all(curve.curve for curve in survival)
    assert set(summary.decision_result.failure_modes_summary) == {
        "agent-a",
        "agent-b",
        "agent-c",
    }
    assert service.store.get(summary.experiment_id) is not None
    assert len(service.store.get_runs(summary.experiment_id)) == 15
    assert 0.0 <= summary.confidence_score <= 1.0

    print(
        "SAEE_CONTROLLED_TRIAL_LOCAL_E2E_SMOKE: PASS "
        f"experiment_id={summary.experiment_id} "
        f"recommended_agent={summary.recommended_agent} "
        f"ranking_top={ranking.ranking[0].agent_id} "
        f"agents={len(summary.agents)} "
        "local_only=true "
        "external_calls_made=false "
        "production_ready=false "
        "customer_validated=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
