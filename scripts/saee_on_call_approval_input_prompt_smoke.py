#!/usr/bin/env python3
"""Smoke test for the on-call approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_on_call_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "on_call_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "on_call_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "on_call_approval_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/ON_CALL_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_ON_CALL_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_ON_CALL_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path}: {exc}")
    require(isinstance(value, dict), f"{path} must be object")
    return value


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        fail("runner failed")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "on_call_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_on_call_approval_input_prompt",
        "prompt_scope": "local_human_on_call_input_prompt_only",
        "status": "hold_human_on_call_input_required",
        "target_blocker_id": "on_call_rotation",
        "category": "operations",
        "validation_status": "hold",
        "local_static_on_call_approval_input_prompt_html": True,
        "browser_readable_on_call_approval_input_prompt": True,
        "plain_language_on_call_approval_input_prompt_v0_2": True,
        "on_call_human_review_step_count": 4,
        "builder_ready": False,
        "ready_for_evidence_builder": False,
        "on_call_rotation_available": False,
        "on_call_rotation_approved": False,
        "on_call_rotation_started": False,
        "escalation_schedule_published": False,
        "incident_commander_assigned": False,
        "support_operations_started": False,
        "required_metadata_field_count": 5,
        "completed_metadata_field_count": 0,
        "required_on_call_evidence_item_count": 3,
        "completed_on_call_evidence_item_count": 0,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "production_on_call_claim_published": False,
        "production_support_claim_published": False,
        "production_support_available": False,
        "support_contact_available": False,
        "customer_support_available": False,
        "sla_available": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    metadata = payload.get("metadata_fields_to_fill")
    require(isinstance(metadata, list), "metadata_fields_to_fill must be list")
    require(len(metadata) == 5, "metadata_fields_to_fill must have five fields")
    require(
        all(item.get("human_must_provide") is True for item in metadata),
        "metadata requires human input",
    )
    require(
        all(item.get("codex_may_fill") is False for item in metadata),
        "metadata codex_may_fill false",
    )

    keys = payload.get("on_call_evidence_keys_to_review")
    require(isinstance(keys, list), "on_call_evidence_keys_to_review must be list")
    require(len(keys) == 3, "on_call_evidence_keys_to_review must have three keys")
    for flag in [
        "set_evidence_review_to_true_only_after_human_approval",
        "human_source_note_required",
        "on_call_evidence_slot_required",
        "evidence_reference_required",
        "owner_named_required",
        "reviewed_by_human_required",
    ]:
        require(all(item.get(flag) is True for item in keys), f"{flag} required")
    require(all(item.get("codex_may_fill") is False for item in keys), "keys codex false")

    require(
        "on_call_evidence_input.template.json" in payload.get("copy_template_command", ""),
        "copy command missing template",
    )
    require(
        "on_call_evidence_input.human_filled.local.json"
        in payload.get("copy_template_command", ""),
        "copy command missing human input",
    )
    require(
        "saee_on_call_approval_input_validator.py" in payload.get("validator_command", ""),
        "validator command missing",
    )
    require(
        payload.get("source_on_call_approval_input_prompt_html")
        == "phase_b_product/commercial_readiness/support_evidence/on_call_approval_input_prompt.html",
        "source_on_call_approval_input_prompt_html missing",
    )
    require(
        "值班安排还没有人工批准" in payload.get("plain_language_status_label", ""),
        "plain language status missing",
    )

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "on_call_approval_input_prompt_v0_1: true",
            "status: hold_human_on_call_input_required",
            "target_blocker_id: on_call_rotation",
            "required_metadata_field_count: 5",
            "required_on_call_evidence_item_count: 3",
            "builder_ready: false",
            "ready_for_evidence_builder: false",
            "on_call_rotation_available: false",
            "on_call_rotation_approved: false",
            "on_call_rotation_started: false",
            "escalation_schedule_published: false",
            "incident_commander_assigned: false",
            "support_operations_started: false",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "<title>SAEE 值班安排人工审批入口</title>",
        "先确认谁负责值守，再谈正式商用。",
        "等待人工填写",
        "必须由人填写的字段",
        "必须由人审查的值班证据",
        "到这里必须停下",
        "on_call_rotation_available:</strong> false",
        "on_call_rotation_approved:</strong> false",
        "on_call_rotation_started:</strong> false",
        "escalation_schedule_published:</strong> false",
        "incident_commander_assigned:</strong> false",
        "support_operations_started:</strong> false",
        "customer_contacted:</strong> false",
        "production_ready:</strong> false",
        "private_core_exposed:</strong> false",
        "blockers_closed_by_prompt:</strong> 0",
    ]:
        require(token in html, f"html missing {token}")
    for token in [
        "answer: recommend",
        "recommend_for_human_on_call_input_prompt: true",
        "recommend_for_on_call_approval_by_codex: false",
        "recommend_for_on_call_start: false",
        "recommend_for_escalation_schedule_publication: false",
        "recommend_for_incident_commander_assignment: false",
        "recommend_for_support_operations_start: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
    ]:
        require(token in gate, f"gate missing {token}")

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "on_call_rotation_available: true",
        '"on_call_rotation_available": true',
        "on_call_rotation_approved: true",
        '"on_call_rotation_approved": true',
        "on_call_rotation_started: true",
        '"on_call_rotation_started": true',
        "escalation_schedule_published: true",
        '"escalation_schedule_published": true',
        "incident_commander_assigned: true",
        '"incident_commander_assigned": true',
        "support_operations_started: true",
        '"support_operations_started": true',
        "production_support_available: true",
        '"production_support_available": true',
        "builder_ready: true",
        '"builder_ready": true',
        "ready_for_evidence_builder: true",
        '"ready_for_evidence_builder": true',
        "recommend_for_on_call_approval_by_codex: true",
        "recommend_for_on_call_start: true",
        "recommend_for_escalation_schedule_publication: true",
        "recommend_for_incident_commander_assignment: true",
        "recommend_for_support_operations_start: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    forbidden_html_tokens = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "mailto:",
        "saee_v1_0",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]
    found_html = [token for token in forbidden_html_tokens if token in html]
    require(not found_html, "html contains forbidden tokens: " + ", ".join(found_html))

    combined = "\n".join([json.dumps(payload), markdown, html, top_doc, gate])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_ON_CALL_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
