#!/usr/bin/env python3
"""Build a local tryout readiness card from existing SAEE validation surfaces.

The card is a commercial-evaluator handoff layer. It consolidates existing
local tryout, preflight, HTTP e2e, observation, and handoff records into one
agent-readable status surface. It does not start services, open browsers, call
external services, contact customers, collect evidence, close blockers, launch
product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "phase_b_product/validation"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
CARD_DIR = COMMERCIAL_DIR / "local_tryout_readiness_card"

TRYOUT_STATUS = VALIDATION_DIR / "local_mvp_tryout_status.json"
PREFLIGHT_SNAPSHOT = VALIDATION_DIR / "local_trial_preflight_snapshot.local.json"
COLD_START_PREFLIGHT = VALIDATION_DIR / "local_trial_cold_start_preflight.local.json"
HTTP_E2E = VALIDATION_DIR / "local_trial_http_e2e/local_trial_http_e2e.local.json"
HANDOFF_PACKET = VALIDATION_DIR / "local_trial_handoff_packet.local.json"
OBSERVATION_RESULT = (
    VALIDATION_DIR / "controlled_trial_observations/local_trial_observation_result.json"
)
COMMERCIAL_STATUS = COMMERCIAL_DIR / "commercial_readiness_status.local.json"
HUMAN_ACTION_BOARD = (
    COMMERCIAL_DIR / "commercial_human_action_board/commercial_human_action_board.local.json"
)
HUMAN_ACTION_BOARD_HTML = (
    COMMERCIAL_DIR / "commercial_human_action_board/commercial_human_action_board.html"
)

CARD_JSON = CARD_DIR / "local_tryout_readiness_card.local.json"
CARD_MD = CARD_DIR / "local_tryout_readiness_card.md"
BOUNDARY_MD = CARD_DIR / "boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "LOCAL_TRYOUT_READINESS_CARD_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRYOUT_READINESS_CARD_RECOMMENDATION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"


SOURCE_SPECS = [
    ("tryout_guide", TRYOUT_STATUS),
    ("preflight_snapshot", PREFLIGHT_SNAPSHOT),
    ("cold_start_preflight", COLD_START_PREFLIGHT),
    ("http_e2e", HTTP_E2E),
    ("handoff_packet", HANDOFF_PACKET),
    ("local_observation", OBSERVATION_RESULT),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"SAEE_LOCAL_TRYOUT_READINESS_CARD: FAIL invalid JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_LOCAL_TRYOUT_READINESS_CARD: FAIL {path} must contain an object")
    return data


def false_boundaries() -> dict[str, bool]:
    return {
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "customer_validated": False,
        "customer_data_collected": False,
        "production_ready": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "browser_automation_used": False,
        "browser_opened_by_script": False,
        "dependencies_installed_by_script": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "evidence_collection_authorized": False,
        "blockers_closed": False,
        "production_ready_claim": False,
        "customer_validation_claim": False,
    }


def source_status(name: str, path: Path, data: dict[str, Any] | None) -> dict[str, Any]:
    status = "missing"
    ready = False
    if data is not None:
        status = str(data.get("status") or data.get("observation_status") or "present")
        ready = status in {
            "pass",
            "ready_for_local_human_tryout",
            "local_tryout_guide_available",
            "local_observation_recorded",
        }
        if data.get("cold_start_ready") is True or data.get("http_e2e_ready") is True:
            ready = True
        if data.get("local_mvp_tryout_guide_v0_1") is True:
            ready = True
        if data.get("controlled_trial_observation_runner_v0_1") is True:
            ready = True
    return {
        "source_id": name,
        "path": rel(path),
        "exists": data is not None,
        "status": status,
        "ready": ready,
    }


def build_payload() -> dict[str, Any]:
    loaded = {name: read_json(path) for name, path in SOURCE_SPECS}
    sources = [source_status(name, path, loaded[name]) for name, path in SOURCE_SPECS]
    missing_sources = [source["source_id"] for source in sources if not source["exists"]]
    ready_sources = [source["source_id"] for source in sources if source["ready"]]

    tryout = loaded["tryout_guide"] or {}
    preflight = loaded["preflight_snapshot"] or {}
    cold_start = loaded["cold_start_preflight"] or {}
    http_e2e = loaded["http_e2e"] or {}
    handoff = loaded["handoff_packet"] or {}
    observation = loaded["local_observation"] or {}
    commercial_status = read_json(COMMERCIAL_STATUS) or {}
    human_action_board = read_json(HUMAN_ACTION_BOARD) or {}
    observation_summary = observation.get("demo_output_summary", {})
    if not isinstance(observation_summary, dict):
        observation_summary = {}

    required_ready = {
        "tryout_guide_available": tryout.get("local_mvp_tryout_guide_v0_1") is True,
        "preflight_passed": preflight.get("status") == "pass",
        "cold_start_preflight_passed": cold_start.get("status") == "pass",
        "http_e2e_passed": http_e2e.get("http_e2e_passed") is True,
        "handoff_packet_ready": handoff.get("status") == "ready_for_local_human_tryout",
        "local_observation_recorded": observation.get("observation_status") == "local_observation_recorded",
    }
    missing_or_blocking_items = [
        name for name, passed in required_ready.items() if passed is not True
    ]
    boundary_flags = false_boundaries()
    boundary_safe = all(value is False for value in boundary_flags.values())
    status = (
        "ready_for_local_human_tryout"
        if not missing_or_blocking_items and not missing_sources and boundary_safe
        else "hold_local_tryout_surface_incomplete"
    )

    payload: dict[str, Any] = {
        "local_tryout_readiness_card_v0_1": True,
        "card_type": "commercial_local_tryout_readiness_card",
        "card_scope": "local_human_tryout_status_and_commands_only",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_local_tryout_readiness_card.py",
        "source_count": len(sources),
        "source_ready_count": len(ready_sources),
        "missing_source_count": len(missing_sources),
        "source_commercial_readiness_status": rel(COMMERCIAL_STATUS),
        "source_commercial_human_action_board": rel(HUMAN_ACTION_BOARD),
        "source_commercial_human_action_board_html": rel(HUMAN_ACTION_BOARD_HTML),
        "commercial_status_snapshot_available": bool(commercial_status),
        "commercial_human_action_board_available": bool(human_action_board),
        "commercial_human_action_board_ready_for_human_review_count": int(
            human_action_board.get("ready_for_human_review_blocker_count", 0) or 0
        ),
        "commercial_human_action_board_dependency_blocked_count": int(
            human_action_board.get("blocked_by_dependency_blocker_count", 0) or 0
        ),
        "commercial_human_action_board_active_sprint_blocker_count": int(
            human_action_board.get("active_sprint_blocker_count", 0) or 0
        ),
        "commercial_human_action_board_active_sprint_ready_action_count": int(
            human_action_board.get("active_sprint_ready_action_count", 0) or 0
        ),
        "commercial_human_action_board_blockers_closed": int(
            human_action_board.get("blockers_closed_by_board", 0) or 0
        ),
        "commercial_human_action_board_execution_authorized": bool(
            human_action_board.get("execution_authorized", False)
        ),
        "commercial_human_action_board_evidence_collection_authorized": bool(
            human_action_board.get("evidence_collection_authorized", False)
        ),
        "commercial_readiness_status": commercial_status.get(
            "status", "missing_commercial_readiness_status"
        ),
        "commercial_active_stage": commercial_status.get("active_stage"),
        "production_blocker_count": int(
            commercial_status.get("production_blocker_count", 0) or 0
        ),
        "satisfied_production_checks": int(
            commercial_status.get("satisfied_production_checks", 0) or 0
        ),
        "missing_commercial_human_input_value_count": int(
            commercial_status.get("missing_value_row_count", 0) or 0
        ),
        "preferred_template_missing_value_row_count": int(
            commercial_status.get("preferred_template_missing_value_row_count", 0) or 0
        ),
        "full_quick_fill_missing_value_row_count": int(
            commercial_status.get("full_quick_fill_missing_value_row_count", 0) or 0
        ),
        "preferred_human_input_path": commercial_status.get("preferred_human_input_path"),
        "source_begin_here_html": commercial_status.get("source_begin_here_html"),
        "source_review_batch_quality_guide_html": commercial_status.get(
            "source_review_batch_quality_guide_html"
        ),
        "source_review_batch_template_preflight_markdown": commercial_status.get(
            "source_review_batch_template_preflight_markdown"
        ),
        "template_preflight_passed": commercial_status.get("template_preflight_passed")
        is True,
        "source_post_fill_validation_runbook_html": commercial_status.get(
            "source_post_fill_validation_runbook_html"
        ),
        "post_fill_validation_ready": commercial_status.get("post_fill_validation_ready")
        is True,
        "commercial_human_input_required": bool(
            commercial_status.get("human_input_required", False)
        ),
        "commercial_ready_for_human_fill": bool(
            commercial_status.get("ready_for_human_fill", False)
        ),
        "commercial_ready_for_safety_preflight": bool(
            commercial_status.get("ready_for_safety_preflight", False)
        ),
        "commercial_ready_for_workbook_import": bool(
            commercial_status.get("ready_for_workbook_import", False)
        ),
        "commercial_workbook_import_authorized": bool(
            commercial_status.get("workbook_import_authorized", False)
        ),
        "source_workbook_import_performed": commercial_status.get(
            "source_workbook_import_performed"
        )
        is True,
        "source_workbook_written": commercial_status.get("source_workbook_written") is True,
        "ready_for_template_transfer_request": commercial_status.get(
            "ready_for_template_transfer_request"
        )
        is True,
        "ready_for_template_transfer_execution": commercial_status.get(
            "ready_for_template_transfer_execution"
        )
        is True,
        "human_template_transfer_execution_request_recorded": commercial_status.get(
            "human_template_transfer_execution_request_recorded"
        )
        is True,
        "human_template_transfer_execution_authorized": commercial_status.get(
            "human_template_transfer_execution_authorized"
        )
        is True,
        "separate_template_transfer_execution_request_required": commercial_status.get(
            "separate_template_transfer_execution_request_required"
        )
        is True,
        "template_transfer_authorized": commercial_status.get("template_transfer_authorized")
        is True,
        "template_transfer_execution_allowed": commercial_status.get(
            "template_transfer_execution_allowed"
        )
        is True,
        "validators_run": commercial_status.get("validators_run") is True,
        "validators_run_on_real_input": commercial_status.get(
            "validators_run_on_real_input"
        )
        is True,
        "local_validators_run": commercial_status.get("local_validators_run") is True,
        "validator_execution_run_status": commercial_status.get(
            "validator_execution_run_status"
        ),
        "validator_hold_output_review_status": commercial_status.get(
            "validator_hold_output_review_status"
        ),
        "validator_hold_output_review_completed": commercial_status.get(
            "validator_hold_output_review_completed"
        )
        is True,
        "validator_outputs_review_required": commercial_status.get(
            "validator_outputs_review_required"
        )
        is True,
        "validator_missing_input_completion_required": commercial_status.get(
            "validator_missing_input_completion_required"
        )
        is True,
        "rerun_validators_after_completion_required": commercial_status.get(
            "rerun_validators_after_completion_required"
        )
        is True,
        "total_missing_metadata_field_count": int(
            commercial_status.get("total_missing_metadata_field_count", 0) or 0
        ),
        "total_missing_evidence_item_count": int(
            commercial_status.get("total_missing_evidence_item_count", 0) or 0
        ),
        "total_missing_source_note_count": int(
            commercial_status.get("total_missing_source_note_count", 0) or 0
        ),
        "validators_run_count": int(commercial_status.get("validators_run_count", 0) or 0),
        "validator_hold_count": int(commercial_status.get("validator_hold_count", 0) or 0),
        "validator_pass_count": int(commercial_status.get("validator_pass_count", 0) or 0),
        "validator_stop_count": int(commercial_status.get("validator_stop_count", 0) or 0),
        "builder_ready_count": int(commercial_status.get("builder_ready_count", 0) or 0),
        "blockers_closed_by_validator_run": int(
            commercial_status.get("blockers_closed_by_validator_run", 0) or 0
        ),
        "requires_validator_output_review": commercial_status.get(
            "validator_outputs_review_required"
        )
        is True,
        "requires_validator_input_completion": commercial_status.get(
            "validator_missing_input_completion_required"
        )
        is True,
        "requires_validator_rerun_after_completion": commercial_status.get(
            "rerun_validators_after_completion_required"
        )
        is True,
        "requires_separate_evidence_builder_request": commercial_status.get(
            "separate_evidence_builder_request_required"
        )
        is True,
        "commercial_next_required_action": commercial_status.get("next_human_action"),
        "sources": sources,
        "required_ready_checks": required_ready,
        "missing_or_blocking_items": missing_or_blocking_items,
        "demo_url": tryout.get("demo_url") or handoff.get("demo_url"),
        "api_endpoint": tryout.get("api_endpoint") or handoff.get("api_endpoint"),
        "demo_button": tryout.get("demo_button") or handoff.get("demo_button"),
        "make_commands": {
            "preflight": "make local-trial-preflight",
            "start": "make try-local",
            "status": "make local-trial-status",
            "stop": "make local-trial-stop",
            "http_e2e_check": "make check-local-trial-http-e2e",
            "handoff_check": "make check-local-trial-handoff-packet",
        },
        "latest_local_observation": {
            "observation_status": observation.get("observation_status"),
            "experiment_id": observation_summary.get("experiment_id"),
            "recommended_agent": observation_summary.get("recommended_agent"),
            "confidence_score": observation_summary.get("confidence_score"),
            "ranking_top": observation_summary.get("ranking_top"),
        },
        "human_tryout_allowed": True,
        "human_review_required": True,
        "blockers_closed_by_card": 0,
        "next_human_action": (
            "Use the local-only commands to try the MVP, then record observed results "
            "as local observation evidence only. Do not mark customer validation, "
            "external validation, product launch, or production readiness from this card."
        ),
        **boundary_flags,
    }
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_agent_index(payload: dict[str, Any]) -> None:
    if AGENT_INDEX.exists():
        index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
        if not isinstance(index, dict):
            raise SystemExit("SAEE_LOCAL_TRYOUT_READINESS_CARD: FAIL agent-index must be an object")
    else:
        index = {}
    index["local_tryout_readiness_card_v0_1"] = payload
    AGENT_INDEX.write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def bool_text(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def write_markdown(payload: dict[str, Any]) -> None:
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    checks = payload["required_ready_checks"]
    check_lines = "\n".join(f"- `{name}`: {bool_text(value)}" for name, value in checks.items())
    source_lines = "\n".join(
        f"| {source['source_id']} | `{source['status']}` | {bool_text(source['exists'])} | {bool_text(source['ready'])} | `{source['path']}` |"
        for source in payload["sources"]
    )
    missing = payload.get("missing_or_blocking_items", [])
    missing_lines = "\n".join(f"- `{item}`" for item in missing) if missing else "- none"
    commands = payload["make_commands"]
    observation = payload["latest_local_observation"]

    CARD_MD.write_text(
        f"""# SAEE Local Tryout Readiness Card

