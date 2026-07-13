#!/usr/bin/env python3
"""Smoke test for the production monitoring approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_production_monitoring_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "production_monitoring_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "production_monitoring_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "production_monitoring_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message
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
        "production_monitoring_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_production_monitoring_approval_input_prompt",
        "prompt_scope": "local_human_production_monitoring_input_prompt_only",
        "status": "hold_human_production_monitoring_input_required",
        "target_blocker_id": "production_monitoring",
        "category": "operations",
        "validation_status": "pass",
        "local_static_production_monitoring_approval_input_prompt_html": True,
        "browser_readable_production_monitoring_approval_input_prompt": True,
        "plain_language_production_monitoring_approval_input_prompt_v0_2": True,
        "production_monitoring_human_review_step_count": 4,
        "builder_ready": False,
        "production_monitoring_available": False,
        "production_monitoring_approved": False,
        "production_monitoring_deployed": False,
        "required_metadata_field_count": 5,
        "completed_metadata_field_count": 0,
        "required_monitoring_evidence_item_count": 5,
        "completed_monitoring_evidence_item_count": 0,
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
        "production_monitoring_approved_by_codex": False,
        "production_monitoring_deployed_by_codex": False,
        "dashboard_configured_by_codex": False,
        "metrics_export_enabled_by_codex": False,
        "log_retention_changed_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "production_monitoring_claim_published": False,
        "external_alert_delivery_enabled": False,
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

    keys = payload.get("monitoring_evidence_keys_to_review")
    require(isinstance(keys, list), "monitoring_evidence_keys_to_review must be list")
    require(len(keys) == 5, "monitoring_evidence_keys_to_review must have five keys")
    require(
        all(item.get("codex_may_fill") is False for item in keys),
        "monitoring keys codex_may_fill false",
    )
    require(
        all(item.get("human_source_note_required") is True for item in keys),
        "monitoring source notes required",
    )
    require(
        all(item.get("monitoring_evidence_slot_required") is True for item in keys),
        "monitoring evidence slots required",
    )
    require(
        all(item.get("owner_named_required") is True for item in keys),
        "monitoring owner name required",
    )
    require(
        all(item.get("reviewed_by_human_required") is True for item in keys),
        "monitoring human review required",
    )

    require(
        "production_monitoring_evidence_input.template.json"
        in payload.get("copy_template_command", ""),
        "copy command missing template",
    )
    require(
        "production_monitoring_evidence_input.human_filled.local.json"
        in payload.get("copy_template_command", ""),
        "copy command missing human input",
    )
    require(
        "saee_production_monitoring_approval_input_validator.py"
        in payload.get("validator_command", ""),
        "validator command missing",
    )
    require(
        payload.get("source_production_monitoring_approval_input_prompt_html")
        == "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_prompt.html",
        "source_production_monitoring_approval_input_prompt_html missing",
    )
    require(
        "生产监控还没有人工批准" in payload.get("plain_language_status_label", ""),
        "plain language status missing",
    )

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "production_monitoring_approval_input_prompt_v0_1: true",
            "status: hold_human_production_monitoring_input_required",
            "target_blocker_id: production_monitoring",
            "required_metadata_field_count: 5",
            "required_monitoring_evidence_item_count: 5",
            "builder_ready: false",
            "production_monitoring_available: false",
            "production_monitoring_approved: false",
            "production_monitoring_deployed: false",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "<title>SAEE 生产监控人工审批入口</title>",
        "先确认谁看护线上状态，再谈正式商用。",
        "等待人工填写",
        "必须由人填写的字段",
        "必须由人审查的监控证据",
        "到这里必须停下",
        "production_monitoring_available:</strong> false",
        "production_monitoring_approved:</strong> false",
        "production_monitoring_deployed:</strong> false",
        "dashboard_configured_by_codex:</strong> false",
        "metrics_export_enabled_by_codex:</strong> false",
        "log_retention_changed_by_codex:</strong> false",
        "customer_contacted:</strong> false",
        "production_ready:</strong> false",
        "private_core_exposed:</strong> false",
        "blockers_closed_by_prompt:</strong> 0",
    ]:
        require(token in html, f"html missing {token}")
    for token in [
        "answer: recommend",
        "recommend_for_human_production_monitoring_input_prompt: true",
        "recommend_for_monitoring_approval_by_codex: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_monitoring_deployment: false",
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
        "production_monitoring_available: true",
        '"production_monitoring_available": true',
        "production_monitoring_approved: true",
        '"production_monitoring_approved": true',
        "production_monitoring_deployed: true",
        '"production_monitoring_deployed": true',
        "builder_ready: true",
        '"builder_ready": true',
        "dashboard_configured_by_codex: true",
        '"dashboard_configured_by_codex": true',
        "metrics_export_enabled_by_codex: true",
        '"metrics_export_enabled_by_codex": true',
        "log_retention_changed_by_codex: true",
        '"log_retention_changed_by_codex": true',
        "recommend_for_monitoring_approval_by_codex: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_monitoring_deployment: true",
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

    print("SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
