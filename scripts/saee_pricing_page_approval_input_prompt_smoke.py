#!/usr/bin/env python3
"""Smoke check for the SAEE pricing-page approval input prompt."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PROMPT_JSON = EVIDENCE_DIR / "pricing_page_approval_input_prompt.local.json"
PROMPT_MD = EVIDENCE_DIR / "pricing_page_approval_input_prompt.md"
PROMPT_HTML = EVIDENCE_DIR / "pricing_page_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRICING_PAGE_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRICING_PAGE_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
RUNNER = ROOT / "scripts/saee_pricing_page_approval_input_prompt.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRICING_PAGE_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in [PROMPT_JSON, PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE, RUNNER]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    prompt = read_json(PROMPT_JSON)
    expected = {
        "pricing_page_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_pricing_page_approval_input_prompt",
        "prompt_scope": "local_human_pricing_page_input_prompt_only",
        "status": "hold_human_pricing_page_input_required",
        "builder_ready": False,
        "pricing_page_evidence_complete_for_review": False,
        "pricing_page_available": False,
        "pricing_page_published": False,
        "local_static_pricing_page_approval_input_prompt_html": True,
        "browser_readable_pricing_page_approval_input_prompt": True,
        "plain_language_pricing_page_review_entry_v0_2": True,
        "plain_language_status_label": "定价页还没有批准，也没有发布",
        "plain_language_next_action": "先由人审定价文案和价格边界，再填写本地证据模板。",
        "pricing_page_human_review_step_count": 4,
        "required_metadata_field_count": 9,
        "completed_metadata_field_count": 0,
        "required_pricing_page_evidence_item_count": 5,
        "completed_pricing_page_evidence_item_count": 0,
        "human_review_required": True,
        "separate_validator_request_allowed": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_validator": False,
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
        "codex_approved_pricing_page": False,
        "codex_published_pricing_page": False,
        "codex_sent_sales_offer": False,
        "codex_contacted_customer": False,
        "codex_contacted_payment_provider": False,
        "codex_configured_payment_provider": False,
        "codex_enabled_checkout": False,
        "codex_collected_payment": False,
        "pricing_page_claim_published": False,
        "sales_offer_generated": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "production_billing_enabled": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"{key} must be {value}")

    require(prompt.get("target_blocker_ids") == ["pricing_page"], "target blocker changed")

    metadata = prompt.get("metadata_fields_to_fill")
    require(isinstance(metadata, list) and len(metadata) == 9, "metadata count")
    for item in metadata:
        require(item.get("human_must_provide") is True, "metadata must require human")
        require(item.get("codex_may_fill") is False, "metadata codex_may_fill false")

    keys = prompt.get("pricing_page_keys_to_review")
    require(isinstance(keys, list) and len(keys) == 5, "pricing page key count")
    for item in keys:
        require(item.get("codex_may_fill") is False, "key codex_may_fill false")
        require(item.get("human_source_note_required") is True, "source note required")
        require(item.get("review_artifact_required") is True, "artifact required")
        require(item.get("owner_named_required") is True, "owner named required")
        require(item.get("reviewed_by_human_required") is True, "human review required")

    command_text = "\n".join(
        [
            prompt.get("copy_template_command", ""),
            prompt.get("validator_command_after_human_input", ""),
            prompt.get("builder_command_after_separate_approval", ""),
        ]
    )
    for token in [
        "pricing_page_evidence_input.template.json",
        "pricing_page_evidence_input.human_filled.local.json",
        "saee_pricing_page_approval_input_validator.py",
        "saee_pricing_page_evidence_builder.py",
    ]:
        require(token in command_text, "missing command token: " + token)
    require(
        prompt.get("source_pricing_page_approval_input_prompt_html", "").endswith(
            "pricing_page_approval_input_prompt.html"
        ),
        "missing html source path",
    )

    docs = "\n".join(path.read_text(encoding="utf-8") for path in [PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE])
    for token in [
        "pricing_page_approval_input_prompt_v0_1: true",
        "plain_language_pricing_page_review_entry_v0_2: true",
        "plain_language_status_label: 定价页还没有批准，也没有发布",
        "plain_language_next_action: 先由人审定价文案和价格边界，再填写本地证据模板。",
        "SAEE 定价页人工审批入口",
        "先把定价说清楚，再决定能不能发布。",
        "不会生成价格，不会发布定价页，不会联系客户，不会配置支付，也不会关闭商用阻塞项",
        "Codex 可代执行：false",
        "status: hold_human_pricing_page_input_required",
        "required_metadata_field_count: 9",
        "required_pricing_page_evidence_item_count: 5",
        "builder_ready: false",
        "ready_for_validator: false",
        "ready_for_evidence_builder: false",
        "pricing_page_available: false",
        "pricing_page_published: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "codex_approved_pricing_page: false",
        "codex_published_pricing_page: false",
        "codex_sent_sales_offer: false",
        "codex_configured_payment_provider: false",
        "codex_enabled_checkout: false",
        "recommend_for_human_pricing_page_input_prompt",
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
        "ready_for_validator: true",
        '"ready_for_validator": true',
        "ready_for_evidence_builder: true",
        '"ready_for_evidence_builder": true',
        "pricing_page_published: true",
        '"pricing_page_published": true',
        "sales_offer_sent: true",
        "payment_provider_configured: true",
        "checkout_enabled: true",
        "customer_payment_collected: true",
        "revenue_validated: true",
        "codex_approved_pricing_page: true",
        "codex_published_pricing_page: true",
        "codex_sent_sales_offer: true",
        "recommend_for_pricing_page_publication: true",
        "recommend_for_sales_offer_generation: true",
        "recommend_for_payment_provider_configuration: true",
        "recommend_for_checkout_enablement: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden if token in docs]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print("SAEE_PRICING_PAGE_APPROVAL_INPUT_PROMPT_SMOKE: PASS")


if __name__ == "__main__":
    main()
