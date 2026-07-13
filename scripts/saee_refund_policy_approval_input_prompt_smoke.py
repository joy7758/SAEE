#!/usr/bin/env python3
"""Smoke check for the SAEE refund-policy approval input prompt."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PROMPT_JSON = EVIDENCE_DIR / "refund_policy_approval_input_prompt.local.json"
PROMPT_MD = EVIDENCE_DIR / "refund_policy_approval_input_prompt.md"
PROMPT_HTML = EVIDENCE_DIR / "refund_policy_approval_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/REFUND_POLICY_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_REFUND_POLICY_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
RUNNER = ROOT / "scripts/saee_refund_policy_approval_input_prompt.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_REFUND_POLICY_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in [PROMPT_JSON, PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE, RUNNER]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    prompt = read_json(PROMPT_JSON)
    expected = {
        "refund_policy_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_refund_policy_approval_input_prompt",
        "prompt_scope": "local_human_refund_policy_input_prompt_only",
        "status": "hold_human_refund_policy_input_required",
        "builder_ready": False,
        "refund_policy_evidence_complete_for_review": False,
        "refund_policy_available": False,
        "refund_policy_approved": False,
        "local_static_refund_policy_approval_input_prompt_html": True,
        "browser_readable_refund_policy_approval_input_prompt": True,
        "plain_language_refund_policy_entry_v0_2": True,
        "plain_language_status_label": "退款政策还没有批准，也没有发布",
        "plain_language_next_action": "先由人审退款规则、取消流程、试用转付费和服务故障补偿边界，再填写本地证据模板。",
        "refund_policy_human_review_step_count": 4,
        "required_metadata_field_count": 11,
        "completed_metadata_field_count": 0,
        "required_refund_policy_evidence_item_count": 5,
        "completed_refund_policy_evidence_item_count": 0,
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
        "tax_collection_started": False,
        "refund_policy_published": False,
        "refund_processed": False,
        "refund_issued_to_customer": False,
        "cancellation_process_available": False,
        "trial_conversion_policy_available": False,
        "service_failure_remedy_available": False,
        "refund_request_workflow_available": False,
        "payment_provider_refund_configured": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "production_billing_enabled": False,
        "refund_policy_claim_published": False,
        "refund_policy_completed_by_codex": False,
        "refund_policy_execution_authorized": False,
        "codex_published_refund_policy": False,
        "codex_processed_refund": False,
        "codex_configured_refund_handling": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"{key} must be {value}")

    require(prompt.get("target_blocker_ids") == ["refund_policy"], "target blocker changed")

    metadata = prompt.get("metadata_fields_to_fill")
    require(isinstance(metadata, list) and len(metadata) == 11, "metadata count")
    for item in metadata:
        require(item.get("human_must_provide") is True, "metadata must require human")
        require(item.get("codex_may_fill") is False, "metadata codex_may_fill false")

    keys = prompt.get("refund_policy_keys_to_review")
    require(isinstance(keys, list) and len(keys) == 5, "refund policy key count")
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
        "refund_policy_evidence_input.template.json",
        "refund_policy_evidence_input.human_filled.local.json",
        "saee_refund_policy_evidence_builder.py",
    ]:
        require(token in command_text, "missing command token: " + token)
    require(
        prompt.get("source_refund_policy_approval_input_prompt_html", "").endswith(
            "refund_policy_approval_input_prompt.html"
        ),
        "missing html source path",
    )

    docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE]
    )
    for token in [
        "refund_policy_approval_input_prompt_v0_1: true",
        "plain_language_refund_policy_entry_v0_2: true",
        "plain_language_status_label: 退款政策还没有批准，也没有发布",
        "plain_language_next_action: 先由人审退款规则、取消流程、试用转付费和服务故障补偿边界，再填写本地证据模板。",
        "SAEE 退款政策人工审批入口",
        "先把退款规则审清楚，再决定能不能对外收费。",
        "不会发布退款政策，不会处理退款，不会配置支付平台退款，不会收款，也不会关闭商用阻塞项",
        "Codex 可代执行：false",
        "status: hold_human_refund_policy_input_required",
        "required_metadata_field_count: 11",
        "required_refund_policy_evidence_item_count: 5",
        "builder_ready: false",
        "ready_for_evidence_builder: false",
        "refund_policy_available: false",
        "refund_policy_approved: false",
        "refund_policy_published: false",
        "refund_processed: false",
        "refund_issued_to_customer: false",
        "cancellation_process_available: false",
        "trial_conversion_policy_available: false",
        "service_failure_remedy_available: false",
        "refund_request_workflow_available: false",
        "payment_provider_refund_configured: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "codex_published_refund_policy: false",
        "codex_processed_refund: false",
        "codex_configured_refund_handling: false",
        "recommend_for_human_refund_policy_input_prompt",
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
        "refund_policy_available: true",
        '"refund_policy_available": true',
        "refund_policy_approved: true",
        '"refund_policy_approved": true',
        "refund_policy_published: true",
        '"refund_policy_published": true',
        "refund_processed: true",
        '"refund_processed": true',
        "refund_issued_to_customer: true",
        '"refund_issued_to_customer": true',
        "customer_payment_collected: true",
        '"customer_payment_collected": true',
        "revenue_validated: true",
        '"revenue_validated": true',
        "codex_published_refund_policy: true",
        "codex_processed_refund: true",
        "codex_configured_refund_handling: true",
        "recommend_for_refund_policy_publication: true",
        "recommend_for_cancellation_process_approval: true",
        "recommend_for_refund_processing: true",
        "recommend_for_payment_provider_refund_configuration: true",
        "recommend_for_payment_collection: true",
        "recommend_for_revenue_validation: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden if token in docs]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print("SAEE_REFUND_POLICY_APPROVAL_INPUT_PROMPT_SMOKE: PASS")


if __name__ == "__main__":
    main()
