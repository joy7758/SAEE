#!/usr/bin/env python3
"""Smoke test for the customer-support approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_customer_support_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "customer_support_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "customer_support_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "customer_support_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message)


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
        "customer_support_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_customer_support_approval_input_prompt",
        "prompt_scope": "local_human_customer_support_input_prompt_only",
        "status": "hold_human_customer_support_input_required",
        "target_blocker_id": "customer_support",
        "category": "support",
        "validation_status": "hold",
        "builder_ready": False,
        "ready_for_evidence_builder": False,
        "customer_support_available": False,
        "customer_support_approved": False,
        "customer_support_configured": False,
        "customer_support_published": False,
        "source_customer_support_approval_input_prompt_html": (
            "phase_b_product/commercial_readiness/support_evidence/"
            "customer_support_approval_input_prompt.html"
        ),
        "local_static_customer_support_approval_input_prompt_html": True,
        "browser_readable_customer_support_approval_input_prompt": True,
        "plain_language_customer_support_approval_input_prompt_v0_2": True,
        "support_operations_started": False,
        "support_process_started": False,
        "support_case_created": False,
        "customer_communication_sent": False,
        "staffed_support_started": False,
        "customer_support_human_review_step_count": 4,
        "plain_language_status_label": "客户支持流程还没有批准，也没有启用。",
        "required_metadata_field_count": 4,
        "completed_metadata_field_count": 0,
        "required_customer_support_evidence_item_count": 6,
        "completed_customer_support_evidence_item_count": 0,
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
        "customer_support_approved_by_codex": False,
        "customer_support_configured_by_codex": False,
        "customer_support_published_by_codex": False,
        "support_process_started_by_codex": False,
        "support_case_created_by_codex": False,
        "customer_communication_sent_by_codex": False,
        "support_vendor_contacted_by_codex": False,
        "production_support_claim_published": False,
        "customer_support_claim_published": False,
        "production_support_available": False,
        "support_process_available": False,
        "support_contact_available": False,
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

    keys = payload.get("customer_support_evidence_keys_to_review")
    require(isinstance(keys, list), "customer_support_evidence_keys_to_review must be list")
    require(len(keys) == 6, "customer_support_evidence_keys_to_review must have six keys")
    for flag in [
        "set_evidence_review_to_true_only_after_human_approval",
        "human_source_note_required",
        "process_evidence_slot_required",
        "evidence_reference_required",
        "owner_named_required",
        "reviewed_by_human_required",
    ]:
        require(all(item.get(flag) is True for item in keys), f"{flag} required")
    require(all(item.get("codex_may_fill") is False for item in keys), "keys codex false")

    require(
        "customer_support_evidence_input.template.json"
        in payload.get("copy_template_command", ""),
        "copy command missing template",
    )
    require(
        "customer_support_evidence_input.human_filled.local.json"
        in payload.get("copy_template_command", ""),
        "copy command missing human input",
    )
    require(
        "saee_customer_support_approval_input_validator.py"
        in payload.get("validator_command", ""),
        "validator command missing",
    )

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "customer_support_approval_input_prompt_v0_1: true",
            "status: hold_human_customer_support_input_required",
            "target_blocker_id: customer_support",
            "required_metadata_field_count: 4",
            "required_customer_support_evidence_item_count: 6",
            "builder_ready: false",
            "ready_for_evidence_builder: false",
            "customer_support_available: false",
            "customer_support_approved: false",
            "customer_support_configured: false",
            "customer_support_published: false",
            "support_operations_started: false",
            "support_process_started: false",
            "support_case_created: false",
            "customer_communication_sent: false",
            "staffed_support_started: false",
            "source_customer_support_approval_input_prompt_html: phase_b_product/commercial_readiness/support_evidence/customer_support_approval_input_prompt.html",
            "local_static_customer_support_approval_input_prompt_html: true",
            "browser_readable_customer_support_approval_input_prompt: true",
            "plain_language_customer_support_approval_input_prompt_v0_2: true",
            "customer_support_human_review_step_count: 4",
            "plain_language_status_label: 客户支持流程还没有批准，也没有启用。",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "<title>SAEE 客户支持流程人工审批入口</title>",
        "先把客服流程审清楚，再决定能不能对用户承诺支持。",
        "Codex 可代执行：<code>false</code>",
        "customer_support_available: <code>false</code>",
        "customer_support_published: <code>false</code>",
        "support_case_created: <code>false</code>",
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
        "customer_support_available: <code>true</code>",
        "customer_support_published: <code>true</code>",
        "support_case_created: <code>true</code>",
        "production_ready: <code>true</code>",
    ]
    found_html = [token for token in forbidden_html if token in html]
    require(not found_html, "html contains forbidden tokens: " + ", ".join(found_html))
    for token in [
        "answer: recommend",
        "recommend_for_human_customer_support_input_prompt: true",
        "recommend_for_customer_support_approval_by_codex: false",
        "recommend_for_customer_support_publication: false",
        "recommend_for_customer_support_configuration: false",
        "recommend_for_staffed_support_start: false",
        "recommend_for_support_case_creation: false",
        "recommend_for_customer_communication: false",
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
        "customer_support_available: true",
        '"customer_support_available": true',
        "customer_support_approved: true",
        '"customer_support_approved": true',
        "customer_support_configured: true",
        '"customer_support_configured": true',
        "customer_support_published: true",
        '"customer_support_published": true',
        "support_operations_started: true",
        '"support_operations_started": true',
        "support_process_started: true",
        '"support_process_started": true',
        "support_case_created: true",
        '"support_case_created": true',
        "customer_communication_sent: true",
        '"customer_communication_sent": true',
        "staffed_support_started: true",
        '"staffed_support_started": true',
        "production_support_available: true",
        '"production_support_available": true',
        "builder_ready: true",
        '"builder_ready": true',
        "ready_for_evidence_builder: true",
        '"ready_for_evidence_builder": true',
        "recommend_for_customer_support_approval_by_codex: true",
        "recommend_for_customer_support_publication: true",
        "recommend_for_customer_support_configuration: true",
        "recommend_for_staffed_support_start: true",
        "recommend_for_support_case_creation: true",
        "recommend_for_customer_communication: true",
        "recommend_for_support_operations_start: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    combined = "\n".join([json.dumps(payload), markdown, html, top_doc, gate])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
