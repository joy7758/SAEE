#!/usr/bin/env python3
"""Smoke check for the SAEE payment-provider approval input prompt."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PROMPT_JSON = EVIDENCE_DIR / "payment_provider_approval_input_prompt.local.json"
PROMPT_MD = EVIDENCE_DIR / "payment_provider_approval_input_prompt.md"
PROMPT_HTML = EVIDENCE_DIR / "payment_provider_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
RUNNER = ROOT / "scripts/saee_payment_provider_approval_input_prompt.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: " + message
        )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in [PROMPT_JSON, PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE, RUNNER]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    prompt = read_json(PROMPT_JSON)
    expected = {
        "payment_provider_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_payment_provider_approval_input_prompt",
        "prompt_scope": "local_human_payment_provider_input_prompt_only",
        "status": "hold_human_payment_provider_input_required",
        "builder_ready": False,
        "payment_provider_evidence_complete_for_review": False,
        "payment_provider_selected": False,
        "payment_provider_configured": False,
        "local_static_payment_provider_approval_input_prompt_html": True,
        "browser_readable_payment_provider_approval_input_prompt": True,
        "plain_language_payment_provider_review_entry_v0_2": True,
        "plain_language_status_label": "支付服务还没有选择，也没有配置",
        "plain_language_next_action": "先由人审支付服务、结账、回调和安全边界，再填写本地证据模板。",
        "payment_provider_human_review_step_count": 4,
        "required_metadata_field_count": 7,
        "completed_metadata_field_count": 0,
        "required_payment_provider_evidence_item_count": 6,
        "completed_payment_provider_evidence_item_count": 0,
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
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
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
        "payment_provider_contacted": False,
        "checkout_enabled": False,
        "payment_provider_live_mode_enabled": False,
        "payment_link_created": False,
        "webhook_endpoint_created": False,
        "webhook_secret_configured": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "production_billing_enabled": False,
        "codex_selected_payment_provider": False,
        "codex_contacted_payment_provider": False,
        "codex_configured_payment_provider": False,
        "codex_enabled_checkout": False,
        "codex_created_payment_link": False,
        "codex_processed_payment": False,
        "payment_provider_claim_published": False,
        "payment_provider_completed_by_codex": False,
        "payment_provider_execution_authorized": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"{key} must be {value}")

    require(prompt.get("target_blocker_ids") == ["payment_provider"], "target blocker changed")

    metadata = prompt.get("metadata_fields_to_fill")
    require(isinstance(metadata, list) and len(metadata) == 7, "metadata count")
    for item in metadata:
        require(item.get("human_must_provide") is True, "metadata must require human")
        require(item.get("codex_may_fill") is False, "metadata codex_may_fill false")

    keys = prompt.get("payment_provider_keys_to_review")
    require(isinstance(keys, list) and len(keys) == 6, "payment provider key count")
    for item in keys:
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
        "payment_provider_evidence_input.template.json",
        "payment_provider_evidence_input.human_filled.local.json",
        "saee_payment_provider_evidence_builder.py",
    ]:
        require(token in command_text, "missing command token: " + token)
    require(
        prompt.get("source_payment_provider_approval_input_prompt_html", "").endswith(
            "payment_provider_approval_input_prompt.html"
        ),
        "missing html source path",
    )

    docs = "\n".join(path.read_text(encoding="utf-8") for path in [PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE])
    for token in [
        "payment_provider_approval_input_prompt_v0_1: true",
        "plain_language_payment_provider_review_entry_v0_2: true",
        "plain_language_status_label: 支付服务还没有选择，也没有配置",
        "plain_language_next_action: 先由人审支付服务、结账、回调和安全边界，再填写本地证据模板。",
        "SAEE 支付服务人工审批入口",
        "先把收款风险审清楚，再决定能不能接支付。",
        "不会选择支付服务，不会联系供应商，不会配置支付，不会开结账，不会收款，也不会关闭商用阻塞项",
        "Codex 可代执行：false",
        "status: hold_human_payment_provider_input_required",
        "required_metadata_field_count: 7",
        "required_payment_provider_evidence_item_count: 6",
        "builder_ready: false",
        "ready_for_evidence_builder: false",
        "payment_provider_selected: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "payment_link_created: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "codex_selected_payment_provider: false",
        "codex_contacted_payment_provider: false",
        "codex_configured_payment_provider: false",
        "codex_enabled_checkout: false",
        "codex_created_payment_link: false",
        "codex_processed_payment: false",
        "recommend_for_human_payment_provider_input_prompt",
        "recommend_for_evidence_builder_execution: false",
    ]:
        require(token in docs, "missing doc token: " + token)

    forbidden = [
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
        "ready_for_evidence_builder: true",
        '"ready_for_evidence_builder": true',
        "payment_provider_selected: true",
        '"payment_provider_selected": true',
        "payment_provider_configured: true",
        '"payment_provider_configured": true',
        "checkout_enabled: true",
        '"checkout_enabled": true',
        "payment_link_created: true",
        '"payment_link_created": true',
        "webhook_endpoint_created: true",
        '"webhook_endpoint_created": true',
        "webhook_secret_configured: true",
        '"webhook_secret_configured": true',
        "customer_payment_collected: true",
        '"customer_payment_collected": true',
        "revenue_validated: true",
        '"revenue_validated": true',
        "codex_selected_payment_provider: true",
        "codex_contacted_payment_provider: true",
        "codex_configured_payment_provider: true",
        "codex_enabled_checkout: true",
        "codex_created_payment_link: true",
        "codex_processed_payment: true",
        "recommend_for_payment_provider_selection: true",
        "recommend_for_payment_provider_contact: true",
        "recommend_for_payment_provider_configuration: true",
        "recommend_for_checkout_enablement: true",
        "recommend_for_payment_link_creation: true",
        "recommend_for_webhook_setup: true",
        "recommend_for_payment_collection: true",
        "recommend_for_revenue_validation: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden if token in docs]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print("SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT_SMOKE: PASS")


if __name__ == "__main__":
    main()
