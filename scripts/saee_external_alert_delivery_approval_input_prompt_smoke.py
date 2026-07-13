#!/usr/bin/env python3
"""Smoke test for the external alert delivery approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_external_alert_delivery_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "external_alert_delivery_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "external_alert_delivery_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "external_alert_delivery_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message
    )


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
        "external_alert_delivery_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_external_alert_delivery_approval_input_prompt",
        "prompt_scope": "local_human_external_alert_delivery_input_prompt_only",
        "status": "hold_human_external_alert_delivery_input_required",
        "target_blocker_id": "external_alert_delivery",
        "category": "operations",
        "source_external_alert_delivery_approval_input_prompt_html": "phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_prompt.html",
        "local_static_external_alert_delivery_approval_input_prompt_html": True,
        "browser_readable_external_alert_delivery_approval_input_prompt": True,
        "plain_language_external_alert_delivery_approval_input_prompt_v0_2": True,
        "external_alert_delivery_human_review_step_count": 4,
        "validation_status": "hold",
        "builder_ready": False,
        "external_alert_delivery_available": False,
        "external_alert_delivery_approved": False,
        "external_alert_delivery_enabled": False,
        "required_metadata_field_count": 5,
        "completed_metadata_field_count": 0,
        "required_alert_delivery_evidence_item_count": 6,
        "completed_alert_delivery_evidence_item_count": 0,
        "human_review_required": True,
        "separate_validator_required": True,
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
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "external_alert_delivery_approved_by_codex": False,
        "external_alert_delivery_enabled_by_codex": False,
        "external_alert_channel_configured_by_codex": False,
        "alert_routing_policy_published_by_codex": False,
        "alert_delivery_test_performed_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "production_alert_delivery_claim_published": False,
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

    keys = payload.get("alert_delivery_evidence_keys_to_review")
    require(isinstance(keys, list), "alert_delivery_evidence_keys_to_review must be list")
    require(len(keys) == 6, "alert_delivery_evidence_keys_to_review must have six keys")
    for item in keys:
        require(item.get("codex_may_fill") is False, "alert delivery codex_may_fill false")
        require(item.get("human_source_note_required") is True, "source notes required")
        require(
            item.get("alert_delivery_evidence_slot_required") is True,
            "alert delivery evidence slots required",
        )
        require(item.get("owner_named_required") is True, "owner name required")
        require(item.get("reviewed_by_human_required") is True, "human review required")

    for token in [
        "external_alert_delivery_evidence_input.template.json",
        "external_alert_delivery_evidence_input.human_filled.local.json",
        "saee_external_alert_delivery_approval_input_validator.py",
    ]:
        command_text = "\n".join(
            [payload.get("copy_template_command", ""), payload.get("validator_command", "")]
        )
        require(token in command_text, "missing command token: " + token)
    require(
        "外部告警送达还没有人工批准" in payload.get("plain_language_status_label", ""),
        "plain language status label missing",
    )

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "external_alert_delivery_approval_input_prompt_v0_1: true",
            "status: hold_human_external_alert_delivery_input_required",
            "target_blocker_id: external_alert_delivery",
            "required_metadata_field_count: 5",
            "required_alert_delivery_evidence_item_count: 6",
            "builder_ready: false",
            "external_alert_delivery_available: false",
            "external_alert_delivery_approved: false",
            "external_alert_delivery_enabled: false",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "<title>SAEE 外部告警送达人工审批入口</title>",
        "先确认告警真的能送到人，再谈正式商用。",
        "等待人工填写",
        "必须由人填写的字段",
        "必须由人审查的告警证据",
        "到这里必须停下",
        "external_alert_delivery_available:</strong> false",
        "external_alert_delivery_approved:</strong> false",
        "external_alert_delivery_enabled:</strong> false",
        "external_alert_channel_configured_by_codex:</strong> false",
        "alert_routing_policy_published_by_codex:</strong> false",
        "alert_delivery_test_performed_by_codex:</strong> false",
        "alert_provider_contacted_by_codex:</strong> false",
        "customer_contacted:</strong> false",
        "production_ready:</strong> false",
        "private_core_exposed:</strong> false",
        "blockers_closed_by_prompt:</strong> 0",
    ]:
        require(token in html, "html missing token: " + token)
    for token in [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "mailto:",
        "saee_v1_0",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]:
        require(token not in html, "html contains forbidden token: " + token)
    for token in [
        "answer: recommend",
        "recommend_for_human_external_alert_delivery_input_prompt: true",
        "recommend_for_external_alert_delivery_approval_by_codex: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_alert_channel_configuration: false",
        "recommend_for_alert_routing_publication: false",
        "recommend_for_alert_delivery_test_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
    ]:
        require(token in gate, f"gate missing {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_PROMPT_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_prompt.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_prompt.md",
        "/phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_prompt.html",
        "/docs/strategy/SAEE_EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md",
        "/scripts/saee_external_alert_delivery_approval_input_prompt.py",
        "/scripts/saee_external_alert_delivery_approval_input_prompt_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("external_alert_delivery_approval_input_prompt_v0_1", {})
    for key, value in {
        "status": "hold_human_external_alert_delivery_input_required",
        "prompt_type": "saee_external_alert_delivery_approval_input_prompt",
        "target_blocker_id": "external_alert_delivery",
        "source_external_alert_delivery_approval_input_prompt_html": "phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_prompt.html",
        "local_static_external_alert_delivery_approval_input_prompt_html": True,
        "browser_readable_external_alert_delivery_approval_input_prompt": True,
        "plain_language_external_alert_delivery_approval_input_prompt_v0_2": True,
        "external_alert_delivery_human_review_step_count": 4,
        "required_metadata_field_count": 5,
        "required_alert_delivery_evidence_item_count": 6,
        "builder_ready": False,
        "external_alert_delivery_available": False,
        "external_alert_delivery_approved": False,
        "external_alert_delivery_enabled": False,
        "blockers_closed_by_prompt": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print("SAEE_EXTERNAL_ALERT_DELIVERY_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
