#!/usr/bin/env python3
"""Smoke check for the owner-assignment readiness board."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/saee_commercial_evidence_sprint_owner_assignment_readiness_board.py"
)
HELPER = (
    ROOT
    / "scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py"
)
DEFAULT_INPUT = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.template.json"
)
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_readiness_board.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_readiness_board.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_readiness_board.csv"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD_RECOMMENDATION_GATE.md"
)

PASS_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD_SMOKE: PASS"
FAIL_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


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


def run_board(*args: str) -> dict[str, object]:
    subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, check=True, text=True)
    output_path = OUTPUT_JSON
    if "--output-json" in args:
        output_path = Path(args[args.index("--output-json") + 1])
    return json.loads(output_path.read_text(encoding="utf-8"))


def main() -> int:
    payload = run_board()
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    expected = {
        "commercial_evidence_sprint_owner_assignment_readiness_board_v0_1": True,
        "board_type": "saee_commercial_evidence_sprint_owner_assignment_readiness_board",
        "board_version": "v0.1",
        "status": "hold_no_complete_owner_assignment",
        "board_scope": "local_owner_assignment_input_readiness_diagnostic",
        "selected_blocker_count": 5,
        "complete_owner_assignment_count": 0,
        "partial_owner_assignment_count": 0,
        "missing_owner_assignment_count": 5,
        "boundary_risk_assignment_count": 0,
        "boundary_violation_count": 0,
        "import_ready_assignment_count": 0,
        "ready_for_validator_import": False,
        "ready_for_separate_evidence_collection_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"default {key} must be {value}")
    check_boundary(payload)
    review = payload.get("owner_assignment_readiness_review", [])
    require(len(review) == 5, "board must review 5 selected blockers")
    require(
        all(item.get("owner_assignment_status") == "missing" for item in review),
        "default rows must be missing",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fixture_input = tmp / "single_owner_assignment.json"
        fixture_json = tmp / "single_board.json"
        fixture_md = tmp / "single_board.md"
        fixture_csv = tmp / "single_board.csv"
        subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--single-blocker-id",
                "support_contact",
                "--assigned-human-owner",
                "Fixture Owner",
                "--owner-contact-reference",
                "fixture-owner-contact-reference",
                "--target-review-date",
                "2026-07-12",
                "--owner-acknowledged-scope",
                "true",
                "--human-approval-reference",
                "fixture-human-approval-reference",
                "--output-input-json",
                str(fixture_input),
            ],
            cwd=ROOT,
            check=True,
            text=True,
        )
        fixture = run_board(
            "--input-json",
            str(fixture_input),
            "--output-json",
            str(fixture_json),
            "--output-md",
            str(fixture_md),
            "--output-csv",
            str(fixture_csv),
        )
        require(
            fixture["status"] == "ready_for_validator_import",
            "single complete owner assignment should be import ready",
        )
        require(
            fixture["complete_owner_assignment_count"] == 1,
            "fixture has one complete owner assignment",
        )
        require(
            fixture["missing_owner_assignment_count"] == 4,
            "fixture keeps four owner assignments missing",
        )
        require(
            fixture["import_ready_assignment_count"] == 1,
            "fixture has one import-ready assignment",
        )
        require(
            fixture["ready_blocker_ids"] == ["support_contact"],
            "fixture ready blocker id mismatch",
        )
        check_boundary(fixture)

        unsafe_input = tmp / "unsafe_owner_assignment.json"
        unsafe_data = json.loads(fixture_input.read_text(encoding="utf-8"))
        unsafe_data["boundary_review"]["production_ready"] = True
        unsafe_input.write_text(json.dumps(unsafe_data, indent=2) + "\n", encoding="utf-8")
        unsafe = run_board(
            "--input-json",
            str(unsafe_input),
            "--output-json",
            str(tmp / "unsafe_board.json"),
            "--output-md",
            str(tmp / "unsafe_board.md"),
            "--output-csv",
            str(tmp / "unsafe_board.csv"),
        )
        require(
            unsafe["status"] == "stop_boundary_violation",
            "unsafe fixture must stop on boundary violation",
        )
        require(
            unsafe["boundary_violation_count"] >= 1,
            "unsafe fixture must report boundary violation",
        )

    # Restore default repo outputs after temp fixtures.
    subprocess.run([sys.executable, str(HELPER)], cwd=ROOT, check=True, text=True)
    payload = run_board()

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE]
    )
    for token in [
        "commercial_evidence_sprint_owner_assignment_readiness_board_v0_1: true",
        "status: hold_no_complete_owner_assignment",
        "board_scope: local_owner_assignment_input_readiness_diagnostic",
        "selected_blocker_count: 5",
        "complete_owner_assignment_count: 0",
        "missing_owner_assignment_count: 5",
        "import_ready_assignment_count: 0",
        "ready_for_validator_import: false",
        "ready_for_separate_evidence_collection_request: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "owner_contacted_by_codex: false",
        "blockers_closed_by_board: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_owner_assignment_readiness_diagnostic: true",
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
        + " status=hold_no_complete_owner_assignment "
        + "import_ready_assignment_count=0 blockers_closed_by_board=0 "
        + "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
