#!/usr/bin/env python3
"""Smoke test for the commercial review batch post-fill readiness preview."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

OUT_JSON = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.csv"
OUT_HTML = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.html"
OUT_AUDIT = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_POST_FILL_READINESS_PREVIEW_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_READINESS_PREVIEW_RECOMMENDATION_GATE.md"
)
SOURCE_TEMPLATE = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_READINESS_PREVIEW_SMOKE: FAIL: "
        + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_review_batch_post_fill_readiness_preview.py"],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_AUDIT, TOP_DOC, GATE, SOURCE_TEMPLATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    with SOURCE_TEMPLATE.open("r", encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        preview_csv_rows = list(csv.DictReader(handle))

    require(
        payload["commercial_review_batch_post_fill_readiness_preview_v0_1"] is True,
        "marker false",
    )
    require(
        payload["preview_type"] == "read_only_10_row_post_fill_readiness_preview",
        "wrong preview type",
    )
    require(
        payload["status"] == "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "current status should show superseded route",
    )
    require(payload["review_batch_row_count"] == 0, "row count should be zero after supersession")
    require(payload["filled_human_value_row_count"] == 0, "current template should remain blank")
    require(payload["missing_human_value_row_count"] == 0, "superseded template should have no missing rows")
    require(payload["human_input_required"] is False, "human input should not be required for superseded template")
    require(payload["post_fill_check_ready"] is False, "post-fill check must not be ready")
    require(payload["review_batch_route_superseded"] is True, "route should be marked superseded")
    require(payload["ready_for_workbook_import_approval_review"] is True, "should point to workbook import approval review")
    require(payload["post_fill_check_executed"] is False, "post-fill check must not execute")
    require(payload["post_fill_e2e_dry_run_executed"] is False, "e2e dry run must not execute")
    require(payload["blockers_closed_by_preview"] == 0, "blockers closed")
    require(len(payload["rows"]) == 0, "preview rows should be empty after supersession")
    require(len(preview_csv_rows) == 0, "preview CSV rows should be empty after supersession")

    for row in source_rows:
        require(row.get("human_value_to_enter", "") == "", "source template value was filled")
        require(row.get("notes_for_human", "") == "", "source template notes were filled")

    forbidden_row_keys = {"human_value_to_enter", "notes_for_human", "fill_instruction", "leave_blank_condition"}
    for row in payload["rows"]:
        require(not forbidden_row_keys.intersection(row), "preview row exposes raw-entry columns")
        require(row["value_present"] is False, "current row should not have value")
        require(row["notes_present"] is False, "current row should not have notes")
        require(row["row_status"] == "missing_human_value", "current row status should be missing")

    for row in preview_csv_rows:
        for forbidden in forbidden_row_keys:
            require(forbidden not in row, "preview CSV exposes raw-entry columns")

    false_flags = [
        "raw_values_recorded",
        "raw_notes_recorded",
        "human_values_generated_by_codex",
        "codex_prefill_performed",
        "source_template_modified",
        "source_quick_fill_packet_modified",
        "workbook_import_authorized",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "customer_contacted",
        "customer_validated",
        "product_launched",
        "production_ready",
        "production_ready_claim",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_HTML, OUT_AUDIT, TOP_DOC, GATE]
    )
    required_tokens = [
        "SAEE 10 行填后就绪预览",
        "commercial_review_batch_post_fill_readiness_preview_v0_1: true",
        "status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "read-only local commercial-readiness guidance",
        "10 行填写路径已经被完整 quick-fill 值替代",
        "review_batch_route_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "不展示、不保存、不生成任何人工填写的原文",
        "raw_values_recorded: false",
        "raw_notes_recorded: false",
        "human_values_generated_by_codex: false",
        "codex_prefill_performed: false",
        "workbook_import_authorized: false",
        "validators_run_on_real_input: false",
        "blockers_closed_by_preview: 0",
        "production_ready: false",
        "recommend_for_read_only_presence_preview: true",
        "recommend_for_codex_prefill: false",
    ]
    for token in required_tokens:
        require(token in combined, f"missing token {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "workbook_import_authorized: true",
        '"workbook_import_authorized": true',
        "validators_run_on_real_input: true",
        '"validators_run_on_real_input": true',
        "recommend_for_codex_prefill: true",
        "recommend_for_workbook_import: true",
        "recommend_for_blocker_closure: true",
    ]
    for token in forbidden_tokens:
        require(token not in combined, f"forbidden token in docs {token}")
        require(token not in json.dumps(payload), f"forbidden token in payload {token}")

    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_READINESS_PREVIEW_SMOKE: PASS "
        f"status={payload['status']} "
        f"missing={payload['missing_human_value_row_count']} "
        "raw_values_recorded=false production_ready=false"
    )


if __name__ == "__main__":
    main()
