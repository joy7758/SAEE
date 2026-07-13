#!/usr/bin/env python3
"""Smoke check for Commercial Review Batch Template Preflight v0.1."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_review_batch_template_preflight.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_JSON = SPRINT_DIR / "commercial_review_batch_template_preflight.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_template_preflight.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_template_preflight.csv"
OUT_AUDIT = SPRINT_DIR / "commercial_review_batch_template_preflight_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_RECOMMENDATION_GATE.md"
SOURCE_TEMPLATE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_SMOKE: FAIL {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)

    for path in [RUNNER, OUT_JSON, OUT_MD, OUT_CSV, OUT_AUDIT, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_review_batch_template_preflight_v0_1": True,
        "preflight_type": "commercial_review_batch_template_preflight",
        "preflight_scope": "local_empty_template_structure_check_no_values_no_import_no_execution",
        "status": "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "template_row_count": 0,
        "expected_template_row_count": 10,
        "source_quick_fill_row_count": 64,
        "expected_source_quick_fill_row_count": 64,
        "required_column_count": 15,
        "missing_required_column_count": 0,
        "duplicate_id_count": 0,
        "blank_human_value_row_count": 0,
        "blank_notes_row_count": 0,
        "prefilled_human_value_row_count": 0,
        "prefilled_notes_row_count": 0,
        "row_preflight_pass_count": 0,
        "row_issue_count": 0,
        "boundary_violation_count": 0,
        "preflight_passed": False,
        "safe_to_start_human_fill": False,
        "template_preflight_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "human_input_required": False,
        "human_review_required": True,
        "blockers_closed_by_preflight": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(payload.get("boundary_violations") == [], "boundary_violations must be empty")

    false_flags = [
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
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")

    reports = payload.get("row_reports", [])
    require(isinstance(reports, list) and len(reports) == 0, "row_reports must be empty after template supersession")
    require(all(row.get("row_status") == "pass_blank_ready_for_human_entry" for row in reports), "all rows must pass blank preflight")

    with SOURCE_TEMPLATE_CSV.open(encoding="utf-8", newline="") as handle:
        template_rows = list(csv.DictReader(handle))
    require(len(template_rows) == 0, "source template must contain no data rows after supersession")
    require(all(not row.get("human_value_to_enter", "").strip() for row in template_rows), "source template values must remain blank")
    require(all(not row.get("notes_for_human", "").strip() for row in template_rows), "source template notes must remain blank")

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 0, "preflight CSV must contain no data rows after supersession")
    require(all(row.get("issue_count") == "0" for row in csv_rows), "preflight CSV issue_count must be 0")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_AUDIT, TOP_DOC, GATE])
    required_tokens = [
        "commercial_review_batch_template_preflight_v0_1: true",
        "status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "preflight_passed: false",
        "safe_to_start_human_fill: false",
        "template_preflight_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "blank_human_value_row_count: 0",
        "prefilled_human_value_row_count: 0",
        "blockers_closed_by_preflight: 0",
        "recommend_for_human_template_preflight: false",
        "recommend_for_value_generation_by_codex: false",
        "recommend_for_workbook_import_execution: false",
        "recommend_for_validator_execution_on_real_input: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT: PASS",
    ]
    for token in required_tokens:
        require(token in combined, "missing documentation token: " + token)

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "workbook_import_authorized: true",
        '"workbook_import_authorized": true',
        "validators_run_on_real_input: true",
        '"validators_run_on_real_input": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "execution_authorized: true",
        '"execution_authorized": true',
    ]
    found = [token for token in forbidden if token in combined or token in json.dumps(payload)]
    require(not found, "forbidden claim found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_review_batch_template_preflight.py",
        "/scripts/saee_commercial_review_batch_template_preflight_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing preflight paths: " + ", ".join(missing_llms))

    for required_file in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        require("commercial_review_batch_template_preflight_v0_1" in text, f"{required_file} missing preflight token")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    require("check-commercial-review-batch-template-preflight" in makefile, "Makefile missing preflight check target")
    require("scripts/saee_commercial_review_batch_template_preflight_smoke.py" in makefile, "Makefile missing preflight smoke")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_review_batch_template_preflight_v0_1", {})
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index preflight {key} must be {value!r}")
    for flag in false_flags:
        require(entry.get(flag) is False, f"agent-index preflight {flag} must be false")
    require(entry.get("make_target") == "make check-commercial-review-batch-template-preflight", "agent-index preflight make_target mismatch")

    print("SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_SMOKE: PASS")


if __name__ == "__main__":
    main()
