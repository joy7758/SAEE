#!/usr/bin/env python3
"""Smoke check for the SAEE privacy/legal + DPA approval input prompt."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
)
PROMPT_JSON = EVIDENCE_DIR / "privacy_legal_dpa_approval_input_prompt.local.json"
PROMPT_MD = EVIDENCE_DIR / "privacy_legal_dpa_approval_input_prompt.md"
PROMPT_HTML = EVIDENCE_DIR / "privacy_legal_dpa_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
RUNNER = ROOT / "scripts/saee_privacy_legal_dpa_approval_input_prompt.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: " + message
        )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in [PROMPT_JSON, PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE, RUNNER]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    prompt = read_json(PROMPT_JSON)
    expected = {
        "privacy_legal_dpa_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_privacy_legal_dpa_approval_input_prompt",
        "prompt_scope": "local_human_privacy_legal_dpa_input_prompt_only",
        "status": "hold_human_privacy_legal_dpa_input_required",
        "builder_ready": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_available": False,
        "required_metadata_field_count": 7,
        "completed_metadata_field_count": 0,
        "required_privacy_legal_evidence_item_count": 7,
        "required_dpa_evidence_item_count": 6,
        "required_total_evidence_item_count": 13,
        "completed_total_evidence_item_count": 0,
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
        "source_privacy_legal_dpa_approval_input_prompt_html": (
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
            "privacy_legal_dpa_approval_input_prompt.html"
        ),
        "local_static_privacy_legal_dpa_approval_input_prompt_html": True,
        "browser_readable_privacy_legal_dpa_approval_input_prompt": True,
        "plain_language_privacy_legal_dpa_approval_input_prompt_v0_2": True,
        "privacy_legal_dpa_human_review_step_count": 5,
        "plain_language_status_label": "隐私法律审查和 DPA 还没有完成，也不能声称可以正式处理客户数据。",
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "codex_performed_legal_review": False,
        "codex_contacted_legal_counsel": False,
        "codex_created_dpa": False,
        "codex_approved_dpa": False,
        "codex_processed_customer_data": False,
        "privacy_legal_review_completed_by_codex": False,
        "data_processing_agreement_completed_by_codex": False,
        "legal_review_claim_published": False,
        "dpa_availability_claim_published": False,
        "customer_data_processing_claim_published": False,
        "legal_review_execution_authorized": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "dpa_sent_to_customer": False,
        "terms_published": False,
        "privacy_notice_published": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"{key} must be {value}")

    require(
        prompt.get("target_blocker_ids")
        == ["privacy_legal_review", "data_processing_agreement"],
        "target blocker ids changed",
    )

    metadata = prompt.get("metadata_fields_to_fill")
    require(isinstance(metadata, list) and len(metadata) == 7, "metadata count")
    for item in metadata:
        require(item.get("human_must_provide") is True, "metadata must require human")
        require(item.get("codex_may_fill") is False, "metadata codex_may_fill false")

    privacy_keys = prompt.get("privacy_legal_keys_to_review")
    dpa_keys = prompt.get("dpa_keys_to_review")
    require(isinstance(privacy_keys, list) and len(privacy_keys) == 7, "privacy key count")
    require(isinstance(dpa_keys, list) and len(dpa_keys) == 6, "DPA key count")
    for item in privacy_keys + dpa_keys:
        require(item.get("codex_may_fill") is False, "key codex_may_fill false")
        require(item.get("human_source_note_required") is True, "source note required")
        require(item.get("review_artifact_required") is True, "artifact required")
        require(item.get("owner_named_required") is True, "owner named required")
        require(item.get("reviewed_by_human_required") is True, "human review required")

    command_text = "\n".join(
        [
            prompt.get("copy_template_command", ""),
            prompt.get("builder_command_after_separate_approval", ""),
        ]
    )
    for token in [
        "privacy_legal_dpa_evidence_input.template.json",
        "privacy_legal_dpa_evidence_input.human_filled.local.json",
        "saee_privacy_legal_dpa_evidence_builder.py",
    ]:
        require(token in command_text, "missing command token: " + token)

    docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [PROMPT_MD, TOP_DOC, GATE]
    )
    for token in [
        "privacy_legal_dpa_approval_input_prompt_v0_1: true",
        "status: hold_human_privacy_legal_dpa_input_required",
        "source_privacy_legal_dpa_approval_input_prompt_html: phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_prompt.html",
        "local_static_privacy_legal_dpa_approval_input_prompt_html: true",
        "browser_readable_privacy_legal_dpa_approval_input_prompt: true",
        "plain_language_privacy_legal_dpa_approval_input_prompt_v0_2: true",
        "privacy_legal_dpa_human_review_step_count: 5",
        "plain_language_status_label: 隐私法律审查和 DPA 还没有完成，也不能声称可以正式处理客户数据。",
        "required_metadata_field_count: 7",
        "required_privacy_legal_evidence_item_count: 7",
        "required_dpa_evidence_item_count: 6",
        "required_total_evidence_item_count: 13",
        "builder_ready: false",
        "privacy_legal_review_completed: false",
        "data_processing_agreement_available: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "codex_performed_legal_review: false",
        "codex_created_dpa: false",
        "recommend_for_human_privacy_legal_dpa_input_prompt: true",
        "recommend_for_evidence_builder_execution: false",
    ]:
        require(token in docs, "missing doc token: " + token)

    html = PROMPT_HTML.read_text(encoding="utf-8")
    for token in [
        "<title>SAEE 隐私法律与 DPA 人工审批入口</title>",
        "先补齐隐私、法律和 DPA 证据，再谈正式商用。",
        "隐私法律审查和 DPA 还没有完成，也不能声称可以正式处理客户数据。",
        "隐私法律审查完成</span><code>false</code>",
        "DPA 可用</span><code>false</code>",
        "Codex 执行法律审查</span><code>false</code>",
        "客户数据已处理</span><code>false</code>",
        "生产可用</span><code>false</code>",
        "关闭 blocker</span><code>0</code>",
        "复制模板",
        "单独批准后才可运行",
        "不能越过的边界",
        "不做法律审查或隐私合规判断。",
        "不创建、批准或发送 DPA。",
        "不联系法律顾问、客户或供应商。",
        "不处理客户数据，不发布条款或隐私声明。",
        "不声称已完成法律审查或生产可用。",
    ]:
        require(token in html, "html missing token: " + token)

    forbidden = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "<form",
        "https://",
        "http://",
        "mailto:",
        "隐私法律审查完成</span><code>true</code>",
        "DPA 可用</span><code>true</code>",
        "Codex 执行法律审查</span><code>true</code>",
        "客户数据已处理</span><code>true</code>",
        "生产可用</span><code>true</code>",
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "builder_ready: true",
        '"builder_ready": true',
        "privacy_legal_review_completed: true",
        '"privacy_legal_review_completed": true',
        "data_processing_agreement_available: true",
        '"data_processing_agreement_available": true',
        "legal_counsel_contacted: true",
        "customer_data_processed: true",
        "dpa_sent_to_customer: true",
        "codex_performed_legal_review: true",
        "codex_created_dpa: true",
        "recommend_for_legal_review_execution_by_codex: true",
        "recommend_for_dpa_creation_by_codex: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden if token in docs + "\n" + html]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print("SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_SMOKE: PASS")


if __name__ == "__main__":
    main()
