#!/usr/bin/env python3
"""Smoke check for commercial sprint validator hold output review."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_sprint_validator_hold_output_review.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_JSON = SPRINT_DIR / "commercial_sprint_validator_hold_output_review.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_validator_hold_output_review.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_validator_hold_output_review.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_validator_hold_output_review_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_SPRINT_VALIDATOR_HOLD_OUTPUT_REVIEW_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_VALIDATOR_HOLD_OUTPUT_REVIEW_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_SPRINT_VALIDATOR_HOLD_OUTPUT_REVIEW_SMOKE: FAIL " + message)


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_validator_hold_output_review_v0_1": True,
        "review_type": "local_validator_hold_output_review_no_execution",
        "status": "validators_passed_evidence_builder_request_required",
        "validator_outputs_reviewed_count": 5,
        "validator_hold_count": 0,
        "validator_pass_count": 5,
        "validator_stop_count": 0,
        "builder_ready_count": 5,
        "total_missing_metadata_field_count": 0,
        "total_missing_evidence_item_count": 0,
        "total_missing_source_note_count": 0,
        "missing_input_completion_required": False,
        "rerun_validators_after_completion_required": False,
        "separate_evidence_builder_request_required": True,
        "evidence_builder_execution_allowed": False,
        "evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_review": 0,
        "boundary_violation_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "real_evidence_created": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(payload.get("boundary_violations") == [], "boundary_violations must be []")
    rows = payload.get("review_rows", [])
    require(isinstance(rows, list) and len(rows) == 5, "review_rows must contain five rows")
    expected_blockers = {
        "support_contact",
        "pricing_page",
        "formal_security_review",
        "production_restore_policy",
        "production_monitoring",
    }
    require({row.get("blocker_id") for row in rows} == expected_blockers, "blocker set changed")
    require(all(row.get("validation_status") == "pass" for row in rows), "all rows must be pass")
    require(all(row.get("builder_ready") is True for row in rows), "builder_ready must be true")
    require(
        all(row.get("evidence_builder_execution_allowed") is False for row in rows),
        "row builder execution must be false",
    )
    require(
        all(row.get("blocker_closure_allowed") is False for row in rows),
        "row blocker closure must be false",
    )

    with OUT_CSV.open(newline="", encoding="utf-8") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 5, "CSV must contain five rows")
    require(all(row["evidence_builder_execution_allowed"] == "False" for row in csv_rows), "CSV builder flag")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE])
    for token in [
        "commercial_sprint_validator_hold_output_review_v0_1: true",
        "status: validators_passed_evidence_builder_request_required",
        "validator_hold_count: 0",
        "builder_ready_count: 5",
        "total_missing_metadata_field_count: 0",
        "total_missing_evidence_item_count: 0",
        "missing_input_completion_required: false",
        "rerun_validators_after_completion_required: false",
        "evidence_builder_execution_allowed: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_review: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: validators_passed_evidence_builder_request_required",
    ]:
        require(token in combined, "missing token " + token)
    for token in [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "evidence_builder_execution_allowed: true",
        '"evidence_builder_execution_allowed": true',
        "blockers_closed_by_review: 1",
    ]:
        require(token not in combined and token not in json.dumps(payload), "forbidden token " + token)

    print(
        "SAEE_COMMERCIAL_SPRINT_VALIDATOR_HOLD_OUTPUT_REVIEW_SMOKE: PASS "
        "validator_hold_count=0 builder_ready_count=5 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
