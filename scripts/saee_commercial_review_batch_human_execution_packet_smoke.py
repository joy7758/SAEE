#!/usr/bin/env python3
"""Smoke test for the commercial review-batch human execution packet."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

SUMMARY = SPRINT_DIR / "commercial_review_batch_human_execution_packet.local.json"
MARKDOWN = SPRINT_DIR / "commercial_review_batch_human_execution_packet.md"
CSV_PATH = SPRINT_DIR / "commercial_review_batch_human_execution_packet.csv"
HTML_PATH = SPRINT_DIR / "commercial_review_batch_human_execution_packet.html"
AUDIT = SPRINT_DIR / "commercial_review_batch_human_execution_packet_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_HUMAN_EXECUTION_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_EXECUTION_PACKET_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_EXECUTION_PACKET_SMOKE: FAIL {message}")


def require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    for path in [SUMMARY, MARKDOWN, CSV_PATH, HTML_PATH, AUDIT, TOP_DOC, GATE]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = {
        "commercial_review_batch_human_execution_packet_v0_1": True,
        "packet_type": "human_10_row_execution_packet",
        "status": "ready_for_human_10_row_entry",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "packet_row_count": 10,
        "expected_packet_row_count": 10,
        "blank_human_value_row_count": 10,
        "preferred_template_missing_value_row_count": 0,
        "full_quick_fill_missing_value_row_count": 0,
        "human_input_required": True,
        "human_review_required": True,
        "ready_for_human_fill": True,
        "boundary_violation_count": 0,
        "blockers_closed_by_packet": 0,
        "make_target": "make check-commercial-review-batch-human-execution-packet",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            fail(f"{key} must be {value!r}")

    for key in [
        "values_generated_by_codex",
        "human_values_filled_by_codex",
        "raw_values_recorded",
        "source_template_modified",
        "source_quick_fill_packet_modified",
        "local_quick_fill_output_written",
        "workbook_import_authorized",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "blockers_closed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "landing_page_modified",
        "private_core_exposed",
        "customer_contacted",
        "customer_validated",
        "product_launched",
        "production_ready",
        "production_ready_claim",
        "customer_validation_claim",
        "public_sdk_released",
        "external_calls_made",
    ]:
        require_false(data, key)

    rows = data.get("execution_rows")
    if not isinstance(rows, list) or len(rows) != 10:
        fail("execution_rows must contain 10 rows")
    required_keys = {
        "assigned_human_owner",
        "owner_contact_reference",
        "target_review_date",
        "owner_acknowledged_scope",
        "human_approval_reference",
        "human_reviewer_name",
        "review_date",
        "selected_support_contact_channel",
        "decision_summary",
        "abuse_handling_path_defined",
    }
    observed_keys = {row.get("input_key") for row in rows}
    if observed_keys != required_keys:
        fail("execution_rows input_key set changed")
    for row in rows:
        if row.get("human_value_to_enter") != "":
            fail(f"{row.get('review_batch_row_id')} human_value_to_enter must stay blank")
        if row.get("notes_for_human") != "":
            fail(f"{row.get('review_batch_row_id')} notes_for_human must stay blank")
        if row.get("codex_may_fill") is not False:
            fail(f"{row.get('review_batch_row_id')} codex_may_fill must be false")
        for key in ["plain_label", "plain_fill_guide", "plain_blank_guide"]:
            if not row.get(key):
                fail(f"{row.get('review_batch_row_id')} missing {key}")

    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 10:
        fail("execution CSV must contain 10 rows")
    for row in csv_rows:
        if row.get("human_value_to_enter", "") != "":
            fail("execution CSV human_value_to_enter must stay blank")
        if row.get("notes_for_human", "") != "":
            fail("execution CSV notes_for_human must stay blank")

    combined = "\n".join(
        [
            MARKDOWN.read_text(encoding="utf-8"),
            HTML_PATH.read_text(encoding="utf-8"),
            AUDIT.read_text(encoding="utf-8"),
            TOP_DOC.read_text(encoding="utf-8"),
            GATE.read_text(encoding="utf-8"),
        ]
    )
    required_text = [
        "SAEE 10 行人工执行包",
        "真正填写位置",
        "只填写两列",
        "human_value_to_enter",
        "notes_for_human",
        "填完后的本地检查顺序",
        "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py",
        "make check-commercial-review-batch-human-execution-packet",
        "不导入工作簿",
        "不要关闭 blocker",
        "不代表正式上线",
        "recommend_for_human_10_row_entry: true",
        "recommend_for_value_generation: false",
        "production_ready: false",
    ]
    missing = [token for token in required_text if token not in combined]
    if missing:
        fail("missing guidance tokens: " + ", ".join(missing))
    forbidden = [
        "production_ready: true",
        "\"production_ready\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "workbook_import_performed: true",
        "\"workbook_import_performed\": true",
        "validators_run_on_real_input: true",
        "\"validators_run_on_real_input\": true",
        "blocker_closure_authorized: true",
        "\"blocker_closure_authorized\": true",
    ]
    found = [token for token in forbidden if token in combined]
    if found:
        fail("forbidden true token found: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_EXECUTION_PACKET_SMOKE: PASS "
        "status=ready_for_human_10_row_entry packet_row_count=10 "
        "values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
