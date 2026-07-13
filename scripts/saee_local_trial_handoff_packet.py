#!/usr/bin/env python3
"""Generate a local SAEE trial handoff packet.

This packet consolidates the local tryout guide, current preflight snapshot,
and local observation result into one human-readable handoff surface. It does
not start services, open a browser, call external services, contact customers,
collect customer data, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "phase_b_product/validation"
TRYOUT_STATUS = VALIDATION_DIR / "local_mvp_tryout_status.json"
PREFLIGHT_SNAPSHOT = VALIDATION_DIR / "local_trial_preflight_snapshot.local.json"
OBSERVATION_RESULT = (
    VALIDATION_DIR / "controlled_trial_observations/local_trial_observation_result.json"
)
OUTPUT_JSON = VALIDATION_DIR / "local_trial_handoff_packet.local.json"
OUTPUT_MD = VALIDATION_DIR / "local_trial_handoff_packet.md"
TOP_DOC = VALIDATION_DIR / "LOCAL_TRIAL_HANDOFF_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_HANDOFF_PACKET_RECOMMENDATION_GATE.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"SAEE_LOCAL_TRIAL_HANDOFF_PACKET: FAIL invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"SAEE_LOCAL_TRIAL_HANDOFF_PACKET: FAIL {path} must contain an object")
    return value


def false_boundaries() -> dict[str, bool]:
    return {
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_data_allowed": False,
        "customer_data_collected": False,
        "paid_trial_enabled": False,
        "payment_provider_configured": False,
        "product_launched": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "external_calls_made": False,
        "browser_opened_by_script": False,
        "dependencies_installed_by_script": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
    }


def build_packet() -> dict[str, Any]:
    tryout = read_json(TRYOUT_STATUS)
    preflight = read_json(PREFLIGHT_SNAPSHOT)
    observation = read_json(OBSERVATION_RESULT)
    preflight_ready = preflight.get("ready_to_start") is True
    tryout_ready = tryout.get("local_mvp_tryout_guide_v0_1") is True
    observation_ready = observation.get("controlled_trial_observation_runner_v0_1") is True
    status = "ready_for_local_human_tryout" if preflight_ready and tryout_ready else "hold_local_setup_required"
    result = observation.get("demo_output_summary", {})
    if not isinstance(result, dict):
        result = {}
    expected_fields = result.get("expected_fields_present", {})
    if not isinstance(expected_fields, dict):
        expected_fields = {}
    return {
        "local_trial_handoff_packet_v0_1": True,
        "packet_type": "saee_local_trial_handoff_packet",
        "packet_version": "v0.1",
        "status": status,
        "handoff_scope": "local_mvp_tryout_to_human_observation_recording",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_local_trial_handoff_packet.py",
        "source_files": {
            "tryout_status": rel(TRYOUT_STATUS),
            "preflight_snapshot": rel(PREFLIGHT_SNAPSHOT),
            "observation_result": rel(OBSERVATION_RESULT),
        },
        "demo_url": tryout.get("demo_url"),
        "api_endpoint": tryout.get("api_endpoint"),
        "demo_button": tryout.get("demo_button"),
        "tryout_guide_available": tryout_ready,
        "preflight_status": preflight.get("status"),
        "preflight_ready_to_start": preflight_ready,
        "backend_port": preflight.get("backend_port"),
        "landing_port": preflight.get("landing_port"),
        "backend_owned_by_saee": preflight.get("backend_owned_by_saee") is True,
        "landing_owned_by_saee": preflight.get("landing_owned_by_saee") is True,
        "missing_or_blocking_items": preflight.get("missing_or_blocking_items", []),
        "local_observation_available": observation_ready,
        "local_observation_status": observation.get("observation_status"),
        "observed_experiment_id": result.get("experiment_id"),
        "observed_recommended_agent": result.get("recommended_agent"),
        "observed_confidence_score": result.get("confidence_score"),
        "observed_ranking_top": result.get("ranking_top"),
        "expected_result_fields_present": expected_fields,
        "human_execution_required": True,
        "human_observation_recording_required": True,
        "blockers_closed_by_handoff": 0,
        "next_human_action": (
            "Open the local demo URL, click Run Demo Battle, and record the observed "
            "result in the controlled trial observation sheet. Do not mark customer "
            "validation or production readiness from this local handoff."
        ),
        **false_boundaries(),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_report(payload: dict[str, Any]) -> None:
    missing = payload.get("missing_or_blocking_items", [])
    missing_lines = "\n".join(f"- {item}" for item in missing) if missing else "- none"
    fields = payload.get("expected_result_fields_present", {})
    if not isinstance(fields, dict):
        fields = {}
    field_lines = "\n".join(f"- `{k}`: {bool_text(v)}" for k, v in sorted(fields.items()))
    OUTPUT_MD.write_text(
        f"""# SAEE Local Trial Handoff Packet

