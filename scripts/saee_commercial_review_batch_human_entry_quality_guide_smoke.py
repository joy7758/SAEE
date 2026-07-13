#!/usr/bin/env python3
"""Smoke test for the commercial review-batch human entry quality guide."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SUMMARY = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.local.json"
MARKDOWN = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.md"
CSV_PATH = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.csv"
HTML_PATH = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.html"
AUDIT = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_BATCH_HUMAN_ENTRY_QUALITY_GUIDE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_ENTRY_QUALITY_GUIDE_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_ENTRY_QUALITY_GUIDE_SMOKE: FAIL {message}")


def require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    for path in [SUMMARY, MARKDOWN, CSV_PATH, HTML_PATH, AUDIT, TOP_DOC, GATE]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = {
        "commercial_review_batch_human_entry_quality_guide_v0_1": True,
        "status": "ready_for_human_entry_quality_review",
        "guide_row_count": 10,
        "expected_guide_row_count": 10,
        "target_blocker_id": "support_contact",
        "human_required": True,
        "human_review_required": True,
        "quality_guide_only": True,
        "field_level_quality_rules": True,
        "placeholder_examples_only": True,
        "boundary_violation_count": 0,
        "blockers_closed_by_quality_guide": 0,
    }
    for key, expected_value in expected.items():
        if data.get(key) != expected_value:
            fail(f"{key} must be {expected_value!r}")

    for key in [
        "human_values_generated_by_codex",
        "human_input_filled_by_codex",
        "raw_values_recorded",
        "source_quick_fill_packet_modified",
        "quick_fill_imported_to_workbook",
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
        "production_ready",
        "customer_validated",
        "product_launched",
        "customer_contacted",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "production_ready_claim",
        "customer_validation_claim",
    ]:
        require_false(data, key)

    rows = data.get("guidance_rows")
    if not isinstance(rows, list) or len(rows) != 10:
        fail("guidance_rows must contain 10 rows")
    required_row_fields = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "expected_value_shape",
        "target_json_pointer",
        "quality_rule",
        "accepted_value_shape",
        "reject_if",
        "example_placeholder",
        "privacy_note",
        "human_required",
    ]
    for row in rows:
        for field in required_row_fields:
            if field not in row or row.get(field) in ("", None):
                fail(f"{row.get('review_batch_row_id')} missing {field}")
        if row.get("human_required") is not True:
            fail(f"{row.get('review_batch_row_id')} human_required must be true")
        if row.get("codex_may_fill") is not False:
            fail(f"{row.get('review_batch_row_id')} codex_may_fill must be false")
        if not str(row.get("example_placeholder", "")).startswith("EXAMPLE_ONLY:"):
            fail(f"{row.get('review_batch_row_id')} example must be placeholder-only")

    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 10:
        fail("CSV must contain 10 data rows")
    for field in required_row_fields:
        if field not in csv_rows[0]:
            fail(f"CSV missing {field}")

    html_text = HTML_PATH.read_text(encoding="utf-8")
    forbidden_html = ["<script", "fetch(", "XMLHttpRequest", "mailto:", "http://", "https://"]
    found_html = [token for token in forbidden_html if token in html_text]
    if found_html:
        fail("HTML must remain static and local-only; found " + ", ".join(found_html))

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
        "This file explains what counts as a safe human-entered value",
        "EXAMPLE_ONLY: YYYY-MM-DD",
        "Reject vague dates such as soon, later",
        "Reject production-ready, customer-validated, launched",
        "不代填证据值",
        "不导入工作簿",
        "不关闭 blocker",
        "不联系客户，不发布产品，不声明生产可用",
        "separate approval request",
        "python3 scripts/saee_commercial_review_batch_template_preflight.py",
        "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py",
    ]
    missing = [token for token in required_text if token not in combined]
    if missing:
        fail("missing required guidance tokens: " + ", ".join(missing))

    forbidden_true = [
        "production_ready: true",
        "product_launched: true",
        "customer_validated: true",
        "private_core_exposed: true",
        "workbook_import_authorized: true",
        "validators_run_on_real_input: true",
        "evidence_collection_authorized: true",
        "blocker_closure_authorized: true",
        "human_values_generated_by_codex: true",
        "human_input_filled_by_codex: true",
    ]
    found_true = [token for token in forbidden_true if token in combined]
    if found_true:
        fail("forbidden true claim found: " + ", ".join(found_true))

    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_ENTRY_QUALITY_GUIDE_SMOKE: PASS "
        "status=ready_for_human_entry_quality_review guide_row_count=10 "
        "values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
