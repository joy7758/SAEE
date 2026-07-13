#!/usr/bin/env python3
"""Smoke check for SAEE request limits v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import (
    DEFAULT_MAX_AGENTS,
    DEFAULT_MAX_PAYLOAD_BYTES,
    DEFAULT_MAX_REPEAT_RUNS,
    DEFAULT_MAX_TIME_HORIZON,
    load_settings,
)
from saee_backend.models.request import EnvironmentConfig, EvaluationConfig, ScenarioBatchRequest
from saee_backend.services.request_limits import (
    RequestLimitViolation,
    scenario_payload_bytes,
    validate_scenario_limits,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_REQUEST_LIMITS_SMOKE: FAIL: {message}")


def build_request(agent_count: int = 3, repeat_runs: int = 5, time_horizon: int = 60) -> ScenarioBatchRequest:
    return ScenarioBatchRequest(
        experiment_id="request-limits-smoke",
        agents=[
            {
                "agent_id": f"agent-{idx}",
                "config": {"policy": "guarded-stable-retry-bounded"},
                "type": "agent",
            }
            for idx in range(agent_count)
        ],
        environment=EnvironmentConfig(
            scenario_type="request_limit_check",
            noise_level=0.2,
            competition_intensity=0.5,
            time_horizon=time_horizon,
        ),
        evaluation_config=EvaluationConfig(
            metrics=["stability", "survival", "failure_mode", "ranking"],
            repeat_runs=repeat_runs,
        ),
    )


def expect_violation(req: ScenarioBatchRequest, settings, token: str) -> None:
    try:
        validate_scenario_limits(req, settings)
    except RequestLimitViolation as exc:
        require(token in str(exc), f"violation must mention {token}")
        return
    raise SystemExit(f"SAEE_REQUEST_LIMITS_SMOKE: FAIL: expected violation for {token}")


def main() -> None:
    default = load_settings({})
    require(default.max_agents == DEFAULT_MAX_AGENTS, "default max_agents mismatch")
    require(default.max_repeat_runs == DEFAULT_MAX_REPEAT_RUNS, "default max_repeat_runs mismatch")
    require(default.max_time_horizon == DEFAULT_MAX_TIME_HORIZON, "default max_time_horizon mismatch")
    require(default.max_payload_bytes == DEFAULT_MAX_PAYLOAD_BYTES, "default max_payload_bytes mismatch")

    req = build_request()
    validate_scenario_limits(req, default)
    require(scenario_payload_bytes(req) > 0, "payload byte count must be positive")

    strict = load_settings(
        {
            "SAEE_MAX_AGENTS": "2",
            "SAEE_MAX_REPEAT_RUNS": "4",
            "SAEE_MAX_TIME_HORIZON": "50",
            "SAEE_MAX_PAYLOAD_BYTES": "256",
        }
    )
    expect_violation(build_request(agent_count=3), strict, "max_agents")
    expect_violation(build_request(agent_count=2, repeat_runs=5), strict, "max_repeat_runs")
    expect_violation(build_request(agent_count=2, repeat_runs=4, time_horizon=60), strict, "max_time_horizon")
    expect_violation(build_request(agent_count=2, repeat_runs=4, time_horizon=50), strict, "max_payload_bytes")

    boundary_doc = (ROOT / "phase_b_product/commercial_readiness/REQUEST_LIMITS_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_REQUEST_LIMITS_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("request_limits_v0_1: true" in boundary_doc, "request limits doc missing state")
    require("api_schema_modified: false" in boundary_doc, "request limits doc must preserve schema boundary")
    require("answer: conditional" in gate, "request limits gate must remain conditional")
    require("production_ready: false" in gate, "request limits gate must not claim production")

    print(
        "SAEE_REQUEST_LIMITS_SMOKE: PASS "
        "max_agents=true "
        "max_repeat_runs=true "
        "max_time_horizon=true "
        "max_payload_bytes=true "
        "api_schema_modified=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
