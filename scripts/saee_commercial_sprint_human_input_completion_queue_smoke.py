#!/usr/bin/env python3
"""Smoke check for commercial sprint human input completion queue."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.csv"
OUT_HTML = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.html"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_completion_queue_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    for script in [
        "scripts/saee_commercial_sprint_human_input_workbook.py",
        "scripts/saee_commercial_sprint_human_input_workbook_validator.py",
        "scripts/saee_commercial_sprint_human_input_transfer_map.py",
        "scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run.py",
        "scripts/saee_commercial_sprint_human_input_completion_queue.py",
    ]:
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_completion_queue_v0_1": True,
        "queue_type": "local_missing_human_input_completion_queue",
        "queue_scope": "missing_required_human_values_only_no_value_transfer",
        "status": "hold_human_input_required",
        "workbook_row_count": 65,
        "required_row_count": 64,
        "completed_required_row_count": 0,
        "missing_required_row_count": 64,
        "queue_item_count": 64,
        "source_completion_queue_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_completion_queue.html",
        "local_static_completion_queue_html": True,
        "browser_readable_completion_queue": True,
        "completion_queue_visual_palette": "commercial-clean-slate-mint-v1",
        "local_browser_completion_csv_builder": True,
        "browser_only_completion_csv_text_generation": True,
        "completion_csv_builder_writes_files": False,
        "completion_csv_builder_network_calls": False,
        "completion_csv_builder_imports_workbook": False,
        "grouped_by_blocker": True,
        "grouped_by_owner_review_lane": True,
        "target_template_count": 5,
        "all_pointers_resolved": True,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "human_input_required": True,
        "human_review_required": True,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_completion_queue": 0,
        "boundary_violation_count": 0,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "vendor_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "task_candidates_executed": False,
        "payment_collected": False,
        "revenue_validated": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must remain empty")
    rows = payload.get("queue_items", [])
    if len(rows) != 64:
        fail("queue_items must contain 64 missing required rows")
    if any(row.get("minimum_required") is not True for row in rows):
        fail("all queue items must be required rows")
    if any(row.get("human_value_present") is not False for row in rows):
        fail("queue items must not contain human values")
    if any(row.get("pointer_resolved") is not True for row in rows):
        fail("all queue items must have resolved pointers")
    if any(row.get("value_transferred") is not False for row in rows):
        fail("no values may be transferred")
    if any(row.get("template_written") is not False for row in rows):
        fail("no human-filled templates may be written")
    if payload.get("blocker_missing_counts") != {
        "formal_security_review": 12,
        "pricing_page": 14,
        "production_monitoring": 10,
        "production_restore_policy": 13,
        "support_contact": 15,
    }:
        fail("unexpected blocker_missing_counts")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 64:
        fail("CSV must contain 64 queue rows")

    required_tokens = [
        "commercial_sprint_human_input_completion_queue_v0_1: true",
        "status: hold_human_input_required",
        "queue_scope: missing_required_human_values_only_no_value_transfer",
        "missing_required_row_count: 64",
        "queue_item_count: 64",
        "source_completion_queue_html: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_completion_queue.html",
        "local_static_completion_queue_html: true",
        "browser_readable_completion_queue: true",
        "completion_queue_visual_palette: commercial-clean-slate-mint-v1",
        "local_browser_completion_csv_builder: true",
        "browser_only_completion_csv_text_generation: true",
        "completion_csv_builder_writes_files: false",
        "completion_csv_builder_network_calls: false",
        "completion_csv_builder_imports_workbook: false",
        "all_pointers_resolved: true",
        "ready_for_template_transfer: false",
        "human_input_filled_by_codex: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_completion_queue: 0",
        "production_ready: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")
    html = OUT_HTML.read_text(encoding="utf-8")
    for token in [
        "SAEE 商业化人工补证据队列",
        "暂停：等待人工补证据",
        "commercial_sprint_human_input_completion_queue_v0_1=true",
        "64 个待人工填写项",
        "生成 CSV 文本",
        "清空页面输入",
        "本地生成 CSV 文本",
        "不联网、不保存文件、不写入仓库、不导入 workbook",
        "按 blocker 看",
        "按负责人线看",
        "Codex 不填写任何人工值。",
        "不关闭 blocker，不声明生产可用。",
    ]:
        if token not in html:
            fail(f"HTML missing token {token}")
    if html.count("data-value-for=") != 64:
        fail("HTML must contain 64 human value textareas")
    if html.count("data-note-for=") != 64:
        fail("HTML must contain 64 human note textareas")
    for token in ["fetch(", "XMLHttpRequest", "localStorage", "http://", "https://"]:
        if token in html:
            fail(f"HTML must remain static and local-only: {token}")
    gate = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: recommend",
        "recommend_for_missing_input_coordination: true",
        "recommend_for_value_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        if token not in gate:
            fail(f"gate missing token {token}")

    runner = (
        ROOT / "scripts/saee_commercial_sprint_human_input_completion_queue.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE_SMOKE: PASS "
        f"status={payload['status']} "
        f"queue_item_count={payload['queue_item_count']} "
        f"missing_required_row_count={payload['missing_required_row_count']} "
        f"values_transferred={str(payload['values_transferred']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
