#!/usr/bin/env python3
"""Offline truth-surface validation for a pending or completed Phase 7.2 run."""

from __future__ import annotations

import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
STATUS=ROOT/"agent-interface/reliability/benchmark-runs/v1.1/SAEE_PHASE7_2_EXECUTION_STATUS.json"
CONFIG=ROOT/"agent-interface/reliability/benchmark-runs/saee-extended-internal-reliability-benchmark-run.v1.1.json"
RUNNER=ROOT/"scripts/saee_extended_internal_reliability_benchmark.py"
SCHEMA=ROOT/"schemas/saee-extended-internal-reliability-benchmark-result.schema.v1.1.json"
GATE=ROOT/"docs/strategy/SAEE_EXTENDED_INTERNAL_RELIABILITY_BENCHMARK_V1_1_RECOMMENDATION_GATE.md"
PREFLIGHT=ROOT/"docs/research/SAEE_PHASE7_2_EXECUTION_PREFLIGHT.md"


def main() -> int:
    assert all(path.exists() for path in (STATUS,CONFIG,RUNNER,SCHEMA,GATE,PREFLIGHT))
    status=json.loads(STATUS.read_text(encoding="utf-8")); config=json.loads(CONFIG.read_text(encoding="utf-8"))
    assert status["implementation_ready"] is True and status["offline_preflight_passed"] is True
    assert status["additional_real_model_runs_required"]==30 and status["combined_runs_required"]==75
    assert config["additional_repetition_indices"]==[4,5]
    assert config["preserve_scenario_strata"] is True and config["preserve_failures_and_unavailability"] is True
    assert status["qianfan_substitution_allowed"] is False
    assert status["external_world_actions"] is False and status["ranking_generated"] is False and status["production_ready"] is False
    if status["execution_complete"]:
        assert status["additional_real_model_runs_attempted"]==30 and status["combined_runs_available"]==75 and status["blocking_condition"] is None
    else:
        assert status["additional_real_model_runs_attempted"]==0 and status["combined_runs_available"]==45
        assert status["blocking_condition"]=="ARK_API_KEY_NOT_IN_CURRENT_EXECUTION_ENVIRONMENT"
    source=RUNNER.read_text(encoding="utf-8")
    assert "ARK_API_KEY" not in source and "QIANFAN_API_KEY" not in source
    print("SAEE_EXTENDED_INTERNAL_RELIABILITY_PREFLIGHT_SMOKE: PASS")
    print(f"execution_complete={str(status['execution_complete']).lower()}")
    print(f"additional_real_model_runs_attempted={status['additional_real_model_runs_attempted']}/30")
    print(f"combined_runs_available={status['combined_runs_available']}/75")
    print("qianfan_substitution_allowed=false")
    print("external_world_actions=false")
    print("ranking_generated=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
