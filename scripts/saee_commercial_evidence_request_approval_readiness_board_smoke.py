#!/usr/bin/env python3
"""Smoke check for the ERD approval readiness board."""

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
)


SCRIPT = ROOT / "scripts/saee_commercial_evidence_request_approval_readiness_board.py"
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_readiness_board.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_readiness_board.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_readiness_board.csv"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD_RECOMMENDATION_GATE.md"
)
PASS_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD_SMOKE: PASS"
FAIL_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == CSV_FIELDS, "source completion CSV header mismatch")
        return list(reader)


def write_fixture_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for index, row in enumerate(rows):
            item = dict(row)
            if index == 0:
                item["assigned_human_owner"] = "Fixture Owner"
                item["human_approval_reference"] = "fixture-approval-reference"
                item["approval_scope"] = "evidence_collection_only"
                item["approval_decision"] = (
                    "approved_for_separate_evidence_collection_request"
                )
                item["evidence_collection_request_reference"] = (
                    "fixture-separate-evidence-request"
                )
                item["owner_acknowledged_scope"] = "true"
                item["boundary_acknowledged"] = "true"
            writer.writerow(item)


def check_boundary(payload: dict[str, object]) -> None:
    for key in [
        "evidence_collection_authorized",
        "execution_authorized",
        "owner_contacted_by_codex",
        "customer_contacted",
        "vendor_contacted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "task_candidates_executed",
        "development_permission_granted",
    ]:
        require(payload.get(key) is False, f"{key} must remain false")
    require(payload.get("blockers_closed_by_board") == 0, "board closes no blockers")


def main() -> int:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, text=True)
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_evidence_request_approval_readiness_board_v0_1": True,
        "board_type": "saee_commercial_evidence_request_approval_readiness_board",
        "board_version": "v0.1",
        "status": "hold_no_approved_request",
        "board_scope": "local_erd_approval_completion_readiness_diagnostic",
        "approval_row_count": 5,
        "approved_candidate_count": 0,
        "import_ready_request_count": 0,
        "invalid_row_count": 0,
        "boundary_violation_count": 0,
        "ready_for_validator_import": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"default {key} must be {value}")
    check_boundary(payload)
    review = payload.get("request_readiness_review", [])
    require(len(review) == 5, "board must review 5 rows")
    require(
        all(item.get("row_status") == "held" for item in review),
        "default rows must remain held",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fixture_csv = tmp / "fixture_completion.csv"
        fixture_json = tmp / "fixture_board.json"
        fixture_md = tmp / "fixture_board.md"
        fixture_board_csv = tmp / "fixture_board.csv"
        write_fixture_csv(fixture_csv, read_rows(COMPLETION_CSV_PATH))
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input-csv",
                str(fixture_csv),
                "--output-json",
                str(fixture_json),
                "--output-md",
                str(fixture_md),
                "--output-csv",
                str(fixture_board_csv),
            ],
            cwd=ROOT,
            check=True,
            text=True,
        )
        fixture = json.loads(fixture_json.read_text(encoding="utf-8"))
        require(
            fixture["status"] == "ready_for_validator_import",
            "complete fixture should be import ready",
        )
        require(fixture["approved_candidate_count"] == 1, "fixture has one approval")
        require(fixture["import_ready_request_count"] == 1, "fixture has one ready row")
        require(fixture["ready_request_ids"] == ["ERD-001"], "fixture ready id mismatch")
        check_boundary(fixture)

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE]
    )
    for token in [
        "commercial_evidence_request_approval_readiness_board_v0_1: true",
        "status: hold_no_approved_request",
        "board_scope: local_erd_approval_completion_readiness_diagnostic",
        "approval_row_count: 5",
        "approved_candidate_count: 0",
        "import_ready_request_count: 0",
        "ready_for_validator_import: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_board: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_approval_readiness_diagnostic: true",
        "recommend_for_validator_import: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
    ]:
        require(token in combined, "missing doc/gate token " + token)

    forbidden = [
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
        "recommend_for_validator_import: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print(
        PASS_PREFIX
        + " status=hold_no_approved_request import_ready_request_count=0 "
        + "blockers_closed_by_board=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
