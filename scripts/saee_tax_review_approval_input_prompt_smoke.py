#!/usr/bin/env python3
"""Smoke check for the SAEE tax-review approval input prompt."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PROMPT_JSON = EVIDENCE_DIR / "tax_review_approval_input_prompt.local.json"
PROMPT_MD = EVIDENCE_DIR / "tax_review_approval_input_prompt.md"
PROMPT_HTML = EVIDENCE_DIR / "tax_review_approval_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/TAX_REVIEW_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_TAX_REVIEW_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
RUNNER = ROOT / "scripts/saee_tax_review_approval_input_prompt.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TAX_REVIEW_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in [PROMPT_JSON, PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE, RUNNER]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    prompt = read_json(PROMPT_JSON)
    expected = {
        "tax_review_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_tax_review_approval_input_prompt",
        "prompt_scope": "local_human_tax_review_input_prompt_only",
        "status": "hold_human_tax_review_input_required",
        "builder_ready": False,
        "tax_review_evidence_complete_for_review": False,
        "tax_review_completed": False,
        "tax_collection_ready": False,
        "local_static_tax_review_approval_input_prompt_html": True,
        "browser_readable_tax_review_approval_input_prompt": True,
        "plain_language_tax_review_entry_v0_2": True,
        "plain_language_status_label": "税务审查还没有完成，也没有启用收税",
        "plain_language_next_action": "先由人审目标地区、税务责任、发票文字和币种规则，再填写本地证据模板。",
        "tax_review_human_review_step_count": 4,
        "required_metadata_field_count": 9,
        "completed_metadata_field_count": 0,
        "required_tax_review_evidence_item_count": 5,
        "completed_tax_review_evidence_item_count": 0,
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
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "payment_link_created": False,
        "invoice_sent_to_customer": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "tax_rate_configured": False,
        "tax_collection_started": False,
        "tax_exemption_process_available": False,
        "invoice_wording_published": False,
        "currency_policy_published": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "production_billing_enabled": False,
        "tax_review_claim_published": False,
        "tax_review_completed_by_codex": False,
        "tax_review_execution_authorized": False,
        "codex_contacted_tax_advisor": False,
        "codex_contacted_legal_counsel": False,
        "codex_configured_tax_collection": False,
        "codex_started_tax_collection": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"{key} must be {value}")

    require(prompt.get("target_blocker_ids") == ["tax_review"], "target blocker changed")

    metadata = prompt.get("metadata_fields_to_fill")
    require(isinstance(metadata, list) and len(metadata) == 9, "metadata count")
    for item in metadata:
        require(item.get("human_must_provide") is True, "metadata must require human")
        require(item.get("codex_may_fill") is False, "metadata codex_may_fill false")

    keys = prompt.get("tax_review_keys_to_review")
    require(isinstance(keys, list) and len(keys) == 5, "tax review key count")
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
        "tax_review_evidence_input.template.json",
        "tax_review_evidence_input.human_filled.local.json",
        "saee_tax_review_evidence_builder.py",
    ]:
        require(token in command_text, "missing command token: " + token)
    require(
        prompt.get("source_tax_review_approval_input_prompt_html", "").endswith(
            "tax_review_approval_input_prompt.html"
        ),
        "missing html source path",
    )

    docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE]
    )
    for token in [
        "tax_review_approval_input_prompt_v0_1: true",
        "plain_language_tax_review_entry_v0_2: true",
        "plain_language_status_label: 税务审查还没有完成，也没有启用收税",
        "plain_language_next_action: 先由人审目标地区、税务责任、发票文字和币种规则，再填写本地证据模板。",
        "SAEE 税务审查人工审批入口",
        "先把税务责任审清楚，再决定能不能收款。",
        "不会联系税务顾问，不会联系法务顾问，不会配置税率，不会开始收税，不会收款，也不会关闭商用阻塞项",
        "Codex 可代执行：false",
        "status: hold_human_tax_review_input_required",
        "required_metadata_field_count: 9",
        "required_tax_review_evidence_item_count: 5",
        "builder_ready: false",
        "ready_for_evidence_builder: false",
        "tax_review_completed: false",
        "tax_collection_ready: false",
        "tax_rate_configured: false",
        "tax_collection_started: false",
        "tax_exemption_process_available: false",
        "invoice_wording_published: false",
        "currency_policy_published: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "codex_contacted_tax_advisor: false",
        "codex_contacted_legal_counsel: false",
        "codex_configured_tax_collection: false",
        "codex_started_tax_collection: false",
        "recommend_for_human_tax_review_input_prompt",
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
        "tax_review_completed: true",
        '"tax_review_completed": true',
        "tax_rate_configured: true",
        '"tax_rate_configured": true',
        "tax_collection_started: true",
        '"tax_collection_started": true',
        "customer_payment_collected: true",
        '"customer_payment_collected": true',
        "revenue_validated: true",
        '"revenue_validated": true',
        "codex_contacted_tax_advisor: true",
        "codex_contacted_legal_counsel: true",
        "codex_configured_tax_collection: true",
        "codex_started_tax_collection: true",
        "recommend_for_tax_advisor_contact: true",
        "recommend_for_legal_counsel_contact: true",
        "recommend_for_tax_review_completion: true",
        "recommend_for_tax_rate_configuration: true",
        "recommend_for_tax_collection_start: true",
        "recommend_for_payment_collection: true",
        "recommend_for_revenue_validation: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden if token in docs]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print("SAEE_TAX_REVIEW_APPROVAL_INPUT_PROMPT_SMOKE: PASS")


if __name__ == "__main__":
    main()
