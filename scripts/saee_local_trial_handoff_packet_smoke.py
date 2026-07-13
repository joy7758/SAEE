#!/usr/bin/env python3
"""Smoke check for the SAEE local trial handoff packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RUNNER = ROOT / "scripts/saee_local_trial_handoff_packet.py"
OUTPUT_JSON = ROOT / "phase_b_product/validation/local_trial_handoff_packet.local.json"
OUTPUT_MD = ROOT / "phase_b_product/validation/local_trial_handoff_packet.md"
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_HANDOFF_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_HANDOFF_PACKET_RECOMMENDATION_GATE.md"

PASS_PREFIX = "SAEE_LOCAL_TRIAL_HANDOFF_PACKET_SMOKE: PASS"
FAIL_PREFIX = "SAEE_LOCAL_TRIAL_HANDOFF_PACKET_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def main() -> int:
    require(RUNNER.is_file(), "runner missing")
    subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    for path in [OUTPUT_JSON, OUTPUT_MD, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    packet = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "local_trial_handoff_packet_v0_1": True,
        "packet_type": "saee_local_trial_handoff_packet",
        "packet_version": "v0.1",
        "handoff_scope": "local_mvp_tryout_to_human_observation_recording",
        "tryout_guide_available": True,
        "human_execution_required": True,
        "human_observation_recording_required": True,
        "blockers_closed_by_handoff": 0,
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
    for key, value in expected.items():
        require(packet.get(key) == value, f"{key} must be {value}")
    require(
        packet.get("status") in {"ready_for_local_human_tryout", "hold_local_setup_required"},
        "status must be a bounded local handoff status",
    )
    require(packet.get("demo_url") == "http://127.0.0.1:8765/", "demo URL mismatch")
    require(
        packet.get("api_endpoint") == "http://127.0.0.1:8000/experiment/run",
        "API endpoint mismatch",
    )
    fields = packet.get("expected_result_fields_present", {})
    require(isinstance(fields, dict), "expected_result_fields_present must be object")
    for key in ["decision_result", "recommended_agent", "confidence_score", "ranking", "failure_modes_summary"]:
        require(fields.get(key) is True, f"expected output field missing: {key}")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE]
    )
    for token in [
        "local_trial_handoff_packet_v0_1: true",
        "packet_type: saee_local_trial_handoff_packet",
        "human_execution_required: true",
        "production_ready: false",
        "customer_validated: false",
        "customer_contacted: false",
        "product_launched: false",
        "external_calls_made: false",
        "browser_opened_by_script: false",
        "private_core_exposed: false",
        "blockers_closed_by_handoff: 0",
        "answer: recommend_for_local_tryout_handoff_only",
        "recommend_for_local_tryout_handoff: true",
        "recommend_for_customer_validation_claim: false",
        "recommend_for_production: false",
        "recommend_for_product_launch: false",
        "recommend_for_blocker_closure: false",
    ]:
        require(token in combined, "missing doc/gate token " + token)
    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "external_calls_made: true",
        '"external_calls_made": true',
        "browser_opened_by_script: true",
        '"browser_opened_by_script": true',
        "recommend_for_customer_validation_claim: true",
        "recommend_for_production: true",
        "recommend_for_product_launch: true",
        "recommend_for_blocker_closure: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/validation/LOCAL_TRIAL_HANDOFF_PACKET_V0_1.md",
        "/phase_b_product/validation/local_trial_handoff_packet.local.json",
        "/phase_b_product/validation/local_trial_handoff_packet.md",
        "/docs/strategy/SAEE_LOCAL_TRIAL_HANDOFF_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_local_trial_handoff_packet.py",
        "/scripts/saee_local_trial_handoff_packet_smoke.py",
    ]:
        require(token in llms, "llms.txt missing " + token)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("local_trial_handoff_packet_v0_1", {})
    for key, value in {
        "local_trial_handoff_packet_v0_1": True,
        "status": packet.get("status"),
        "packet_type": "saee_local_trial_handoff_packet",
        "handoff_scope": "local_mvp_tryout_to_human_observation_recording",
        "tryout_guide_available": True,
        "human_execution_required": True,
        "human_observation_recording_required": True,
        "blockers_closed_by_handoff": 0,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "product_launched": False,
        "external_calls_made": False,
        "browser_opened_by_script": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        PASS_PREFIX
        + f" status={packet['status']}"
        + f" preflight_ready_to_start={str(packet['preflight_ready_to_start']).lower()}"
        + " blockers_closed_by_handoff=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
