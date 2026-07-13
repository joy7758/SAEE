#!/usr/bin/env python3
"""Record one local SAEE controlled-trial observation.

This runner uses the existing public request models and experiment service to
produce a machine-checkable local observation record for the operator packet.
It does not start a server, open a browser, call external services, contact
customers, close blockers, or modify runtime/backend/kernel/API behavior.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.experiment_service import ExperimentService
from saee_backend.services.request_limits import validate_scenario_limits
from saee_backend.storage.memory_db import MemoryExperimentStore
from scripts.saee_controlled_trial_local_e2e_smoke import build_landing_demo_request


OUTPUT_DIR = ROOT / "phase_b_product/validation/controlled_trial_observations"
README_PATH = OUTPUT_DIR / "README.md"
INPUT_JSON = OUTPUT_DIR / "local_trial_observation_input.json"
RESULT_JSON = OUTPUT_DIR / "local_trial_observation_result.json"
RESULT_MD = OUTPUT_DIR / "local_trial_observation_result.md"
OPERATOR_TEMPLATE = (
    ROOT
    / "phase_b_product/validation/controlled_trial_operator_packet/local_trial_session_template.json"
)


BOUNDARY_FALSE_FLAGS: dict[str, bool] = {
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "customer_data_collected": False,
    "production_data_collected": False,
    "paid_trial_enabled": False,
    "payment_provider_configured": False,
    "product_launched": False,
    "public_sdk_released": False,
    "external_ai_assistant_tested": False,
    "external_validation_claim": False,
    "private_core_exposed": False,
    "api_schema_modified": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "external_calls_made": False,
}


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_input_record(template: dict[str, Any]) -> dict[str, Any]:
    request = build_landing_demo_request()
    return {
        "controlled_trial_observation_runner_v0_1": True,
        "input_scope": "local_mvp_demo_observation",
        "source_operator_template": str(OPERATOR_TEMPLATE.relative_to(ROOT)),
        "operator_template_session_scope": template.get("session_scope"),
        "operator_template_trial_status": template.get("trial_status"),
        "experiment_id": request.experiment_id,
        "agent_ids": [agent.agent_id for agent in request.agents],
        "agent_count": len(request.agents),
        "scenario_type": request.environment.scenario_type,
        "noise_level": request.environment.noise_level,
        "competition_intensity": request.environment.competition_intensity,
        "time_horizon": request.environment.time_horizon,
        "metrics": list(request.evaluation_config.metrics),
        "repeat_runs": request.evaluation_config.repeat_runs,
        "local_only": True,
        "public_service_layer_used": True,
        "external_calls_made": False,
        "customer_data_allowed": False,
        "customer_data_collected": False,
        "production_ready": False,
        "customer_validated": False,
    }


def build_result() -> dict[str, Any]:
    template = json.loads(OPERATOR_TEMPLATE.read_text(encoding="utf-8"))
    input_record = build_input_record(template)

    request = build_landing_demo_request()
    validate_scenario_limits(request)

    store = MemoryExperimentStore()
    service = ExperimentService(store)
    summary = service.run_experiment(request)
    ranking = service.get_ranking(summary.experiment_id)
    failures = service.get_failures(summary.experiment_id)
    survival = service.get_survival(summary.experiment_id)
    stored_runs = store.get_runs(summary.experiment_id)

    expected_fields_present = {
        "decision_result": summary.decision_result is not None,
        "recommended_agent": summary.recommended_agent is not None,
        "confidence_score": summary.confidence_score is not None,
        "ranking": bool(ranking.ranking),
        "failure_modes_summary": bool(
            summary.decision_result and summary.decision_result.failure_modes_summary
        ),
        "survival_curves": bool(survival),
    }

    return {
        "observation_type": "saee_controlled_trial_observation_runner",
        "observation_version": "v0.1",
        "controlled_trial_observation_runner_v0_1": True,
        "observation_scope": "local_mvp_demo_observation",
        "observation_status": "local_observation_recorded",
        "generated_by": "scripts/saee_controlled_trial_observation_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "input": input_record,
        "demo_output_summary": {
            "experiment_id": summary.experiment_id,
            "status": summary.status,
            "recommended_agent": summary.recommended_agent,
            "confidence_score": summary.confidence_score,
            "ranking_top": ranking.ranking[0].agent_id if ranking.ranking else None,
            "ranking": [
                {
                    "rank": item.rank,
                    "agent_id": item.agent_id,
                    "score": item.score,
                }
                for item in ranking.ranking
            ],
            "agent_count": len(summary.agents),
            "failure_report_count": len(failures),
            "survival_curve_count": len(survival),
            "stored_run_count": len(stored_runs),
            "expected_fields_present": expected_fields_present,
        },
        "local_execution": {
            "server_started": False,
            "browser_started": False,
            "public_request_models_used": True,
            "public_experiment_service_used": True,
            "memory_experiment_store_used": True,
            "request_limits_validated": True,
        },
        "human_review_required": True,
        "blockers_closed_by_observation": 0,
        "next_action": "Human review of local observation only; do not claim customer validation or production readiness.",
        **BOUNDARY_FALSE_FLAGS,
    }


def render_readme() -> str:
    return "\n".join(
        [
            "# SAEE Controlled Trial Observations",
            "",
            "Status: local MVP demo observation records only.",
            "",
            "This directory stores machine-checkable local observation results for the",
            "controlled trial operator packet. The runner uses the existing public",
            "request models, public experiment service, and in-memory experiment store.",
            "",
            "Generate the current local observation with:",
            "",
            "```bash",
            "python3 scripts/saee_controlled_trial_observation_runner.py",
            "```",
            "",
            "Primary files:",
            "",
            "- `local_trial_observation_input.json`",
            "- `local_trial_observation_result.json`",
            "- `local_trial_observation_result.md`",
            "",
            "Boundary:",
            "",
            "- production_ready: false",
            "- customer_validated: false",
            "- customer_contacted: false",
            "- customer_data_collected: false",
            "- product_launched: false",
            "- external_calls_made: false",
            "- external_ai_assistant_tested: false",
            "- private_core_exposed: false",
            "- blockers_closed_by_observation: 0",
            "",
        ]
    )


def render_markdown(result: dict[str, Any]) -> str:
    demo = result["demo_output_summary"]
    fields = demo["expected_fields_present"]
    field_rows = [
        f"| `{name}` | {str(value).lower()} |" for name, value in fields.items()
    ]
    ranking_rows = [
        f"| {item['rank']} | `{item['agent_id']}` | {item['score']:.4f} |"
        for item in demo["ranking"]
    ]
    return "\n".join(
        [
            "# SAEE Controlled Trial Observation Result v0.1",
            "",
            "Status: local observation recorded for the controlled trial demo payload.",
            "",
            "This result was generated from the public MVP service layer and the",
            "operator packet trial template. It does not record customer validation,",
            "production readiness, product launch, customer contact, external AI",
            "assistant testing, or private-core exposure.",
            "",
            "## Summary",
            "",
            f"- observation_scope: {result['observation_scope']}",
            f"- observation_status: {result['observation_status']}",
            f"- experiment_id: {demo['experiment_id']}",
            f"- status: {demo['status']}",
            f"- recommended_agent: {demo['recommended_agent']}",
            f"- confidence_score: {demo['confidence_score']:.4f}",
            f"- ranking_top: {demo['ranking_top']}",
            f"- agent_count: {demo['agent_count']}",
            f"- stored_run_count: {demo['stored_run_count']}",
            f"- failure_report_count: {demo['failure_report_count']}",
            f"- survival_curve_count: {demo['survival_curve_count']}",
            f"- blockers_closed_by_observation: {result['blockers_closed_by_observation']}",
            "- production_ready: false",
            "- customer_validated: false",
            "- customer_contacted: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Expected Output Fields",
            "",
            "| Field | Present |",
            "| --- | --- |",
            *field_rows,
            "",
            "## Ranking",
            "",
            "| Rank | Agent | Score |",
            "| --- | --- | --- |",
            *ranking_rows,
            "",
            "## Boundary",
            "",
            "- No runtime modified.",
            "- No backend modified.",
            "- No kernel modified.",
            "- No API schema modified.",
            "- No private core exposed.",
            "- No external service called.",
            "- No external AI assistant tested.",
            "- No customer contacted.",
            "- No customer data collected.",
            "- No product launched.",
            "- No customer validation claim made.",
            "- No production readiness claim made.",
            "",
        ]
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = build_result()
    write_json(INPUT_JSON, result["input"])
    write_json(RESULT_JSON, result)
    README_PATH.write_text(render_readme(), encoding="utf-8")
    RESULT_MD.write_text(render_markdown(result), encoding="utf-8")
    print(
        "SAEE_CONTROLLED_TRIAL_OBSERVATION_RUNNER: PASS "
        f"experiment_id={result['demo_output_summary']['experiment_id']} "
        f"recommended_agent={result['demo_output_summary']['recommended_agent']} "
        f"ranking_top={result['demo_output_summary']['ranking_top']} "
        "production_ready=false customer_validated=false "
        "customer_contacted=false private_core_exposed=false "
        "blockers_closed_by_observation=0"
    )


if __name__ == "__main__":
    main()
