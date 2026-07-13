#!/usr/bin/env python3
"""Smoke check for controlled workbook-to-template transfer applier."""

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
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_TEMPLATE_TRANSFER_APPLIER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TEMPLATE_TRANSFER_APPLIER_RECOMMENDATION_GATE.md"
)
WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"

EXPECTED_TARGETS = [
    "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json",
    "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json",
    "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json",
    "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json",
    "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json",
]

ARTIFACT_PATHS = [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TEMPLATE_TRANSFER_APPLIER_SMOKE: "
        f"FAIL: {message}"
    )


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_default() -> dict:
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_commercial_sprint_human_input_template_transfer_applier.py",
        ],
        cwd=ROOT,
        check=True,
    )
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))


def assert_default_payload(payload: dict) -> None:
    expected = {
        "commercial_sprint_human_input_template_transfer_applier_v0_1": True,
        "applier_type": "controlled_workbook_to_human_filled_template_transfer",
        "applier_scope": "workbook_to_template_only_no_validator_no_evidence_no_blocker_closure",
        "status": "hold_human_input_required",
        "execution_mode": "dry_run_no_write",
        "workbook_row_count": 65,
        "mapping_row_count": 65,
        "required_row_count": 64,
        "required_value_present_count": 0,
        "missing_required_value_count": 64,
        "optional_value_present_count": 0,
        "required_transfer_ready_count": 0,
        "optional_transfer_ready_count": 1,
        "target_template_count": 5,
        "apply_requested": False,
        "human_transfer_confirmation_provided": False,
        "apply_preconditions_met": False,
        "apply_performed": False,
        "values_transferred_count": 0,
        "templates_written_count": 0,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_applier": 0,
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
        "vendor_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "task_candidates_executed": False,
        "payment_collected": False,
        "revenue_validated": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("default applier boundary violations must remain empty")
    rows = payload.get("transfer_rows", [])
    if len(rows) != 65:
        fail("default applier must contain 65 transfer rows")
    if any(row.get("value_transferred") for row in rows):
        fail("default applier must not transfer values")
    if any(row.get("template_written") for row in rows):
        fail("default applier must not write templates")


def assert_docs() -> None:
    required_tokens = [
        "commercial_sprint_human_input_template_transfer_applier_v0_1: true",
        "status: hold_human_input_required",
        "execution_mode: dry_run_no_write",
        "applier_scope: workbook_to_template_only_no_validator_no_evidence_no_blocker_closure",
        "workbook_row_count: 65",
        "mapping_row_count: 65",
        "required_row_count: 64",
        "required_value_present_count: 0",
        "missing_required_value_count: 64",
        "required_transfer_ready_count: 0",
        "target_template_count: 5",
        "apply_requested: false",
        "human_transfer_confirmation_provided: false",
        "apply_performed: false",
        "ready_for_template_transfer: false",
        "ready_for_existing_local_validators: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "values_transferred_count: 0",
        "templates_written_count: 0",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_applier: 0",
        "boundary_violation_count: 0",
        "production_ready: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")
    gate = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: conditional",
        "recommend_for_transfer_readiness_check: true",
        "recommend_for_human_approved_template_transfer: true",
        "recommend_for_unapproved_transfer: false",
        "recommend_for_value_inference: false",
        "recommend_for_value_suggestion: false",
        "recommend_for_validator_execution: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        if token not in gate:
            fail(f"gate missing token {token}")
    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 65:
        fail("applier CSV must contain 65 rows")


def assert_apply_fixture() -> None:
    with tempfile.TemporaryDirectory() as temp:
        tempdir = Path(temp)
        tmp_workbook = tempdir / "workbook.csv"
        fields, rows = read_csv(WORKBOOK_CSV)
        for row in rows:
            if row["minimum_required"] == "True":
                row["human_value_placeholder"] = "approved"
                row["status"] = "human_filled_pending_transfer"
        write_csv(tmp_workbook, fields, rows)
        subprocess.run(
            [
                sys.executable,
                "scripts/saee_commercial_sprint_human_input_template_transfer_applier.py",
                "--workbook-csv",
                str(tmp_workbook),
                "--output-root",
                str(tempdir),
                "--apply",
                "--confirm-human-approved-transfer",
            ],
            cwd=ROOT,
            check=True,
        )
        payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        if payload.get("apply_performed") is not True:
            fail("apply fixture must record apply_performed true")
        if payload.get("values_transferred") is not True:
            fail("apply fixture must record values_transferred true")
        if payload.get("human_filled_templates_written") is not True:
            fail("apply fixture must record human_filled_templates_written true")
        if payload.get("templates_written_count") != 5:
            fail("apply fixture must write five target templates")
        for target in EXPECTED_TARGETS:
            output_path = tempdir / target
            if not output_path.exists():
                fail(f"apply fixture missing output target {target}")
            document = json.loads(output_path.read_text(encoding="utf-8"))
            if document.get("input_status") != "human_filled_pending_validator":
                fail(f"apply fixture did not mark input_status for {target}")
    payload = run_default()
    assert_default_payload(payload)


def backup_artifacts() -> dict[Path, bytes | None]:
    return {path: path.read_bytes() if path.exists() else None for path in ARTIFACT_PATHS}


def restore_artifacts(backups: dict[Path, bytes | None]) -> None:
    for path, data in backups.items():
        if data is None:
            path.unlink(missing_ok=True)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def assert_current_applied_payload(payload: dict) -> None:
    expected = {
        "commercial_sprint_human_input_template_transfer_applier_v0_1": True,
        "applier_type": "controlled_workbook_to_human_filled_template_transfer",
        "applier_scope": "workbook_to_template_only_no_validator_no_evidence_no_blocker_closure",
        "status": "template_transfer_applied_pending_validator_approval",
        "execution_mode": "apply_write_local_human_filled_templates",
        "workbook_row_count": 65,
        "mapping_row_count": 65,
        "required_row_count": 64,
        "required_value_present_count": 64,
        "missing_required_value_count": 0,
        "optional_value_present_count": 0,
        "required_transfer_ready_count": 64,
        "optional_transfer_ready_count": 1,
        "target_template_count": 5,
        "apply_requested": True,
        "human_transfer_confirmation_provided": True,
        "apply_preconditions_met": True,
        "apply_performed": True,
        "values_transferred_count": 64,
        "templates_written_count": 5,
        "ready_for_template_transfer": True,
        "ready_for_existing_local_validators": True,
        "values_transferred": True,
        "human_filled_templates_written": True,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_applier": 0,
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
        "vendor_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "task_candidates_executed": False,
        "human_input_filled_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "payment_collected": False,
        "revenue_validated": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"current applied payload {key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("current applied payload boundary violations must remain empty")
    rows = payload.get("transfer_rows", [])
    if len(rows) != 65:
        fail("current applied payload must contain 65 transfer rows")
    if sum(1 for row in rows if row.get("value_transferred")) != 64:
        fail("current applied payload must transfer exactly 64 required values")
    if not all(row.get("template_written") for row in rows):
        fail("current applied payload must mark target templates written")


def assert_current_applied_docs() -> None:
    required_tokens = [
        "commercial_sprint_human_input_template_transfer_applier_v0_1: true",
        "status: template_transfer_applied_pending_validator_approval",
        "execution_mode: apply_write_local_human_filled_templates",
        "applier_scope: workbook_to_template_only_no_validator_no_evidence_no_blocker_closure",
        "workbook_row_count: 65",
        "mapping_row_count: 65",
        "required_row_count: 64",
        "required_value_present_count: 64",
        "missing_required_value_count: 0",
        "required_transfer_ready_count: 64",
        "target_template_count: 5",
        "apply_requested: true",
        "human_transfer_confirmation_provided: true",
        "apply_performed: true",
        "ready_for_template_transfer: true",
        "ready_for_existing_local_validators: true",
        "values_transferred: true",
        "human_filled_templates_written: true",
        "values_transferred_count: 64",
        "templates_written_count: 5",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_applier: 0",
        "boundary_violation_count: 0",
        "production_ready: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"current applied {path} missing token {token}")
    boundary = OUT_BOUNDARY.read_text(encoding="utf-8")
    for token in [
        "Apply mode wrote five local human-filled template files after explicit human transfer confirmation.",
        "No validator was run on real input.",
        "No evidence was collected.",
        "No blocker was closed.",
    ]:
        if token not in boundary:
            fail(f"current applied boundary audit missing token {token}")


def main() -> int:
    backups = backup_artifacts()
    try:
        payload = run_default()
        assert_default_payload(payload)
        assert_docs()
        assert_apply_fixture()

        runner = (
            ROOT / "scripts/saee_commercial_sprint_human_input_template_transfer_applier.py"
        ).read_text(encoding="utf-8")
        for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
            if token in runner:
                fail(f"runner suggests external access: {token}")
    finally:
        restore_artifacts(backups)

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert_current_applied_payload(payload)
    assert_current_applied_docs()
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TEMPLATE_TRANSFER_APPLIER_SMOKE: PASS "
        f"status={payload['status']} "
        f"execution_mode={payload['execution_mode']} "
        f"required_transfer_ready_count={payload['required_transfer_ready_count']} "
        f"apply_performed={str(payload['apply_performed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
