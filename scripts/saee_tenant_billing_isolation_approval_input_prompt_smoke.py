#!/usr/bin/env python3
"""Smoke check for the SAEE tenant-billing-isolation approval input prompt."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PROMPT_JSON = EVIDENCE_DIR / "tenant_billing_isolation_approval_input_prompt.local.json"
PROMPT_MD = EVIDENCE_DIR / "tenant_billing_isolation_approval_input_prompt.md"
PROMPT_HTML = EVIDENCE_DIR / "tenant_billing_isolation_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
RUNNER = ROOT / "scripts/saee_tenant_billing_isolation_approval_input_prompt.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: "
            + message
        )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in [PROMPT_JSON, PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE, RUNNER]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    prompt = read_json(PROMPT_JSON)
    expected = {
        "tenant_billing_isolation_approval_input_prompt_v0_1": True,
        "local_static_tenant_billing_isolation_approval_input_prompt_html": True,
        "browser_readable_tenant_billing_isolation_approval_input_prompt": True,
        "plain_language_tenant_billing_isolation_entry_v0_2": True,
        "prompt_type": "saee_tenant_billing_isolation_approval_input_prompt",
        "prompt_scope": "local_human_tenant_billing_isolation_input_prompt_only",
        "status": "hold_human_tenant_billing_isolation_input_required",
        "builder_ready": False,
        "tenant_billing_isolation_evidence_complete_for_review": False,
        "tenant_billing_isolation_available": False,
        "tenant_billing_isolation_approved": False,
        "required_metadata_field_count": 11,
        "completed_metadata_field_count": 0,
        "required_tenant_billing_isolation_evidence_item_count": 6,
        "completed_tenant_billing_isolation_evidence_item_count": 0,
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
        "tenant_billing_isolation_published": False,
        "tenant_billing_isolated": False,
        "tenant_billing_isolation_enabled": False,
        "tenant_billing_account_model_available": False,
        "billing_audit_metadata_policy_available": False,
        "tenant_billing_retention_policy_available": False,
        "tenant_invoice_numbering_available": False,
        "tenant_privacy_security_review_completed": False,
        "payment_provider_tenant_mapping_approved": False,
        "payment_provider_tenant_mapping_configured": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "production_billing_enabled": False,
        "tenant_billing_isolation_claim_published": False,
        "tenant_billing_isolation_completed_by_codex": False,
        "tenant_billing_isolation_execution_authorized": False,
        "codex_published_tenant_billing_isolation": False,
        "codex_processed_tenant_billing": False,
        "codex_configured_tenant_billing_handling": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"{key} must be {value}")

    require(
        prompt.get("target_blocker_ids") == ["tenant_billing_isolation"],
        "target blocker changed",
    )
    require(
        prompt.get("source_tenant_billing_isolation_approval_input_prompt_html")
        == "phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_approval_input_prompt.html",
        "HTML source path mismatch",
    )
    require(
        prompt.get("plain_language_status_label")
        == "租户账单隔离还没有批准，也没有启用",
        "plain language status label mismatch",
    )
    require(
        prompt.get("tenant_billing_isolation_human_review_step_count") == 4,
        "plain language review step count mismatch",
    )

    metadata = prompt.get("metadata_fields_to_fill")
    require(isinstance(metadata, list) and len(metadata) == 11, "metadata count")
    for item in metadata:
        require(item.get("human_must_provide") is True, "metadata must require human")
        require(item.get("codex_may_fill") is False, "metadata codex_may_fill false")

    keys = prompt.get("tenant_billing_isolation_keys_to_review")
    require(isinstance(keys, list) and len(keys) == 6, "tenant billing key count")
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
        "tenant_billing_isolation_evidence_input.template.json",
        "tenant_billing_isolation_evidence_input.human_filled.local.json",
        "saee_tenant_billing_isolation_evidence_builder.py",
    ]:
        require(token in command_text, "missing command token: " + token)

    docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE]
    )
    for token in [
        "tenant_billing_isolation_approval_input_prompt_v0_1: true",
        "plain_language_tenant_billing_isolation_entry_v0_2: true",
        "local_static_tenant_billing_isolation_approval_input_prompt_html: true",
        "browser_readable_tenant_billing_isolation_approval_input_prompt: true",
        "source_tenant_billing_isolation_approval_input_prompt_html: phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_approval_input_prompt.html",
        "plain_language_status_label: 租户账单隔离还没有批准，也没有启用",
        "SAEE 租户账单隔离人工审批入口",
        "先把租户账单边界审清楚，再决定能不能支持多租户付费。",
        "不批准租户账单模型、不运行跨租户测试、不配置支付平台租户映射、不收款、不关闭阻塞项",
        "Codex 可代执行：false",
        "status: hold_human_tenant_billing_isolation_input_required",
        "required_metadata_field_count: 11",
        "required_tenant_billing_isolation_evidence_item_count: 6",
        "builder_ready: false",
        "ready_for_evidence_builder: false",
        "tenant_billing_isolation_available: false",
        "tenant_billing_isolation_approved: false",
        "tenant_billing_isolation_published: false",
        "tenant_billing_isolated: false",
        "tenant_billing_isolation_enabled: false",
        "tenant_billing_account_model_available: false",
        "billing_audit_metadata_policy_available: false",
        "tenant_billing_retention_policy_available: false",
        "tenant_invoice_numbering_available: false",
        "tenant_privacy_security_review_completed: false",
        "payment_provider_tenant_mapping_approved: false",
        "payment_provider_tenant_mapping_configured: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "codex_published_tenant_billing_isolation: false",
        "codex_processed_tenant_billing: false",
        "codex_configured_tenant_billing_handling: false",
        "recommend_for_human_tenant_billing_isolation_input_prompt",
        "recommend_for_evidence_builder_execution: false",
    ]:
        require(token in docs, "missing doc token: " + token)

    html = PROMPT_HTML.read_text(encoding="utf-8")
    for token in ["<script", "fetch(", "XMLHttpRequest", "<form", "https://", "mailto:"]:
        require(token not in html, "HTML must not contain token: " + token)

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
        "tenant_billing_isolation_available: true",
        '"tenant_billing_isolation_available": true',
        "tenant_billing_isolation_approved: true",
        '"tenant_billing_isolation_approved": true',
        "tenant_billing_isolation_published: true",
        '"tenant_billing_isolation_published": true',
        "tenant_billing_isolated: true",
        '"tenant_billing_isolated": true',
        "tenant_billing_isolation_enabled: true",
        '"tenant_billing_isolation_enabled": true',
        "payment_provider_tenant_mapping_configured: true",
        '"payment_provider_tenant_mapping_configured": true',
        "customer_payment_collected: true",
        '"customer_payment_collected": true',
        "revenue_validated: true",
        '"revenue_validated": true',
        "codex_published_tenant_billing_isolation: true",
        "codex_processed_tenant_billing: true",
        "codex_configured_tenant_billing_handling: true",
        "recommend_for_tenant_billing_account_model_approval: true",
        "recommend_for_cross_tenant_billing_test_execution: true",
        "recommend_for_payment_provider_tenant_mapping_configuration: true",
        "recommend_for_payment_collection: true",
        "recommend_for_revenue_validation: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden if token in docs]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print("SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT_SMOKE: PASS")


if __name__ == "__main__":
    main()
