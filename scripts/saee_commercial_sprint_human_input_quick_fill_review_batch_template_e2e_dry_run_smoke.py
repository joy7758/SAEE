#!/usr/bin/env python3
"""Smoke check for the review-batch template E2E dry run."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = (
    ROOT
    / "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py"
)
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json"
)
OUT_MD = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.md"
)
OUT_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.csv"
)
OUT_BOUNDARY = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN_RECOMMENDATION_GATE.md"
)
INPUT_TEMPLATE_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
SOURCE_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
DEFAULT_LOCAL_OUTPUT = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_packet.imported_from_review_batch_template.local.csv"
)
SUPERSEDED_STATUS = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_runner(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def build_fixture_template(path: Path, unsafe: bool = False) -> None:
    fields, _ = read_csv(INPUT_TEMPLATE_CSV)
    _, source_rows = read_csv(SOURCE_QUICK_FILL_CSV)
    rows: list[dict[str, str]] = []
    for index, source_row in enumerate(source_rows[:10], start=1):
        row = {field: "" for field in fields}
        row["review_batch_row_id"] = f"QFRB-{index:03d}"
        for field in [
            "quick_fill_row_id",
            "queue_item_id",
            "workbook_row_id",
            "blocker_id",
            "owner_review_lane",
            "input_group",
            "input_key",
            "input_kind",
            "target_json_pointer",
        ]:
            row[field] = source_row.get(field, "")
        row["expected_value_shape"] = "fixture value"
        if unsafe and index == 1:
            row["human_value_to_enter"] = "production_ready=true"
            row["notes_for_human"] = "Unsafe boundary fixture."
        else:
            value = f"Human-approved review artifact REF-{index:03d} dated 2026-07-06."
            if row["input_key"] == "target_review_date":
                value = "2026-07-06"
            row["human_value_to_enter"] = value
            row["notes_for_human"] = "Manual fixture value for local E2E dry-run smoke only."
        rows.append(row)
    write_csv(path, fields, rows)


def build_clean_fixture_source(path: Path) -> None:
    fields, rows = read_csv(SOURCE_QUICK_FILL_CSV)
    clean_rows = [dict(row) for row in rows]
    for row in clean_rows:
        row["human_value_to_enter"] = ""
        row["notes_for_human"] = ""
        row["quick_fill_status"] = "blank_pending_human_input"
        row["value_imported_to_workbook"] = "False"
        row["value_transferred"] = "False"
        row["template_written"] = "False"
    write_csv(path, fields, clean_rows)


def assert_official_source_not_imported() -> None:
    _, rows = read_csv(SOURCE_QUICK_FILL_CSV)
    require(len(rows) == 64, "source quick-fill CSV must contain 64 rows")
    require(
        all(row.get("value_imported_to_workbook") == "False" for row in rows),
        "source quick-fill CSV must not be imported to workbook",
    )
    if DEFAULT_LOCAL_OUTPUT.exists():
        _, local_rows = read_csv(DEFAULT_LOCAL_OUTPUT)
        require(len(local_rows) == 64, "default local output must contain 64 rows when present")
        require(
            sum(1 for row in local_rows if row.get("human_value_to_enter", "").strip()) == 10,
            "default local output must contain exactly 10 human-entered values when present",
        )


def assert_default_payload(payload: dict) -> None:
    expected = {
        "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1": True,
        "dry_run_type": "review_batch_template_to_preview_quick_fill_to_batch_validator",
        "dry_run_scope": "local_preview_only_no_source_overwrite_no_persistent_output_no_workbook_import",
        "status": SUPERSEDED_STATUS,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "template_row_count": 0,
        "source_quick_fill_row_count": 64,
        "template_value_present_row_count": 0,
        "missing_template_value_row_count": 0,
        "review_batch_template_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "would_import_row_count": 0,
        "importer_status": SUPERSEDED_STATUS,
        "importer_apply_performed": False,
        "preview_validator_executed": False,
        "preview_validator_status": "not_run_template_route_superseded",
        "preview_validator_passed": False,
        "preview_validator_completed_batch_value_row_count": 0,
        "preview_validator_missing_batch_value_row_count": 0,
        "source_quick_fill_packet_modified": False,
        "persistent_preview_quick_fill_written": False,
        "local_quick_fill_output_written": False,
        "batch_values_applied_to_source": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "validators_run_on_official_real_input": False,
        "raw_values_recorded_in_status_artifacts": False,
        "human_values_generated_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blockers_closed_by_dry_run": 0,
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
        "external_calls_made": False,
        "external_ai_assistant_tested": False,
        "production_ready_claim": False,
        "customer_validation_claim": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")
    require(payload.get("row_summaries", []) == [], "row summaries must be empty after supersession")


def main() -> int:
    run_runner()
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing E2E dry-run file: {path}")
    payload = read_json(OUT_JSON)
    assert_default_payload(payload)
    assert_official_source_not_imported()

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE])
    required_tokens = [
        "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1: true",
        f"status: {SUPERSEDED_STATUS}",
        "dry_run_scope: local_preview_only_no_source_overwrite_no_persistent_output_no_workbook_import",
        "template_row_count: 0",
        "source_quick_fill_row_count: 64",
        "template_value_present_row_count: 0",
        "missing_template_value_row_count: 0",
        "review_batch_template_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "would_import_row_count: 0",
        "importer_apply_performed: false",
        "preview_validator_executed: false",
        "preview_validator_status: not_run_template_route_superseded",
        "source_quick_fill_packet_modified: false",
        "persistent_preview_quick_fill_written: false",
        "local_quick_fill_output_written: false",
        "batch_values_applied_to_source: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "validators_run_on_official_real_input: false",
        "raw_values_recorded_in_status_artifacts: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_dry_run: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    for token in required_tokens:
        require(token in combined, "missing documentation token: " + token)

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]
    found = [token for token in forbidden_runner_tokens if token in runner_text]
    require(not found, "E2E dry-run runner suggests external/process access: " + ", ".join(found))

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        safe_template = tmpdir / "safe_template.csv"
        clean_source = tmpdir / "clean_quick_fill_source.csv"
        build_clean_fixture_source(clean_source)
        build_fixture_template(safe_template)
        run_runner("--input-template-csv", str(safe_template), "--quick-fill-csv", str(clean_source))
        safe_payload = read_json(OUT_JSON)
        require(
            safe_payload["status"] == "hold_template_values_need_batch_quality_review",
            "safe E2E dry-run should hold because downstream batch validation route is superseded",
        )
        require(safe_payload["template_value_present_row_count"] == 10, "safe dry-run must see 10 values")
        require(safe_payload["would_import_row_count"] == 10, "safe dry-run must identify 10 importable rows")
        require(safe_payload["preview_validator_executed"] is True, "safe dry-run must execute preview validator")
        require(
            safe_payload["preview_validator_status"] == SUPERSEDED_STATUS,
            "safe dry-run preview validator should report superseded route",
        )
        require(safe_payload["preview_validator_passed"] is False, "superseded preview validator must not pass")
        require(
            safe_payload["preview_validator_completed_batch_value_row_count"] == 0,
            "superseded preview validator should not validate batch values",
        )
        require(safe_payload["local_quick_fill_output_written"] is False, "safe dry-run must not persist output")
        assert_official_source_not_imported()

        unsafe_template = tmpdir / "unsafe_template.csv"
        build_fixture_template(unsafe_template, unsafe=True)
        run_runner("--input-template-csv", str(unsafe_template), "--quick-fill-csv", str(clean_source), check=False)
        unsafe_payload = read_json(OUT_JSON)
        require(
            unsafe_payload["status"] == "stop_template_e2e_boundary_or_validator_issue",
            "unsafe E2E dry-run must stop",
        )
        require(unsafe_payload["boundary_violation_count"] > 0, "unsafe dry-run must detect boundary issue")
        require(unsafe_payload["local_quick_fill_output_written"] is False, "unsafe dry-run must not persist output")
        assert_official_source_not_imported()

    run_runner()
    payload = read_json(OUT_JSON)
    assert_default_payload(payload)
    assert_official_source_not_imported()

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms.txt missing E2E dry-run paths: " + ", ".join(missing))

    for required_file in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        require(
            "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1"
            in text,
            f"{required_file} missing E2E dry-run token",
        )

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    require(
        "check-commercial-sprint-human-input-quick-fill-review-batch-template-e2e-dry-run"
        in makefile,
        "Makefile missing E2E dry-run check target",
    )
    require(
        "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_smoke.py"
        in makefile,
        "Makefile missing E2E dry-run smoke",
    )

    index = read_json(ROOT / "agent-index.json")
    entry = index.get(
        "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1",
        {},
    )
    for key, value in {
        "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1": True,
        "status": SUPERSEDED_STATUS,
        "template_row_count": 0,
        "source_quick_fill_row_count": 64,
        "template_value_present_row_count": 0,
        "missing_template_value_row_count": 0,
        "review_batch_template_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "would_import_row_count": 0,
        "preview_validator_executed": False,
        "preview_validator_passed": False,
        "source_quick_fill_packet_modified": False,
        "persistent_preview_quick_fill_written": False,
        "local_quick_fill_output_written": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "validators_run_on_official_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index E2E dry-run {key} must be {value}")

    print("SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
