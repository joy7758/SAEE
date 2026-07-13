#!/usr/bin/env python3
"""Smoke check for the commercial-readiness begin-here entrypoint."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_readiness_begin_here.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_begin_here"
OUT_JSON = OUT_DIR / "commercial_readiness_begin_here.local.json"
OUT_MD = OUT_DIR / "commercial_readiness_begin_here.md"
OUT_HTML = OUT_DIR / "commercial_readiness_begin_here.html"
OUT_AUDIT = OUT_DIR / "commercial_readiness_begin_here_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_READINESS_BEGIN_HERE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_BEGIN_HERE_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_READINESS_BEGIN_HERE_SMOKE: FAIL " + message)


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    for path in [OUT_MD, OUT_HTML, OUT_AUDIT, TOP_DOC, GATE]:
        require(path.exists(), f"{path.relative_to(ROOT)} missing")

    expected = {
        "commercial_readiness_begin_here_v0_1": True,
        "status": "ready_for_separate_evidence_builder_request",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "first_action_id": "NEXT-EBR-001",
        "first_sequence_step_id": "EBR-001",
        "first_blocker_id": "separate_evidence_builder_request",
        "primary_human_input_lane": "commercial_sprint_evidence_builder_request_review",
        "preferred_human_input_path": "separate_evidence_builder_request",
        "template_transfer_performed": True,
        "template_transfer_execution_allowed": False,
        "template_transfer_applier_execution_allowed": False,
        "ready_for_validator_approval": False,
        "ready_for_validator_execution": False,
        "planned_validator_count": 5,
        "ready_validator_count": 5,
        "validator_execution_run_status": "completed_all_validators_passed",
        "validator_hold_output_review_completed": False,
        "validator_missing_input_completion_required": False,
        "rerun_validators_after_completion_required": False,
        "total_missing_metadata_field_count": 0,
        "total_missing_evidence_item_count": 0,
        "total_missing_source_note_count": 0,
        "validator_hold_count": 0,
        "validator_pass_count": 5,
        "builder_ready_count": 5,
        "approved_validator_count": 0,
        "validator_execution_authorized_count": 0,
        "validators_run": True,
        "requires_validator_approval_review": False,
        "requires_separate_validator_execution_request": False,
        "begin_here_action_count": 4,
        "blockers_closed_by_begin_here": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "validators_run_on_real_input": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    actions = payload.get("actions")
    require(isinstance(actions, list) and len(actions) == 4, "must contain four actions")
    require(actions[0].get("step_id") == "BEGIN-EBR-001", "first action must be evidence builder request review")
    require(all(action.get("codex_execution_allowed") is False for action in actions), "actions must not authorize Codex execution")

    machine_lines = "\n".join(
        f"{key}: {str(value).lower() if isinstance(value, bool) else value}"
        for key, value in payload.items()
        if isinstance(value, (str, int, bool))
    )
    combined = (
        "\n".join(
            path.read_text(encoding="utf-8")
            for path in [OUT_MD, OUT_HTML, OUT_AUDIT, TOP_DOC, GATE]
        )
        + "\n"
        + machine_lines
    )
    for token in [
        "status: ready_for_separate_evidence_builder_request",
        "first_action_id: NEXT-EBR-001",
        "first_blocker_id: separate_evidence_builder_request",
        "primary_human_input_lane: commercial_sprint_evidence_builder_request_review",
        "preferred_human_input_path: separate_evidence_builder_request",
        "template_transfer_performed: true",
        "template_transfer_execution_allowed: false",
        "ready_for_validator_approval: false",
        "ready_for_validator_execution: false",
        "approved_validator_count: 0",
        "validator_execution_authorized_count: 0",
        "validator_execution_run_status: completed_all_validators_passed",
        "validator_hold_output_review_completed: false",
        "validator_outputs_review_required: false",
        "validator_missing_input_completion_required: false",
        "rerun_validators_after_completion_required: false",
        "total_missing_metadata_field_count: 0",
        "total_missing_evidence_item_count: 0",
        "total_missing_source_note_count: 0",
        "local_validators_run: true",
        "validators_run_count: 5",
        "validator_hold_count: 0",
        "validator_pass_count: 5",
        "builder_ready_count: 5",
        "blockers_closed_by_validator_run: 0",
        "requires_validator_output_review: false",
        "requires_validator_input_completion: false",
        "requires_validator_rerun_after_completion: false",
        "requires_separate_evidence_builder_request: true",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "单独创建 evidence builder 执行请求",
    ]:
        require(token in combined, "missing token " + token)
    for token in [
        "production_ready: true",
        '"production_ready": true',
        "ready_for_validator_execution: true",
        '"ready_for_validator_execution": true',
        "recommend_for_validator_execution: true",
    ]:
        require(token not in combined, "forbidden token " + token)

    print(
        "SAEE_COMMERCIAL_READINESS_BEGIN_HERE_SMOKE: PASS "
        "status=ready_for_separate_evidence_builder_request blockers_closed_by_begin_here=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