local_trial_handoff_packet_v0_1: true
packet_type: saee_local_trial_handoff_packet
status: {payload['status']}
handoff_scope: {payload['handoff_scope']}
preflight_ready_to_start: {bool_text(payload['preflight_ready_to_start'])}
local_observation_available: {bool_text(payload['local_observation_available'])}
human_execution_required: true
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_handoff: 0

## Purpose

This packet gives a human reviewer one current local handoff surface for trying
the SAEE MVP demo and recording what was observed. It consolidates the local
tryout guide, current preflight snapshot, and latest local observation result.

## Try It Locally

1. Open `{payload['demo_url']}`.
2. Click `{payload['demo_button']}`.
3. Confirm the page shows `recommended_agent`, `confidence_score`, `ranking`,
   and `failure_modes_summary`.
4. Record the result in
   `phase_b_product/validation/controlled_trial_operator_packet/local_trial_observation_sheet.md`.

## Current Local Readiness

- preflight_status: {payload['preflight_status']}
- preflight_ready_to_start: {bool_text(payload['preflight_ready_to_start'])}
- backend_port: {payload['backend_port']}
- landing_port: {payload['landing_port']}
- backend_owned_by_saee: {bool_text(payload['backend_owned_by_saee'])}
- landing_owned_by_saee: {bool_text(payload['landing_owned_by_saee'])}

## Missing Or Blocking Items

{missing_lines}

## Latest Local Observation

- local_observation_status: {payload['local_observation_status']}
- observed_experiment_id: {payload['observed_experiment_id']}
- observed_recommended_agent: {payload['observed_recommended_agent']}
- observed_confidence_score: {payload['observed_confidence_score']}
- observed_ranking_top: {payload['observed_ranking_top']}

## Expected Result Fields

{field_lines}

## Boundary

This handoff packet does not start servers, open a browser, call external
services, contact customers, collect customer data, collect production evidence,
modify backend behavior, modify runtime/kernel/API schema, expose private core,
launch product, close production blockers, claim customer validation, or claim
production readiness.

## Next Human Action

{payload['next_human_action']}
""",
        encoding="utf-8",
    )


def write_top_doc() -> None:
    TOP_DOC.write_text(
        """# SAEE Local Trial Handoff Packet v0.1

local_trial_handoff_packet_v0_1: true
packet_scope: local_mvp_tryout_to_human_observation_recording
production_ready: false
customer_validated: false
customer_contacted: false
customer_data_allowed: false
product_launched: false
public_sdk_released: false
external_calls_made: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_handoff: 0

## Purpose

This packet consolidates the existing local MVP tryout guide, current local
trial preflight snapshot, and latest controlled trial observation result into a
single human handoff surface.

It is intended to reduce trial friction for reviewers while preserving the
commercial boundary: local tryout is not customer validation and not production
readiness.

## Generated Outputs

- `phase_b_product/validation/local_trial_handoff_packet.local.json`
- `phase_b_product/validation/local_trial_handoff_packet.md`

## Boundary

This packet does not install dependencies, start services, open a browser, call
external services, contact customers, collect customer data, execute production
evidence collection, close blockers, launch product, modify runtime, backend
logic, kernel, API schema, or private core, or claim production readiness.
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE.write_text(
        """# SAEE Local Trial Handoff Packet Recommendation Gate

answer: recommend_for_local_tryout_handoff_only

recommend_for_local_tryout_handoff: true
recommend_for_customer_validation_claim: false
recommend_for_production: false
recommend_for_product_launch: false
recommend_for_blocker_closure: false

## Reason

If a reviewer asks how to try SAEE locally, this packet is useful because it
combines the current local tryout URL, preflight state, and latest local demo
observation into one handoff record. It improves commercial validation
workflow clarity without claiming external/customer validation.

## Boundary

- production_ready: false
- customer_validated: false
- customer_contacted: false
- product_launched: false
- external_calls_made: false
- browser_opened_by_script: false
- private_core_exposed: false
- blockers_closed_by_handoff: 0
""",
        encoding="utf-8",
    )


def run() -> dict[str, Any]:
    packet = build_packet()
    write_json(OUTPUT_JSON, packet)
    write_report(packet)
    write_top_doc()
    write_gate()
    print(
        "SAEE_LOCAL_TRIAL_HANDOFF_PACKET: PASS "
        f"status={packet['status']} "
        f"preflight_ready_to_start={bool_text(packet['preflight_ready_to_start'])} "
        f"local_observation_available={bool_text(packet['local_observation_available'])} "
        "blockers_closed_by_handoff=0 production_ready=false"
    )
    return packet


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
