#!/usr/bin/env python3
"""Smoke check for the ERD approval completion helper."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_evidence_request_approval_completion_helper import (
    COMPLETION_CSV_PATH,
    CSV_FIELDS,
    GATE_PATH,
    GUIDE_PATH,
    STATUS_JSON_PATH,
    STATUS_MD_PATH,
    TOP_DOC_PATH,
)
from scripts.saee_commercial_evidence_request_approval_input_validator import (
    build_validation,
)


HELPER_SCRIPT = (
    ROOT / "scripts/saee_commercial_evidence_request_approval_completion_helper.py"
)
SMOKE_PASS_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER_SMOKE: PASS"
)
SMOKE_FAIL_PREFIX = (
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER_SMOKE: FAIL "
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(SMOKE_FAIL_PREFIX + message)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == CSV_FIELDS, "completion CSV header mismatch")
        return list(reader)


def write_filled_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for index, row in enumerate(rows):
            filled = dict(row)
            if index == 0:
                filled["assigned_human_owner"] = "Fixture Owner"
                filled["human_approval_reference"] = "fixture-human-approval-reference"
                filled["approval_scope"] = "evidence_collection_only"
                filled["approval_decision"] = (
                    "approved_for_separate_evidence_collection_request"
                )
                filled["evidence_collection_request_reference"] = (
                    "fixture-separate-evidence-request"
                )
                filled["execution_request_reference"] = ""
                filled["owner_acknowledged_scope"] = "true"
                filled["boundary_acknowledged"] = "true"
                filled["notes"] = "fixture conversion check only"
            writer.writerow(filled)


def main() -> int:
    require(HELPER_SCRIPT.is_file(), "helper script missing")
    default_run = subprocess.run(
        [sys.executable, str(HELPER_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_status = json.loads(default_run.stdout)
    expected_default = {
        "helper_type": "saee_commercial_evidence_request_approval_completion_helper",
        "helper_version": "v0.1",
        "status": "hold_human_approval_input_required",
        "completion_sheet_ready": True,
        "selected_blocker_count": 5,
        "approval_row_count": 5,
        "human_approval_input_required": True,
        "approved_request_count": 0,
        "approval_input_complete": False,
        "ready_for_validator": False,
        "ready_for_separate_evidence_collection_request": False,
        "ready_for_separate_execution_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "blockers_closed_by_helper": 0,
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
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "owner_contacted_by_codex": False,
        "vendor_contacted": False,
    }
    for key, value in expected_default.items():
        require(default_status.get(key) == value, f"default {key} must be {value}")

    for path in [
        COMPLETION_CSV_PATH,
        STATUS_JSON_PATH,
        STATUS_MD_PATH,
        GUIDE_PATH,
        TOP_DOC_PATH,
        GATE_PATH,
    ]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    rows = read_csv_rows(COMPLETION_CSV_PATH)
    require(len(rows) == 5, "completion CSV must contain 5 rows")
    require(
        [row["request_id"] for row in rows]
        == ["ERD-001", "ERD-002", "ERD-003", "ERD-004", "ERD-005"],
        "completion CSV request order mismatch",
    )
    for row in rows:
        for field in [
            "assigned_human_owner",
            "human_approval_reference",
            "approval_scope",
            "evidence_collection_request_reference",
            "execution_request_reference",
            "notes",
        ]:
            require(row[field] == "", f"completion CSV {field} must default blank")
        require(row["approval_decision"] == "hold", "approval_decision must default hold")
        require(
            row["owner_acknowledged_scope"].lower() in {"false", ""},
            "owner_acknowledged_scope must default false or blank",
        )
        require(
            row["boundary_acknowledged"].lower() in {"false", ""},
            "boundary_acknowledged must default false or blank",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        filled_csv = tmp / "filled_evidence_request_approval_input.csv"
        imported_json = tmp / "evidence_request_approval_input.human_filled.local.json"
        write_filled_csv(filled_csv, rows)
        subprocess.run(
            [
                sys.executable,
                str(HELPER_SCRIPT),
                "--import-csv",
                str(filled_csv),
                "--output-input-json",
                str(imported_json),
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        require(imported_json.is_file(), "imported approval input JSON missing")
        imported = json.loads(imported_json.read_text(encoding="utf-8"))
        require(
            imported.get("input_status") == "human_filled_local_import",
            "imported input status mismatch",
        )
        validation = build_validation(imported_json)
        require(validation["status"] == "pass", "imported complete fixture must pass validator")
        require(validation["approval_input_complete"] is True, "imported fixture must be complete")
        require(validation["approved_request_count"] == 1, "imported fixture must approve one request")
        require(
            validation["ready_for_separate_evidence_collection_request"] is True,
            "imported fixture must be ready for separate evidence request",
        )
        require(
            validation["ready_for_separate_execution_request"] is False,
            "imported fixture must not be ready for execution request",
        )
        for key in [
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
            "external_model_api_called",
            "external_ai_assistant_tested",
            "task_candidates_executed",
            "development_permission_granted",
            "execution_authorized",
            "evidence_collection_authorized",
            "owner_contacted_by_codex",
            "vendor_contacted",
        ]:
            require(validation[key] is False, f"validator {key} must remain false")
        require(validation["blockers_closed_by_validator"] == 0, "validator closes no blockers")

        single_json = tmp / "evidence_request_approval_input.single.local.json"
        single_run = subprocess.run(
            [
                sys.executable,
                str(HELPER_SCRIPT),
                "--single-request-id",
                "ERD-001",
                "--assigned-human-owner",
                "Fixture Owner",
                "--human-approval-reference",
                "fixture-human-approval-reference",
                "--approval-decision",
                "approved_for_separate_evidence_collection_request",
                "--approval-scope",
                "evidence_collection_only",
                "--evidence-collection-request-reference",
                "fixture-separate-evidence-request",
                "--single-request-notes",
                "fixture single-request generation check only",
                "--output-input-json",
                str(single_json),
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        single_status = json.loads(single_run.stdout)
        require(single_json.is_file(), "single-request approval input JSON missing")
        require(
            single_status.get("single_request_input_generator_used") is True,
            "single-request generator flag must be true in temp status",
        )
        require(
            single_status.get("ready_for_validator") is True,
            "single-request generator output must be ready for validator",
        )
        single_imported = json.loads(single_json.read_text(encoding="utf-8"))
        require(
            single_imported.get("input_status")
            == "human_filled_single_request_local_input",
            "single-request input status mismatch",
        )
        single_validation = build_validation(single_json)
        require(
            single_validation["status"] == "pass",
            "single-request complete fixture must pass validator",
        )
        require(
            single_validation["approved_request_count"] == 1,
            "single-request fixture must approve one request",
        )
        require(
            single_validation["ready_for_separate_evidence_collection_request"] is True,
            "single-request fixture must be ready for separate evidence request",
        )
        require(
            single_validation["ready_for_separate_execution_request"] is False,
            "single-request fixture must not be ready for execution request",
        )
        for key in [
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
            "external_model_api_called",
            "external_ai_assistant_tested",
            "task_candidates_executed",
            "development_permission_granted",
            "execution_authorized",
            "evidence_collection_authorized",
            "owner_contacted_by_codex",
            "vendor_contacted",
        ]:
            require(
                single_validation[key] is False,
                f"single validator {key} must remain false",
            )
        require(
            single_validation["blockers_closed_by_validator"] == 0,
            "single validator closes no blockers",
        )

    subprocess.run(
        [sys.executable, str(HELPER_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [GUIDE_PATH, STATUS_MD_PATH, TOP_DOC_PATH, GATE_PATH]
    )
    for token in [
        "commercial_evidence_request_approval_completion_helper_v0_1: true",
        "status: hold_human_approval_input_required",
        "helper_scope: local_evidence_request_approval_completion_sheet_and_import_helper",
        "completion_sheet_ready: true",
        "approved_request_count: 0",
        "approval_input_complete: false",
        "ready_for_validator: false",
        "ready_for_separate_evidence_collection_request: false",
        "ready_for_separate_execution_request: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "owner_contacted_by_codex: false",
        "blockers_closed_by_helper: 0",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_evidence_request_approval_completion_support: true",
        "recommend_for_evidence_request_approval_import: true",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "--single-request-id",
        "explicit human-provided single-request",
    ]:
        require(token in combined, "missing doc/gate token " + token)

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "owner_contacted_by_codex: true",
        '"owner_contacted_by_codex": true',
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_completion.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_guide.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_status.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_status.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_request_approval_completion_helper.py",
        "/scripts/saee_commercial_evidence_request_approval_completion_helper_smoke.py",
    ]:
        require(token in llms, "llms.txt missing " + token)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_request_approval_completion_helper_v0_1", {})
    for key, value in {
        "commercial_evidence_request_approval_completion_helper_v0_1": True,
        "status": "hold_human_approval_input_required",
        "helper_type": "saee_commercial_evidence_request_approval_completion_helper",
        "helper_scope": "local_evidence_request_approval_completion_sheet_and_import_helper",
        "completion_sheet_ready": True,
        "selected_blocker_count": 5,
        "approval_row_count": 5,
        "approved_request_count": 0,
        "approval_input_complete": False,
        "ready_for_validator": False,
        "ready_for_separate_evidence_collection_request": False,
        "ready_for_separate_execution_request": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "owner_contacted_by_codex": False,
        "blockers_closed_by_helper": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        SMOKE_PASS_PREFIX
        + " status=hold_human_approval_input_required completion_sheet_ready=true "
        + "approved_request_count=0 blockers_closed_by_helper=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
