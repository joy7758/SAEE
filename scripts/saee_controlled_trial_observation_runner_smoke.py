#!/usr/bin/env python3
"""Smoke check for the SAEE controlled trial observation runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBS_DIR = ROOT / "phase_b_product/validation/controlled_trial_observations"
README_PATH = OBS_DIR / "README.md"
INPUT_JSON = OBS_DIR / "local_trial_observation_input.json"
RESULT_JSON = OBS_DIR / "local_trial_observation_result.json"
RESULT_MD = OBS_DIR / "local_trial_observation_result.md"
DOC_PATH = ROOT / "phase_b_product/validation/CONTROLLED_TRIAL_OBSERVATION_RUNNER_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_CONTROLLED_TRIAL_OBSERVATION_RUNNER_RECOMMENDATION_GATE.md"
RUNNER_PATH = ROOT / "scripts/saee_controlled_trial_observation_runner.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_CONTROLLED_TRIAL_OBSERVATION_RUNNER_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [
        README_PATH,
        INPUT_JSON,
        RESULT_JSON,
        RESULT_MD,
        DOC_PATH,
        GATE_PATH,
        RUNNER_PATH,
    ]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    result = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    observation_input = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    require(
        result.get("observation_type") == "saee_controlled_trial_observation_runner",
        "wrong observation_type",
    )
    require(result.get("controlled_trial_observation_runner_v0_1") is True, "runner flag")
    require(result.get("observation_scope") == "local_mvp_demo_observation", "scope drift")
    require(
        result.get("observation_status") == "local_observation_recorded",
        "status must be local_observation_recorded",
    )
    require(result.get("human_review_required") is True, "human review required")
    require(result.get("blockers_closed_by_observation") == 0, "must close zero blockers")

    expected_false = [
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "customer_data_collected",
        "production_data_collected",
        "paid_trial_enabled",
        "payment_provider_configured",
        "product_launched",
        "public_sdk_released",
        "external_ai_assistant_tested",
        "external_validation_claim",
        "private_core_exposed",
        "api_schema_modified",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "external_calls_made",
    ]
    for key in expected_false:
        require(result.get(key) is False, f"result {key} must be false")

    require(observation_input.get("local_only") is True, "input local_only must be true")
    require(
        observation_input.get("public_service_layer_used") is True,
        "input must record public service layer use",
    )
    require(observation_input.get("external_calls_made") is False, "input external calls false")
    require(observation_input.get("agent_count") == 3, "input must record 3 agents")
    require(observation_input.get("repeat_runs") == 5, "input repeat_runs must be 5")

    demo = result.get("demo_output_summary", {})
    require(demo.get("experiment_id") == "controlled-trial-local-e2e", "experiment_id drift")
    require(demo.get("status") == "completed", "demo status must be completed")
    require(demo.get("recommended_agent") == "agent-b", "recommended_agent must be agent-b")
    require(demo.get("ranking_top") == "agent-b", "ranking_top must be agent-b")
    require(demo.get("agent_count") == 3, "agent_count must be 3")
    require(demo.get("stored_run_count") == 15, "stored_run_count must be 15")
    require(demo.get("failure_report_count") == 3, "failure_report_count must be 3")
    require(demo.get("survival_curve_count") == 3, "survival_curve_count must be 3")
    fields = demo.get("expected_fields_present", {})
    for field in [
        "decision_result",
        "recommended_agent",
        "confidence_score",
        "ranking",
        "failure_modes_summary",
        "survival_curves",
    ]:
        require(fields.get(field) is True, f"expected field {field} missing")

    local_execution = result.get("local_execution", {})
    require(local_execution.get("server_started") is False, "server must not be started")
    require(local_execution.get("browser_started") is False, "browser must not be started")
    require(
        local_execution.get("public_request_models_used") is True,
        "public request models must be used",
    )
    require(
        local_execution.get("public_experiment_service_used") is True,
        "public experiment service must be used",
    )
    require(
        local_execution.get("memory_experiment_store_used") is True,
        "memory experiment store must be used",
    )
    require(local_execution.get("request_limits_validated") is True, "request limits validated")

    combined_docs = "\n".join(
        [
            README_PATH.read_text(encoding="utf-8"),
            RESULT_MD.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "controlled_trial_observation_runner_v0_1: true",
        "observation_status: local_observation_recorded",
        "production_ready: false",
        "customer_validated: false",
        "customer_contacted: false",
        "product_launched: false",
        "external_ai_assistant_tested: false",
        "private_core_exposed: false",
        "blockers_closed_by_observation: 0",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "customer_contacted: true",
        '"customer_contacted": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "blockers_closed_by_observation: 1",
        '"blockers_closed_by_observation": 1',
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/validation/CONTROLLED_TRIAL_OBSERVATION_RUNNER_V0_1.md",
        "/phase_b_product/validation/controlled_trial_observations/README.md",
        "/phase_b_product/validation/controlled_trial_observations/local_trial_observation_input.json",
        "/phase_b_product/validation/controlled_trial_observations/local_trial_observation_result.json",
        "/phase_b_product/validation/controlled_trial_observations/local_trial_observation_result.md",
        "/docs/strategy/SAEE_CONTROLLED_TRIAL_OBSERVATION_RUNNER_RECOMMENDATION_GATE.md",
        "/scripts/saee_controlled_trial_observation_runner.py",
        "/scripts/saee_controlled_trial_observation_runner_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms missing " + ", ".join(missing_llms))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("controlled_trial_observation_runner_v0_1", {})
    expected_entry = {
        "status": "local_observation_recorded",
        "controlled_trial_observation_runner_v0_1": True,
        "observation_scope": "local_mvp_demo_observation",
        "expected_recommended_agent": "agent-b",
        "expected_status": "completed",
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_data_collected": False,
        "product_launched": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "blockers_closed_by_observation": 0,
    }
    for key, value in expected_entry.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_CONTROLLED_TRIAL_OBSERVATION_RUNNER_SMOKE: PASS "
        "observation_status=local_observation_recorded recommended_agent=agent-b "
        "production_ready=false customer_validated=false customer_contacted=false "
        "private_core_exposed=false blockers_closed_by_observation=0"
    )


if __name__ == "__main__":
    main()