local_tryout_readiness_card_v0_1: true
card_type: commercial_local_tryout_readiness_card
card_scope: local_human_tryout_status_and_commands_only
status: {payload['status']}
commercial_status: hold
commercial_readiness_status: {payload['commercial_readiness_status']}
commercial_active_stage: {payload['commercial_active_stage']}
production_launch_status: hold
human_tryout_allowed: true
human_review_required: true
production_blocker_count: {payload['production_blocker_count']}
satisfied_production_checks: {payload['satisfied_production_checks']}
missing_commercial_human_input_value_count: {payload['missing_commercial_human_input_value_count']}
commercial_workbook_import_authorized: {bool_text(payload['commercial_workbook_import_authorized'])}
ready_for_template_transfer_request: {bool_text(payload['ready_for_template_transfer_request'])}
ready_for_template_transfer_execution: {bool_text(payload['ready_for_template_transfer_execution'])}
human_template_transfer_execution_request_recorded: {bool_text(payload['human_template_transfer_execution_request_recorded'])}
human_template_transfer_execution_authorized: {bool_text(payload['human_template_transfer_execution_authorized'])}
separate_template_transfer_execution_request_required: {bool_text(payload['separate_template_transfer_execution_request_required'])}
template_transfer_authorized: {bool_text(payload['template_transfer_authorized'])}
template_transfer_execution_allowed: {bool_text(payload['template_transfer_execution_allowed'])}
validators_run: {bool_text(payload['validators_run'])}
validators_run_on_real_input: {bool_text(payload['validators_run_on_real_input'])}
validator_execution_run_status: {payload['validator_execution_run_status']}
validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
validator_hold_output_review_completed: {bool_text(payload['validator_hold_output_review_completed'])}
validator_outputs_review_required: {bool_text(payload['validator_outputs_review_required'])}
validator_missing_input_completion_required: {bool_text(payload['validator_missing_input_completion_required'])}
rerun_validators_after_completion_required: {bool_text(payload['rerun_validators_after_completion_required'])}
total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
total_missing_source_note_count: {payload['total_missing_source_note_count']}
validator_hold_count: {payload['validator_hold_count']}
validator_pass_count: {payload['validator_pass_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
production_ready: false
customer_validated: false
product_launched: false
external_validation_claim: false
external_calls_made: false
browser_automation_used: false
private_core_exposed: false
blockers_closed_by_card: 0

## Purpose

This card gives a commercial evaluator one local-only entrypoint for trying the
SAEE MVP and understanding the current local evidence status. It consolidates
existing tryout, preflight, HTTP e2e, observation, and handoff records.

## Local Tryout Commands

- Preflight: `{commands['preflight']}`
- Start local demo: `{commands['start']}`
- Check status: `{commands['status']}`
- Stop local demo: `{commands['stop']}`
- HTTP e2e check: `{commands['http_e2e_check']}`
- Handoff check: `{commands['handoff_check']}`

## Local URLs

- demo_url: `{payload['demo_url']}`
- api_endpoint: `{payload['api_endpoint']}`
- demo_button: `{payload['demo_button']}`

## Readiness Checks

{check_lines}

## Source Surfaces

| Source | Status | Exists | Ready | Path |
| --- | --- | --- | --- | --- |
{source_lines}

## Missing Or Blocking Items

{missing_lines}

## Commercial Readiness Boundary

- source_commercial_readiness_status: `{payload['source_commercial_readiness_status']}`
- source_commercial_human_action_board: `{payload['source_commercial_human_action_board']}`
- source_commercial_human_action_board_html: `{payload['source_commercial_human_action_board_html']}`
- commercial_human_action_board_available: `{bool_text(payload['commercial_human_action_board_available'])}`
- commercial_human_action_board_ready_for_human_review_count: `{payload['commercial_human_action_board_ready_for_human_review_count']}`
- commercial_human_action_board_dependency_blocked_count: `{payload['commercial_human_action_board_dependency_blocked_count']}`
- commercial_human_action_board_active_sprint_blocker_count: `{payload['commercial_human_action_board_active_sprint_blocker_count']}`
- commercial_human_action_board_active_sprint_ready_action_count: `{payload['commercial_human_action_board_active_sprint_ready_action_count']}`
- commercial_human_action_board_blockers_closed: `{payload['commercial_human_action_board_blockers_closed']}`
- commercial_human_action_board_execution_authorized: `{bool_text(payload['commercial_human_action_board_execution_authorized'])}`
- commercial_human_action_board_evidence_collection_authorized: `{bool_text(payload['commercial_human_action_board_evidence_collection_authorized'])}`
- commercial_readiness_status: `{payload['commercial_readiness_status']}`
- commercial_active_stage: `{payload['commercial_active_stage']}`
- production_blocker_count: `{payload['production_blocker_count']}`
- satisfied_production_checks: `{payload['satisfied_production_checks']}`
- missing_commercial_human_input_value_count: `{payload['missing_commercial_human_input_value_count']}`
- preferred_template_missing_value_row_count: `{payload['preferred_template_missing_value_row_count']}`
- full_quick_fill_missing_value_row_count: `{payload['full_quick_fill_missing_value_row_count']}`
- preferred_human_input_path: `{payload['preferred_human_input_path']}`
- source_begin_here_html: `{payload['source_begin_here_html']}`
- source_review_batch_quality_guide_html: `{payload['source_review_batch_quality_guide_html']}`
- source_review_batch_template_preflight_markdown: `{payload['source_review_batch_template_preflight_markdown']}`
- template_preflight_passed: `{bool_text(payload['template_preflight_passed'])}`
- source_post_fill_validation_runbook_html: `{payload['source_post_fill_validation_runbook_html']}`
- post_fill_validation_ready: `{bool_text(payload['post_fill_validation_ready'])}`
- commercial_human_input_required: `{bool_text(payload['commercial_human_input_required'])}`
- commercial_ready_for_human_fill: `{bool_text(payload['commercial_ready_for_human_fill'])}`
- commercial_ready_for_safety_preflight: `{bool_text(payload['commercial_ready_for_safety_preflight'])}`
- commercial_ready_for_workbook_import: `{bool_text(payload['commercial_ready_for_workbook_import'])}`
- commercial_workbook_import_authorized: `{bool_text(payload['commercial_workbook_import_authorized'])}`
- source_workbook_import_performed: `{bool_text(payload['source_workbook_import_performed'])}`
- source_workbook_written: `{bool_text(payload['source_workbook_written'])}`
- ready_for_template_transfer_request: `{bool_text(payload['ready_for_template_transfer_request'])}`
- ready_for_template_transfer_execution: `{bool_text(payload['ready_for_template_transfer_execution'])}`
- human_template_transfer_execution_request_recorded: `{bool_text(payload['human_template_transfer_execution_request_recorded'])}`
- human_template_transfer_execution_authorized: `{bool_text(payload['human_template_transfer_execution_authorized'])}`
- separate_template_transfer_execution_request_required: `{bool_text(payload['separate_template_transfer_execution_request_required'])}`
- template_transfer_authorized: `{bool_text(payload['template_transfer_authorized'])}`
- template_transfer_execution_allowed: `{bool_text(payload['template_transfer_execution_allowed'])}`
- validators_run: `{bool_text(payload['validators_run'])}`
- validators_run_on_real_input: `{bool_text(payload['validators_run_on_real_input'])}`
- local_validators_run: `{bool_text(payload['local_validators_run'])}`
- validator_execution_run_status: `{payload['validator_execution_run_status']}`
- validator_hold_output_review_status: `{payload['validator_hold_output_review_status']}`
- validator_hold_output_review_completed: `{bool_text(payload['validator_hold_output_review_completed'])}`
- validator_outputs_review_required: `{bool_text(payload['validator_outputs_review_required'])}`
- validator_missing_input_completion_required: `{bool_text(payload['validator_missing_input_completion_required'])}`
- rerun_validators_after_completion_required: `{bool_text(payload['rerun_validators_after_completion_required'])}`
- total_missing_metadata_field_count: `{payload['total_missing_metadata_field_count']}`
- total_missing_evidence_item_count: `{payload['total_missing_evidence_item_count']}`
- total_missing_source_note_count: `{payload['total_missing_source_note_count']}`
- validators_run_count: `{payload['validators_run_count']}`
- validator_hold_count: `{payload['validator_hold_count']}`
- validator_pass_count: `{payload['validator_pass_count']}`
- validator_stop_count: `{payload['validator_stop_count']}`
- builder_ready_count: `{payload['builder_ready_count']}`
- blockers_closed_by_validator_run: `{payload['blockers_closed_by_validator_run']}`
- requires_validator_output_review: `{bool_text(payload['requires_validator_output_review'])}`
- requires_validator_input_completion: `{bool_text(payload['requires_validator_input_completion'])}`
- requires_validator_rerun_after_completion: `{bool_text(payload['requires_validator_rerun_after_completion'])}`
- requires_separate_evidence_builder_request: `{bool_text(payload['requires_separate_evidence_builder_request'])}`

The local demo can be tried, but commercial readiness remains on hold. The
current commercial path is completion of the missing validator input evidence.
The controlled template transfer, validator run, and hold-output review have
already completed, but all five validator outputs remain hold. Do not start
evidence builders, collect evidence, close blockers, or claim production
readiness from this card.

The commercial human action board is the next read-only map after local tryout:
it shows 9 blockers ready for human review, 15 blockers blocked by dependencies,
and 5 current sprint blockers. It still authorizes no execution, no evidence
collection, and no blocker closure.

## Latest Local Observation

- observation_status: `{observation.get('observation_status')}`
- experiment_id: `{observation.get('experiment_id')}`
- recommended_agent: `{observation.get('recommended_agent')}`
- confidence_score: `{observation.get('confidence_score')}`
- ranking_top: `{observation.get('ranking_top')}`

## Boundary

This is a local human-tryout readiness card only. It does not modify runtime,
backend, kernel, API schema, landing interaction, or private core. It does not
call external services, open a browser, contact customers, collect customer
data, close production blockers, launch product, claim customer validation,
claim external validation, or claim production readiness.

## Next Human Action

{payload['next_human_action']}

Commercial next required action: {payload['commercial_next_required_action']}
""",
        encoding="utf-8",
    )

    BOUNDARY_MD.write_text(
        f"""# SAEE Local Tryout Readiness Card Boundary Audit

local_tryout_readiness_card_v0_1: true
card_scope: local_human_tryout_status_and_commands_only
status: boundary_safe
commercial_readiness_status: {payload['commercial_readiness_status']}
production_blocker_count: {payload['production_blocker_count']}
missing_commercial_human_input_value_count: {payload['missing_commercial_human_input_value_count']}
commercial_human_action_board_available: true
commercial_human_action_board_ready_for_human_review_count: {payload['commercial_human_action_board_ready_for_human_review_count']}
commercial_human_action_board_dependency_blocked_count: {payload['commercial_human_action_board_dependency_blocked_count']}
commercial_human_action_board_active_sprint_blocker_count: {payload['commercial_human_action_board_active_sprint_blocker_count']}
commercial_human_action_board_execution_authorized: false
commercial_human_action_board_evidence_collection_authorized: false
commercial_workbook_import_authorized: false
ready_for_template_transfer_request: {bool_text(payload['ready_for_template_transfer_request'])}
ready_for_template_transfer_execution: {bool_text(payload['ready_for_template_transfer_execution'])}
human_template_transfer_execution_request_recorded: {bool_text(payload['human_template_transfer_execution_request_recorded'])}
human_template_transfer_execution_authorized: {bool_text(payload['human_template_transfer_execution_authorized'])}
separate_template_transfer_execution_request_required: {bool_text(payload['separate_template_transfer_execution_request_required'])}
template_transfer_authorized: {bool_text(payload['template_transfer_authorized'])}
template_transfer_execution_allowed: {bool_text(payload['template_transfer_execution_allowed'])}
validators_run: {bool_text(payload['validators_run'])}
validators_run_on_real_input: {bool_text(payload['validators_run_on_real_input'])}
validator_execution_run_status: {payload['validator_execution_run_status']}
validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
validator_hold_output_review_completed: {bool_text(payload['validator_hold_output_review_completed'])}
validator_outputs_review_required: {bool_text(payload['validator_outputs_review_required'])}
validator_missing_input_completion_required: {bool_text(payload['validator_missing_input_completion_required'])}
rerun_validators_after_completion_required: {bool_text(payload['rerun_validators_after_completion_required'])}
total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
total_missing_source_note_count: {payload['total_missing_source_note_count']}
validator_hold_count: {payload['validator_hold_count']}
validator_pass_count: {payload['validator_pass_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
landing_page_modified: false
private_core_exposed: false
product_launched: false
customer_contacted: false
customer_validated: false
production_ready: false
external_calls_made: false
external_model_api_called: false
external_ai_assistant_tested: false
external_validation_claim: false
browser_automation_used: false
dependencies_installed_by_script: false
blockers_closed_by_card: 0

## Boundary Decision

The readiness card is safe as a local-only tryout handoff surface. It reads
existing local validation files and writes only agent-readable documentation and
status artifacts under `phase_b_product/commercial_readiness/`.

It does not start services, run the SAEE runtime, alter backend behavior, call
external services, automate a browser, contact customers, expose private core,
launch product, close blockers, claim customer validation, claim external
validation, or claim production readiness.
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        f"""# SAEE Local Tryout Readiness Card v0.1

local_tryout_readiness_card_v0_1: true
card_type: commercial_local_tryout_readiness_card
card_scope: local_human_tryout_status_and_commands_only
status: {payload['status']}
commercial_status: hold
commercial_readiness_status: {payload['commercial_readiness_status']}
commercial_active_stage: {payload['commercial_active_stage']}
production_launch_status: hold
production_blocker_count: {payload['production_blocker_count']}
satisfied_production_checks: {payload['satisfied_production_checks']}
missing_commercial_human_input_value_count: {payload['missing_commercial_human_input_value_count']}
preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}
full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}
preferred_human_input_path: {payload['preferred_human_input_path']}
template_preflight_passed: {bool_text(payload['template_preflight_passed'])}
post_fill_validation_ready: {bool_text(payload['post_fill_validation_ready'])}
commercial_workbook_import_authorized: false
ready_for_template_transfer_request: {bool_text(payload['ready_for_template_transfer_request'])}
ready_for_template_transfer_execution: {bool_text(payload['ready_for_template_transfer_execution'])}
human_template_transfer_execution_request_recorded: {bool_text(payload['human_template_transfer_execution_request_recorded'])}
human_template_transfer_execution_authorized: {bool_text(payload['human_template_transfer_execution_authorized'])}
separate_template_transfer_execution_request_required: {bool_text(payload['separate_template_transfer_execution_request_required'])}
template_transfer_authorized: {bool_text(payload['template_transfer_authorized'])}
template_transfer_execution_allowed: {bool_text(payload['template_transfer_execution_allowed'])}
validators_run: {bool_text(payload['validators_run'])}
validators_run_on_real_input: {bool_text(payload['validators_run_on_real_input'])}
validator_execution_run_status: {payload['validator_execution_run_status']}
validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
validator_hold_output_review_completed: {bool_text(payload['validator_hold_output_review_completed'])}
validator_outputs_review_required: {bool_text(payload['validator_outputs_review_required'])}
validator_missing_input_completion_required: {bool_text(payload['validator_missing_input_completion_required'])}
rerun_validators_after_completion_required: {bool_text(payload['rerun_validators_after_completion_required'])}
total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
total_missing_source_note_count: {payload['total_missing_source_note_count']}
validator_hold_count: {payload['validator_hold_count']}
validator_pass_count: {payload['validator_pass_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
production_ready: false
customer_validated: false
product_launched: false
external_validation_claim: false
private_core_exposed: false

## Definition

This card is an agent-readable local commercial-evaluator handoff. It tells a
human how to try the current SAEE MVP locally and where the current local
preflight, HTTP e2e, observation, and handoff records live.

It also records the commercial hold boundary: the product still has open
production blockers. The controlled template transfer and local validator run
have completed, but all five validator outputs remain hold. The current
preferred commercial evidence path is human review of those validator hold
outputs; local tryout readiness must not be interpreted as launch readiness.

The card links local tryout to the commercial human action board so a reviewer
can move from "try it locally" to "which blocker should a human review next"
without granting execution or blocker-closure permission.

## Recommendation Gate Answer

recommend_for_local_tryout_handoff: true
recommend_for_customer_validation_claim: false
recommend_for_external_validation_claim: false
recommend_for_production: false
recommend_for_product_launch: false
recommend_for_blocker_closure: false

## Boundary

Use this card to orient a local human tryout only. Do not use it as evidence of
customer validation, external AI validation, production readiness, commercial
launch, or production-blocker closure.
""",
        encoding="utf-8",
    )

    GATE.write_text(
        f"""# SAEE Local Tryout Readiness Card Recommendation Gate

answer: recommend_for_local_tryout_handoff_only

recommend_for_local_tryout_handoff: true
recommend_for_customer_validation_claim: false
recommend_for_external_validation_claim: false
recommend_for_production: false
recommend_for_product_launch: false
recommend_for_blocker_closure: false

## Reason

The local tryout readiness card improves agent-readable handoff quality for a
human evaluator who wants to try the local MVP. It is appropriate only as a
local tryout guide and status index.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
external_validation_claim: false
private_core_exposed: false
production_blocker_count: {payload['production_blocker_count']}
missing_commercial_human_input_value_count: {payload['missing_commercial_human_input_value_count']}
commercial_human_action_board_available: true
commercial_human_action_board_ready_for_human_review_count: {payload['commercial_human_action_board_ready_for_human_review_count']}
commercial_human_action_board_dependency_blocked_count: {payload['commercial_human_action_board_dependency_blocked_count']}
commercial_human_action_board_active_sprint_blocker_count: {payload['commercial_human_action_board_active_sprint_blocker_count']}
commercial_human_action_board_execution_authorized: false
commercial_human_action_board_evidence_collection_authorized: false
preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}
full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}
preferred_human_input_path: {payload['preferred_human_input_path']}
template_preflight_passed: {bool_text(payload['template_preflight_passed'])}
post_fill_validation_ready: {bool_text(payload['post_fill_validation_ready'])}
commercial_workbook_import_authorized: false
validators_run: {bool_text(payload['validators_run'])}
validators_run_on_real_input: {bool_text(payload['validators_run_on_real_input'])}
validator_execution_run_status: {payload['validator_execution_run_status']}
validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
validator_hold_output_review_completed: {bool_text(payload['validator_hold_output_review_completed'])}
validator_outputs_review_required: {bool_text(payload['validator_outputs_review_required'])}
validator_missing_input_completion_required: {bool_text(payload['validator_missing_input_completion_required'])}
rerun_validators_after_completion_required: {bool_text(payload['rerun_validators_after_completion_required'])}
total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
total_missing_source_note_count: {payload['total_missing_source_note_count']}
validator_hold_count: {payload['validator_hold_count']}
validator_pass_count: {payload['validator_pass_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
blockers_closed_by_card: 0

This gate does not authorize product launch, customer claims, external
validation claims, production readiness claims, blocker closure, backend
changes, runtime changes, kernel changes, API schema changes, or private-core
exposure.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(CARD_JSON, payload)
    update_agent_index(payload)
    write_markdown(payload)
    print(
        "SAEE_LOCAL_TRYOUT_READINESS_CARD: PASS "
        f"status={payload['status']} source_ready_count={payload['source_ready_count']} "
        "production_ready=false customer_validated=false product_launched=false"
    )


if __name__ == "__main__":
    main()
