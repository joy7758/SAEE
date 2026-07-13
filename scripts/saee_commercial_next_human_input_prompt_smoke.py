#!/usr/bin/env python3
"""Smoke test for the current commercial next human input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_RUNNER = ROOT / "scripts/saee_commercial_next_action_summary.py"
RUNNER = ROOT / "scripts/saee_commercial_next_human_input_prompt.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_action_summary"
OUTPUT_JSON = OUTPUT_DIR / "commercial_next_human_input_prompt.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_next_human_input_prompt.md"
OUTPUT_HTML = OUTPUT_DIR / "commercial_next_human_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT_SMOKE: FAIL " + message)


def main() -> int:
    subprocess.run([sys.executable, str(SUMMARY_RUNNER)], cwd=ROOT, check=True, text=True)
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_HTML, TOP_DOC, GATE]:
        require(path.exists(), f"{path.relative_to(ROOT)} missing")

    payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_next_human_input_prompt_v0_1": True,
        "local_static_next_action_html": True,
        "prompt_type": "saee_commercial_next_human_input_prompt",
        "prompt_scope": "local_terminal_evidence_builder_request_prompt_with_related_sequence_context",
        "status": "ready_for_separate_evidence_builder_request",
        "action_id": "NEXT-EBR-001",
        "sequence_step_id": "EBR-001",
        "first_blocker_id": "separate_evidence_builder_request",
        "primary_human_input_lane": "commercial_sprint_evidence_builder_request_review",
        "preferred_human_input_path": "separate_evidence_builder_request",
        "selected_blocker_count": 5,
        "preferred_template_row_count": 5,
        "preferred_template_value_present_row_count": 5,
        "preferred_template_missing_value_row_count": 0,
        "full_quick_fill_missing_value_row_count": 0,
        "completed_value_row_count": 64,
        "missing_value_row_count": 0,
        "required_human_field_count": 1,
        "ready_for_template_transfer_request": True,
        "ready_for_template_transfer_execution": False,
        "template_transfer_performed": True,
        "template_transfer_values_transferred": True,
        "template_transfer_human_filled_templates_written": True,
        "template_transfer_values_transferred_count": 64,
        "template_transfer_templates_written_count": 5,
        "template_transfer_execution_allowed": False,
        "template_transfer_applier_execution_allowed": False,
        "ready_for_validator_approval": False,
        "ready_for_validator_execution": False,
        "planned_validator_count": 5,
        "ready_validator_count": 5,
        "validator_hold_count": 0,
        "validator_pass_count": 5,
        "builder_ready_count": 5,
        "approved_validator_count": 0,
        "validator_execution_authorized_count": 0,
        "validators_run": True,
        "validators_run_on_real_input": True,
        "requires_validator_approval_review": False,
        "requires_validator_output_review": False,
        "requires_validator_input_completion": False,
        "requires_validator_rerun_after_completion": False,
        "requires_separate_validator_execution_request": False,
        "requires_separate_evidence_builder_request": True,
        "validator_hold_output_review_completed": False,
        "validator_missing_input_completion_required": False,
        "rerun_validators_after_completion_required": False,
        "total_missing_metadata_field_count": 0,
        "total_missing_evidence_item_count": 0,
        "total_missing_source_note_count": 0,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "real_evidence_created": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blockers_closed_by_prompt": 0,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "next_action_html": "phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_human_input_prompt.html",
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    fields = payload.get("required_human_fields")
    require(fields == ["human_evidence_builder_execution_decision"], "required fields must request builder decision")
    related_step = payload.get("related_human_sequence_step")
    require(isinstance(related_step, dict), "related human sequence step must be object")
    require(related_step.get("execution_allowed_by_summary") is False, "related execution false")
    require(related_step.get("evidence_collection_authorized") is False, "related evidence false")
    require(
        related_step.get("blocker_closure_allowed_by_summary") is False,
        "related closure false",
    )

    html = OUTPUT_HTML.read_text(encoding="utf-8")
    combined = (
        "\n".join(path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE])
        + "\n"
        + html
    )
    for token in [
        "commercial_next_human_input_prompt_v0_1: true",
        "local_static_next_action_html: true",
        "status: ready_for_separate_evidence_builder_request",
        "prompt_scope: local_terminal_evidence_builder_request_prompt_with_related_sequence_context",
        "action_id: NEXT-EBR-001",
        "sequence_step_id: EBR-001",
        "first_blocker_id: separate_evidence_builder_request",
        "primary_human_input_lane: commercial_sprint_evidence_builder_request_review",
        "preferred_human_input_path: separate_evidence_builder_request",
        "template_transfer_performed: true",
        "template_transfer_execution_allowed: false",
        "template_transfer_applier_execution_allowed: false",
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
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: recommend",
        "recommend_for_human_input_prompt: true",
        "recommend_for_validator_approval_review: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_production: false",
        "缺失值",
        "Codex 不能直接执行 evidence builder",
        "不关闭 blocker",
    ]:
        require(token in combined, "missing token " + token)
    for token in ["<script", "https://", "http://", "fetch(", "XMLHttpRequest"]:
        require(token not in html, "HTML companion contains forbidden token " + token)

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "ready_for_validator_execution: true",
        '"ready_for_validator_execution": true',
        "recommend_for_validator_execution: true",
        "recommend_for_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    text = "\n".join([json.dumps(payload), combined])
    found = [token for token in forbidden if token in text]
    require(not found, "forbidden claims found: " + ", ".join(found))
    print(
        "SAEE_COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT_SMOKE: PASS "
        "status=ready_for_separate_evidence_builder_request validators_run=true "
        "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
