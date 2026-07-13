#!/usr/bin/env python3
"""Smoke check for the review-batch input-template importer."""

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
    / "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py"
)
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.local.json"
)
OUT_MD = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.md"
)
OUT_CSV = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.csv"
)
OUT_BOUNDARY = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER_RECOMMENDATION_GATE.md"
)
INPUT_TEMPLATE_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
SOURCE_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
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


def assert_default_payload(payload: dict) -> None:
    expected = {
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1": True,
        "importer_type": "review_batch_input_template_to_local_quick_fill_output_importer",
        "importer_scope": "template_to_local_quick_fill_output_only_no_source_overwrite_no_workbook_import",
        "status": SUPERSEDED_STATUS,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "execution_mode": "dry_run_no_write",
        "template_row_count": 0,
        "source_quick_fill_row_count": 64,
        "expected_template_row_count": 10,
        "expected_source_quick_fill_row_count": 64,
        "mapping_resolved_row_count": 0,
        "template_value_present_row_count": 0,
        "missing_template_value_row_count": 0,
        "review_batch_template_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "would_import_row_count": 0,
        "row_boundary_issue_count": 0,
        "all_template_values_ready": False,
        "apply_requested": False,
        "human_template_import_confirmation_provided": False,
        "apply_preconditions_met": False,
        "apply_performed": False,
        "local_quick_fill_output_written": False,
        "batch_values_written_to_local_output": False,
        "local_output_ready_for_review_batch_validator": False,
        "source_quick_fill_packet_modified": False,
        "batch_values_applied_to_source": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blockers_closed_by_importer": 0,
        "boundary_violation_count": 0,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "raw_values_recorded_in_status_artifacts": False,
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
    require(len(payload.get("import_rows", [])) == 0, "import rows must be empty after supersession")
    require(
        all(not row.get("human_template_value_present") for row in payload["import_rows"]),
        "default import rows must not contain human values",
    )


def assert_official_source_not_imported() -> None:
    _, rows = read_csv(SOURCE_QUICK_FILL_CSV)
    require(len(rows) == 64, "source quick-fill CSV must contain 64 rows")
    require(
        all(row.get("value_imported_to_workbook") == "False" for row in rows),
        "source quick-fill CSV must not be imported to workbook",
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
            row["human_value_to_enter"] = (
                f"Human-approved review artifact REF-{index:03d} dated 2026-07-06."
            )
            row["notes_for_human"] = "Manual fixture value for local importer smoke only."
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


def main() -> int:
    run_runner()
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing importer file: {path}")
    payload = read_json(OUT_JSON)
    assert_default_payload(payload)
    assert_official_source_not_imported()

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE])
    required_tokens = [
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1: true",
        f"status: {SUPERSEDED_STATUS}",
        "execution_mode: dry_run_no_write",
        "importer_scope: template_to_local_quick_fill_output_only_no_source_overwrite_no_workbook_import",
        "template_row_count: 0",
        "source_quick_fill_row_count: 64",
        "template_value_present_row_count: 0",
        "missing_template_value_row_count: 0",
        "review_batch_template_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "would_import_row_count: 0",
        "apply_performed: false",
        "local_quick_fill_output_written: false",
        "source_quick_fill_packet_modified: false",
        "batch_values_applied_to_source: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
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
    require(not found, "importer runner suggests external/process access: " + ", ".join(found))

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        safe_template = tmpdir / "safe_template.csv"
        clean_source = tmpdir / "clean_quick_fill_source.csv"
        safe_output = tmpdir / "safe_quick_fill_output.csv"
        build_fixture_template(safe_template)
        build_clean_fixture_source(clean_source)

        run_runner(
            "--input-template-csv",
            str(safe_template),
            "--quick-fill-csv",
            str(clean_source),
            "--output-quick-fill-csv",
            str(safe_output),
        )
        dry_payload = read_json(OUT_JSON)
        require(
            dry_payload["status"] == "ready_for_local_quick_fill_output_pending_explicit_human_command",
            "safe dry-run should be ready for explicit command",
        )
        require(dry_payload["template_value_present_row_count"] == 10, "safe dry-run must see 10 values")
        require(dry_payload["would_import_row_count"] == 10, "safe dry-run must identify 10 importable rows")
        require(dry_payload["local_quick_fill_output_written"] is False, "safe dry-run must not write output")
        require(not safe_output.exists(), "safe dry-run must not create output CSV")

        run_runner(
            "--input-template-csv",
            str(safe_template),
            "--quick-fill-csv",
            str(clean_source),
            "--output-quick-fill-csv",
            str(safe_output),
            "--apply",
            "--confirm-human-approved-template-import",
        )
        apply_payload = read_json(OUT_JSON)
        require(apply_payload["apply_performed"] is True, "safe apply must be performed")
        require(apply_payload["local_quick_fill_output_written"] is True, "safe apply must write local output")
        require(apply_payload["source_quick_fill_packet_modified"] is False, "safe apply must not modify source")
        require(safe_output.exists(), "safe apply must create local output CSV")
        _, output_rows = read_csv(safe_output)
        require(len(output_rows) == 64, "safe output quick-fill must contain 64 rows")
        require(
            sum(1 for row in output_rows if row.get("human_value_to_enter", "").strip()) == 10,
            "safe output quick-fill must contain 10 imported values",
        )
        assert_official_source_not_imported()

        unsafe_template = tmpdir / "unsafe_template.csv"
        unsafe_output = tmpdir / "unsafe_output.csv"
        build_fixture_template(unsafe_template, unsafe=True)
        run_runner(
            "--input-template-csv",
            str(unsafe_template),
            "--quick-fill-csv",
            str(clean_source),
            "--output-quick-fill-csv",
            str(unsafe_output),
        )
        unsafe_payload = read_json(OUT_JSON)
        require(
            unsafe_payload["status"] == "stop_boundary_or_apply_precondition_violation",
            "unsafe dry-run must stop",
        )
        require(unsafe_payload["row_boundary_issue_count"] == 1, "unsafe dry-run must detect one boundary issue")
        require(not unsafe_output.exists(), "unsafe dry-run must not create output CSV")

    run_runner()
    payload = read_json(OUT_JSON)
    assert_default_payload(payload)
    assert_official_source_not_imported()

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms.txt missing importer paths: " + ", ".join(missing))

    for required_file in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        require(
            "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1"
            in text,
            f"{required_file} missing importer token",
        )

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    require(
        "check-commercial-sprint-human-input-quick-fill-review-batch-input-template-importer"
        in makefile,
        "Makefile missing importer check target",
    )
    require(
        "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_smoke.py"
        in makefile,
        "Makefile missing importer smoke",
    )

    index = read_json(ROOT / "agent-index.json")
    entry = index.get(
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1",
        {},
    )
    for key, value in {
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1": True,
        "status": SUPERSEDED_STATUS,
        "execution_mode": "dry_run_no_write",
        "template_row_count": 0,
        "source_quick_fill_row_count": 64,
        "template_value_present_row_count": 0,
        "missing_template_value_row_count": 0,
        "review_batch_template_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "would_import_row_count": 0,
        "apply_performed": False,
        "local_quick_fill_output_written": False,
        "source_quick_fill_packet_modified": False,
        "batch_values_applied_to_source": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index importer {key} must be {value}")

    print("SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
