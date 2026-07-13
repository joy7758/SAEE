#!/usr/bin/env python3
"""Smoke test for the commercial review-batch human fill card."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SUMMARY = SPRINT_DIR / "commercial_review_batch_human_fill_card.local.json"
MARKDOWN = SPRINT_DIR / "commercial_review_batch_human_fill_card.md"
CSV_PATH = SPRINT_DIR / "commercial_review_batch_human_fill_card.csv"
HTML_PATH = SPRINT_DIR / "commercial_review_batch_human_fill_card.html"
AUDIT = SPRINT_DIR / "commercial_review_batch_human_fill_card_boundary_audit.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_FILL_CARD_SMOKE: FAIL {message}")


def require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    for path in [SUMMARY, MARKDOWN, CSV_PATH, HTML_PATH, AUDIT]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = {
        "commercial_review_batch_human_fill_card_v0_1": True,
        "status": "ready_for_human_fill_card_review",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "fill_card_row_count": 10,
        "expected_fill_card_row_count": 10,
        "blank_human_value_row_count": 10,
        "prefilled_human_value_row_count": 0,
        "blockers_closed_by_fill_card": 0,
        "human_input_required": True,
        "human_review_required": True,
        "ordinary_user_chinese_fill_guidance": True,
        "local_static_fill_companion_html": True,
        "local_static_execution_panel": True,
        "commercial_fill_card_visual_palette": "commercial-warm-graphite-sage-v1",
        "local_browser_manual_csv_builder": True,
        "browser_only_csv_text_generation": True,
        "manual_csv_builder_writes_files": False,
        "manual_csv_builder_network_calls": False,
        "manual_csv_builder_imports_workbook": False,
        "codex_generated_values": False,
        "human_must_fill_values": True,
        "boundary_violation_count": 0,
        "post_fill_commands_execute_external_calls": False,
        "post_fill_commands_import_workbook": False,
        "post_fill_commands_close_blockers": False,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            fail(f"{key} must be {value!r}")

    for key in [
        "raw_values_recorded",
        "human_values_generated_by_codex",
        "quick_fill_values_entered_by_codex",
        "human_input_filled_by_codex",
        "source_quick_fill_packet_modified",
        "batch_values_applied_to_source",
        "quick_fill_imported_to_workbook",
        "workbook_import_authorized",
        "workbook_import_performed",
        "workbook_written",
        "validators_run_on_real_input",
        "ready_for_safety_preflight",
        "ready_for_workbook_import",
        "safe_to_import_after_human_approval",
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

    rows = data.get("fill_card_rows")
    if not isinstance(rows, list) or len(rows) != 10:
        fail("fill_card_rows must contain 10 rows")
    for row in rows:
        if row.get("human_value_to_enter") != "":
            fail(f"{row.get('review_batch_row_id')} human_value_to_enter must stay blank")
        if row.get("notes_for_human") != "":
            fail(f"{row.get('review_batch_row_id')} notes_for_human must stay blank")
        if row.get("codex_may_fill") is not False:
            fail(f"{row.get('review_batch_row_id')} codex_may_fill must be false")
        for key in [
            "human_plain_label",
            "human_plain_instruction",
            "human_plain_leave_blank_condition",
        ]:
            if not row.get(key):
                fail(f"{row.get('review_batch_row_id')} {key} must be present")

    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 10:
        fail("CSV must contain 10 data rows")
    for row in csv_rows:
        if row.get("human_value_to_enter", "") != "":
            fail("CSV human_value_to_enter must stay blank")
        if row.get("notes_for_human", "") != "":
            fail("CSV notes_for_human must stay blank")

    text = "\n".join(
        [
            MARKDOWN.read_text(encoding="utf-8"),
            HTML_PATH.read_text(encoding="utf-8"),
            AUDIT.read_text(encoding="utf-8"),
        ]
    )
    required_text = [
        "给人看的操作说明",
        "只填写两列",
        "填完后的本地检查顺序",
        "填完后先跑这些本地检查",
        "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py",
        "python3 scripts/mainline_guard.py",
        "不导入工作簿",
        "不要关闭 blocker",
        "真正填写位置",
        "本地生成 CSV 文本",
        "生成 CSV 文本",
        "清空页面输入",
        "它不联网、不保存文件、不写入仓库、不导入工作簿",
        "local_browser_manual_csv_builder: true",
        "browser_only_csv_text_generation: true",
        "manual_csv_builder_writes_files: false",
        "manual_csv_builder_network_calls: false",
        "manual_csv_builder_imports_workbook: false",
        "commercial-warm-graphite-sage-v1",
        "先把这 10 行填清楚",
        "谁负责确认这个支持入口",
        "以后客户从哪里联系支持",
        "滥用或异常请求由谁处理",
    ]
    missing_text = [token for token in required_text if token not in text]
    if missing_text:
        fail("missing plain Chinese guidance tokens: " + ", ".join(missing_text))
    forbidden = [
        "production_ready: true",
        "product_launched: true",
        "customer_validated: true",
        "private_core_exposed: true",
        "workbook_import_performed: true",
        "validators_run_on_real_input: true",
        "blocker_closure_authorized: true",
        "#2563eb",
        "#1d4ed8",
        "#eaf1ff",
        "fetch(",
        "XMLHttpRequest",
        "localStorage",
    ]
    found = [token for token in forbidden if token in text]
    if found:
        fail("forbidden true token found: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_FILL_CARD_SMOKE: PASS "
        "status=ready_for_human_fill_card_review fill_card_row_count=10 "
        "values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
