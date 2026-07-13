#!/usr/bin/env python3
"""Smoke test for the support-contact approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_contact_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "support_contact_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "support_contact_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "support_contact_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message)


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
        "support_contact_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_support_contact_approval_input_prompt",
        "prompt_scope": "local_human_support_contact_input_prompt_only",
        "status": "hold_human_support_contact_input_required",
        "target_blocker_id": "support_contact",
        "category": "support",
        "validation_status": "pass",
        "builder_ready": False,
        "ready_for_evidence_builder": False,
        "support_contact_available": False,
        "support_contact_approved": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "customer_facing_support_contact_configured": False,
        "support_operations_started": False,
        "source_support_contact_approval_input_prompt_html": (
            "phase_b_product/commercial_readiness/support_evidence/"
            "support_contact_approval_input_prompt.html"
        ),
        "local_static_support_contact_approval_input_prompt_html": True,
        "browser_readable_support_contact_approval_input_prompt": True,
        "plain_language_support_contact_approval_input_prompt_v0_2": True,
        "support_contact_human_review_step_count": 4,
        "plain_language_status_label": "客户支持入口还没有批准，也没有启用。",
        "required_metadata_field_count": 4,
        "completed_metadata_field_count": 0,
        "required_support_contact_evidence_item_count": 5,
        "completed_support_contact_evidence_item_count": 0,
        "candidate_contact_slot_count": 2,
        "minimum_completed_contact_slot_count": 1,
        "completed_contact_slot_count": 0,
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
        "support_vendor_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "support_contact_approved_by_codex": False,
        "support_contact_configured_by_codex": False,
        "support_contact_published_by_codex": False,
        "support_contact_tested_by_codex": False,
        "codex_published_support_contact": False,
        "codex_sent_support_contact_test": False,
        "support_contact_claim_published": False,
        "production_support_claim_published": False,
        "production_support_available": False,
        "support_process_available": False,
        "customer_support_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    metadata = payload.get("metadata_fields_to_fill")
    require(isinstance(metadata, list), "metadata_fields_to_fill must be list")
    require(len(metadata) == 4, "metadata_fields_to_fill must have four fields")
    require(
        all(item.get("human_must_provide") is True for item in metadata),
        "metadata requires human input",
    )
    require(
        all(item.get("codex_may_fill") is False for item in metadata),
        "metadata codex_may_fill false",
    )

    keys = payload.get("support_contact_evidence_keys_to_review")
    require(isinstance(keys, list), "support_contact_evidence_keys_to_review must be list")
    require(len(keys) == 5, "support_contact_evidence_keys_to_review must have five keys")
    for flag in [
        "set_evidence_review_to_true_only_after_human_approval",
        "human_source_note_required",
    ]:
        require(all(item.get(flag) is True for item in keys), f"{flag} required")
    require(all(item.get("codex_may_fill") is False for item in keys), "keys codex false")

    slots = payload.get("candidate_contact_slots_to_fill")
    require(isinstance(slots, list), "candidate_contact_slots_to_fill must be list")
    require(len(slots) == 2, "candidate_contact_slots_to_fill must have two slots")
    for flag in [
        "contact_channel_required",
        "display_value_redacted_required",
        "owner_named_required",
        "abuse_handling_reviewed_required",
        "customer_notice_route_reviewed_required",
        "test_plan_reviewed_required",
        "human_source_note_required",
    ]:
        require(all(item.get(flag) is True for item in slots), f"{flag} required")
    require(all(item.get("codex_may_fill") is False for item in slots), "slots codex false")

    require(
        "support_contact_decision_input.template.json" in payload.get("copy_template_command", ""),
        "copy command missing template",
    )
    require(
        "support_contact_decision_input.human_filled.local.json"
        in payload.get("copy_template_command", ""),
        "copy command missing human input",
    )
    require(
        "saee_support_contact_approval_input_validator.py"
        in payload.get("validator_command", ""),
        "validator command missing",
    )

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "support_contact_approval_input_prompt_v0_1: true",
            "status: hold_human_support_contact_input_required",
            "target_blocker_id: support_contact",
            "required_metadata_field_count: 4",
            "required_support_contact_evidence_item_count: 5",
            "candidate_contact_slot_count: 2",
            "minimum_completed_contact_slot_count: 1",
            "builder_ready: false",
            "ready_for_evidence_builder: false",
            "support_contact_available: false",
            "support_contact_approved: false",
            "support_contact_configured: false",
            "support_contact_published: false",
            "support_contact_test_performed: false",
            "customer_facing_support_contact_configured: false",
            "support_operations_started: false",
            "source_support_contact_approval_input_prompt_html: phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_prompt.html",
            "local_static_support_contact_approval_input_prompt_html: true",
            "browser_readable_support_contact_approval_input_prompt: true",
            "plain_language_support_contact_approval_input_prompt_v0_2: true",
            "support_contact_human_review_step_count: 4",
            "plain_language_status_label: 客户支持入口还没有批准，也没有启用。",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "<title>SAEE 客户支持联系入口人工审批入口</title>",
        "先把客户支持入口审清楚，再决定能不能公开给用户。",
        "Codex 可代执行：<code>false</code>",
        "support_contact_available: <code>false</code>",
        "support_contact_published: <code>false</code>",
        "customer_contacted: <code>false</code>",
        "production_ready: <code>false</code>",
        "private_core_exposed: <code>false</code>",
        "复制本地模板",
        "运行本地验证",
        "验证后停下",
    ]:
        require(token in html, f"html missing {token}")
    forbidden_html = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "<form",
        "https://",
        "http://",
        "mailto:",
        "support_contact_available: <code>true</code>",
        "support_contact_published: <code>true</code>",
        "production_ready: <code>true</code>",
    ]
    found_html = [token for token in forbidden_html if token in html]
    require(not found_html, "html contains forbidden tokens: " + ", ".join(found_html))
    for token in [
        "answer: recommend",
        "recommend_for_human_support_contact_input_prompt: true",
        "recommend_for_support_contact_approval_by_codex: false",
        "recommend_for_support_contact_publication: false",
        "recommend_for_support_contact_configuration: false",
        "recommend_for_support_contact_test: false",
        "recommend_for_customer_contact: false",
        "recommend_for_vendor_contact: false",
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
        "support_contact_available: true",
        '"support_contact_available": true',
        "support_contact_approved: true",
        '"support_contact_approved": true',
        "support_contact_configured: true",
        '"support_contact_configured": true',
        "support_contact_published: true",
        '"support_contact_published": true',
        "support_contact_test_performed: true",
        '"support_contact_test_performed": true',
        "customer_facing_support_contact_configured: true",
        '"customer_facing_support_contact_configured": true',
        "support_operations_started: true",
        '"support_operations_started": true',
        "production_support_available: true",
        '"production_support_available": true',
        "builder_ready: true",
        '"builder_ready": true',
        "ready_for_evidence_builder: true",
        '"ready_for_evidence_builder": true',
        "recommend_for_support_contact_approval_by_codex: true",
        "recommend_for_support_contact_publication: true",
        "recommend_for_support_contact_configuration: true",
        "recommend_for_support_contact_test: true",
        "recommend_for_customer_contact: true",
        "recommend_for_vendor_contact: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    combined = "\n".join([json.dumps(payload), markdown, html, top_doc, gate])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
