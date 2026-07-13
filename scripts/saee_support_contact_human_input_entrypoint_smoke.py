#!/usr/bin/env python3
"""Smoke test for the support-contact human input entrypoint."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SUMMARY = SUPPORT_DIR / "support_contact_human_input_entrypoint.local.json"
REPORT = SUPPORT_DIR / "support_contact_human_input_entrypoint.md"
HTML = SUPPORT_DIR / "support_contact_human_input_entrypoint.html"
CSV_PATH = SUPPORT_DIR / "support_contact_human_input_entrypoint.csv"
AUDIT = SUPPORT_DIR / "support_contact_human_input_entrypoint_boundary_audit.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_SUPPORT_CONTACT_HUMAN_INPUT_ENTRYPOINT_SMOKE: FAIL {message}")


def require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    for path in [SUMMARY, REPORT, HTML, CSV_PATH, AUDIT]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = {
        "support_contact_human_input_entrypoint_v0_1": True,
        "entrypoint_type": "support_contact_human_input_navigation",
        "entrypoint_scope": "unified_human_input_navigation_only_no_values_no_export_no_execution",
        "status": "ready_for_human_support_contact_input_navigation",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "support_contact",
        "plain_language_support_contact_entry_v0_2": True,
        "plain_language_status_label": "支持入口仍未配置",
        "plain_language_next_action": "先指定负责人，再人工填写支持入口信息。",
        "plain_language_stop_point": "只到本地检查为止；没有单独批准，不发布支持入口、不关闭阻塞项。",
        "support_contact_human_route_step_count": 3,
        "source_support_contact_human_input_entrypoint_html": "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_entrypoint.html",
        "local_static_support_contact_human_input_entrypoint_html": True,
        "browser_readable_support_contact_human_input_entrypoint": True,
        "review_batch_fill_card_row_count": 10,
        "review_batch_blank_value_row_count": 10,
        "combined_bridge_input_row_count": 16,
        "readiness_step_count": 5,
        "readiness_completed_step_count": 0,
        "readiness_incomplete_step_count": 5,
        "missing_first_owner_field_count": 5,
        "decision_required_human_field_count": 7,
        "human_input_required": True,
        "human_review_required": True,
        "blockers_closed_by_entrypoint": 0,
    }
    for key, expected_value in expected.items():
        if data.get(key) != expected_value:
            fail(f"{key} must be {expected_value!r}")

    if data.get("missing_support_decision_field_count", 0) < 10:
        fail("missing_support_decision_field_count should show incomplete support decision input")
    steps = data.get("steps")
    if not isinstance(steps, list) or len(steps) != 5:
        fail("steps must contain 5 entries")
    for step in steps:
        if step.get("execution_allowed") is not False:
            fail(f"{step.get('step_id')} execution_allowed must be false")
        if step.get("human_action_required") is not True:
            fail(f"{step.get('step_id')} human_action_required must be true")

    for key in [
        "raw_values_recorded",
        "human_values_generated_by_codex",
        "quick_fill_values_entered_by_codex",
        "human_input_filled_by_codex",
        "validator_inputs_exported",
        "validators_run",
        "support_contact_configured",
        "support_contact_published",
        "support_contact_test_performed",
        "customer_facing_support_contact_configured",
        "customer_support_available",
        "production_support_available",
        "workbook_import_authorized",
        "workbook_import_performed",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "external_calls_made",
        "external_ai_assistant_tested",
        "production_ready_claim",
        "customer_validation_claim",
    ]:
        require_false(data, key)

    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 5:
        fail("CSV must contain 5 steps")
    for row in rows:
        if row.get("execution_allowed") != "False":
            fail("CSV execution_allowed must stay False")

    html = HTML.read_text(encoding="utf-8")
    html_required = [
        "<!doctype html>",
        "SAEE 支持入口人工填写",
        "支持入口仍未配置",
        "先指定负责人，再填写支持入口。",
        "不会生成联系人、不会发布支持入口、不会联系客户，也不会关闭阻塞项",
        "Codex 可代执行：false",
        "support_contact_configured: false",
        "support_contact_published: false",
        "blockers_closed_by_entrypoint: 0",
        "production_ready: false",
        "private_core_exposed: false",
    ]
    for token in html_required:
        if token not in html:
            fail(f"HTML missing token: {token}")
    html_forbidden = ["<script", "fetch(", "XMLHttpRequest", "http://", "https://", "mailto:"]
    found_html_forbidden = [token for token in html_forbidden if token in html]
    if found_html_forbidden:
        fail("HTML contains forbidden tokens: " + ", ".join(found_html_forbidden))

    text = REPORT.read_text(encoding="utf-8") + "\n" + html + "\n" + AUDIT.read_text(encoding="utf-8")
    required_tokens = [
        "support_contact_human_input_entrypoint_v0_1: true",
        "plain_language_support_contact_entry_v0_2: true",
        "plain_language_next_action: 先指定负责人，再人工填写支持入口信息。",
        "target_blocker_id: support_contact",
        "missing_first_owner_field_count: 5",
        "values_generated: false",
        "validator_inputs_exported: false",
        "validators_run: false",
        "support_contact_configured: false",
        "production_ready: false",
    ]
    for token in required_tokens:
        if token not in text:
            fail(f"missing token: {token}")
    forbidden = [
        "production_ready: true",
        "product_launched: true",
        "customer_validated: true",
        "private_core_exposed: true",
        "validator_inputs_exported: true",
        "validators_run: true",
        "support_contact_configured: true",
        "support_contact_published: true",
        "blocker_closure_authorized: true",
    ]
    found = [token for token in forbidden if token in text]
    if found:
        fail("forbidden true token found: " + ", ".join(found))

    print(
        "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_ENTRYPOINT_SMOKE: PASS "
        "status=ready_for_human_support_contact_input_navigation "
        "target_blocker_id=support_contact values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
