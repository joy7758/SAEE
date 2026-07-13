#!/usr/bin/env python3
"""Smoke test for the commercial sprint human-input safety preflight."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_human_input_safety_preflight.py"
SOURCE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_SAFETY_PREFLIGHT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_SAFETY_PREFLIGHT_RECOMMENDATION_GATE.md"
)

EXPECTED_FALSE = [
    "ready_for_workbook_import",
    "raw_values_recorded",
    "quick_fill_imported_to_workbook",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
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
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "payment_collected",
    "revenue_validated",
]

REQUIRED_DOC_TOKENS = [
    "commercial_sprint_human_input_safety_preflight_v0_1: true",
    "preflight_scope: quick_fill_values_and_notes_only_no_import_no_transfer_no_evidence",
    "quick_fill_row_count: 64",
    "rows_scanned_count: 64",
    "secret_pattern_hit_count: 0",
    "private_core_reference_count: 0",
    "production_overclaim_count: 0",
    "customer_validation_claim_count: 0",
    "product_launch_claim_count: 0",
    "external_validation_claim_count: 0",
    "unsafe_row_count: 0",
    "warning_row_count: 0",
    "contact_data_warning_count: 0",
    "ready_for_workbook_import: false",
    "raw_values_recorded: false",
    "quick_fill_imported_to_workbook: false",
    "workbook_written: false",
    "values_transferred: false",
    "human_filled_templates_written: false",
    "validators_run_on_real_input: false",
    "real_evidence_created: false",
    "evidence_collection_authorized: false",
    "execution_authorized: false",
    "evidence_builder_executed: false",
    "blocker_closure_authorized: false",
    "boundary_violation_count: 0",
    "production_ready: false",
    "customer_validated: false",
    "product_launched: false",
    "private_core_exposed: false",
]

REQUIRED_GATE_TOKENS = [
    "answer: conditional",
    "recommend_for_pre_import_safety_screening: true",
    "recommend_for_secret_pattern_detection: true",
    "recommend_for_private_core_leakage_screening: true",
    "recommend_for_claim_boundary_screening: true",
    "recommend_for_workbook_import: false",
    "recommend_for_template_transfer: false",
    "recommend_for_validator_execution: false",
    "recommend_for_evidence_collection: false",
    "recommend_for_evidence_builder_execution: false",
    "recommend_for_blocker_closure: false",
    "recommend_for_product_launch: false",
    "recommend_for_production_readiness_claim: false",
]

FORBIDDEN_DOC_TOKENS = [
    "ready_for_workbook_import: true",
    "raw_values_recorded: true",
    "quick_fill_imported_to_workbook: true",
    "workbook_written: true",
    "values_transferred: true",
    "human_filled_templates_written: true",
    "validators_run_on_real_input: true",
    "real_evidence_created: true",
    "evidence_collection_authorized: true",
    "execution_authorized: true",
    "evidence_builder_executed: true",
    "blocker_closure_authorized: true",
    "production_ready: true",
    "customer_validated: true",
    "product_launched: true",
    "private_core_exposed: true",
    "recommend_for_workbook_import: true",
    "recommend_for_template_transfer: true",
    "recommend_for_validator_execution: true",
    "recommend_for_evidence_collection: true",
    "recommend_for_evidence_builder_execution: true",
    "recommend_for_blocker_closure: true",
    "recommend_for_product_launch: true",
    "recommend_for_production_readiness_claim: true",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_SAFETY_PREFLIGHT_SMOKE: FAIL {message}")


def read_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_default() -> dict:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)
    return read_json(OUT_JSON)


def run_unsafe_fixture() -> dict:
    with tempfile.TemporaryDirectory(prefix="saee_input_safety_") as temp:
        fixture = Path(temp) / "quick_fill_with_fake_secret.csv"
        shutil.copyfile(SOURCE_CSV, fixture)
        with fixture.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
            fields = list(rows[0].keys())
        rows[0]["human_value_to_enter"] = "sk-proj-THISISANONREALFAKESECRETKEYFORSCANNERONLY"
        with fixture.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        subprocess.run(
            [sys.executable, str(RUNNER), "--quick-fill-csv", str(fixture)],
            cwd=ROOT,
            check=True,
        )
        unsafe_payload = read_json(OUT_JSON)
    return unsafe_payload


def require_token(text: str, token: str, label: str) -> None:
    if token not in text:
        fail(f"{label} missing token {token}")


def main() -> None:
    payload = run_default()
    filled_count = payload.get("filled_value_row_count")
    blank_count = payload.get("blank_value_row_count")
    if filled_count == 0:
        expected_status = "hold_human_input_required_no_values_to_scan"
        expected_safe_to_import = False
    elif filled_count == 64:
        expected_status = "pass_no_sensitive_values_found_pending_import_approval"
        expected_safe_to_import = True
    else:
        fail("default source must be either blank or fully human-confirmed")
    if payload.get("status") != expected_status:
        fail(f"default status must be {expected_status}")
    expected_payload = {
        "commercial_sprint_human_input_safety_preflight_v0_1": True,
        "preflight_type": "local_human_input_safety_preflight",
        "preflight_scope": "quick_fill_values_and_notes_only_no_import_no_transfer_no_evidence",
        "quick_fill_row_count": 64,
        "rows_scanned_count": 64,
        "filled_value_row_count": filled_count,
        "blank_value_row_count": blank_count,
        "secret_pattern_hit_count": 0,
        "private_core_reference_count": 0,
        "production_overclaim_count": 0,
        "customer_validation_claim_count": 0,
        "product_launch_claim_count": 0,
        "external_validation_claim_count": 0,
        "unsafe_row_count": 0,
        "warning_row_count": 0,
        "contact_data_warning_count": 0,
        "boundary_violation_count": 0,
    }
    for flag, expected in expected_payload.items():
        if payload.get(flag) != expected:
            fail(f"{flag} must be {expected}")
    if payload.get("safe_to_import_after_human_approval") is not expected_safe_to_import:
        fail(f"safe_to_import_after_human_approval must be {expected_safe_to_import}")
    for flag in EXPECTED_FALSE:
        if payload.get(flag) is not False:
            fail(f"{flag} must be false")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty for default input")
    if len(payload.get("row_summaries", [])) != 64:
        fail("row_summaries must contain 64 rows")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = handle.readline() if False else None
    if len(rows) != 64:
        fail("preflight CSV must contain 64 rows")
    if "human_value_to_enter" in ",".join(rows[0].keys()):
        fail("preflight CSV must not include raw human value column")

    docs = {
        "top_doc": TOP_DOC.read_text(encoding="utf-8"),
        "report": OUT_MD.read_text(encoding="utf-8"),
        "boundary": OUT_BOUNDARY.read_text(encoding="utf-8"),
        "gate": GATE.read_text(encoding="utf-8"),
    }
    for label, text in docs.items():
        tokens = REQUIRED_GATE_TOKENS if label == "gate" else REQUIRED_DOC_TOKENS
        for token in tokens:
            require_token(text, token, label)
        if label != "gate":
            for token in [
                f"status: {expected_status}",
                f"filled_value_row_count: {filled_count}",
                f"blank_value_row_count: {blank_count}",
                f"safe_to_import_after_human_approval: {str(expected_safe_to_import).lower()}",
            ]:
                require_token(text, token, label)
    combined = "\n".join(docs.values())
    found = [token for token in FORBIDDEN_DOC_TOKENS if token in combined]
    if found:
        fail("forbidden doc tokens found: " + ", ".join(found))

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]
    found_runner = [token for token in forbidden_runner_tokens if token in runner_text]
    if found_runner:
        fail("runner suggests external access or execution: " + ", ".join(found_runner))

    unsafe_payload = run_unsafe_fixture()
    if unsafe_payload.get("status") != "stop_sensitive_or_forbidden_input_detected":
        fail("unsafe fixture must produce stop status")
    if unsafe_payload.get("secret_pattern_hit_count", 0) < 1:
        fail("unsafe fixture must detect fake secret pattern")
    if unsafe_payload.get("raw_values_recorded") is not False:
        fail("unsafe fixture must not record raw values")

    payload = run_default()
    if payload.get("status") != expected_status:
        fail("default status must be restored after unsafe fixture")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_SAFETY_PREFLIGHT_SMOKE: PASS "
        f"status={payload['status']} rows_scanned_count=64 "
        "secret_pattern_hit_count=0 raw_values_recorded=false production_ready=false"
    )


if __name__ == "__main__":
    main()
