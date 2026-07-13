#!/usr/bin/env python3
"""Smoke test for the commercial sprint human-input synthetic pipeline proof."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"

RUNNER = ROOT / "scripts/saee_commercial_sprint_human_input_pipeline_synthetic_proof.py"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_pipeline_synthetic_proof.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_pipeline_synthetic_proof.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_pipeline_synthetic_proof.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_pipeline_synthetic_proof_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_PIPELINE_SYNTHETIC_PROOF_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_PIPELINE_SYNTHETIC_PROOF_RECOMMENDATION_GATE.md"
)
IMPORTER_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"
APPLIER_JSON = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.local.json"
IMPORTED_WORKBOOK_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_workbook.imported_from_quick_fill.local.csv"
)


EXPECTED_TRUE = {
    "commercial_sprint_human_input_pipeline_synthetic_proof_v0_1": True,
    "synthetic_fixture_used": True,
    "synthetic_import_apply_performed": True,
    "synthetic_workbook_written": True,
    "synthetic_transfer_apply_performed": True,
    "synthetic_values_transferred": True,
    "synthetic_templates_written": True,
    "official_artifacts_restored_to_hold": True,
    "official_artifacts_restored_to_safe_no_write": True,
}

EXPECTED_FALSE = [
    "real_human_input_used",
    "official_workbook_written",
    "official_templates_written",
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
    "official_importer_apply_performed_after_restore",
    "official_applier_apply_performed_after_restore",
]

EXPECTED_NUMBERS = {
    "synthetic_value_row_count": 64,
    "quick_fill_row_count": 64,
    "workbook_row_count": 65,
    "import_ready_row_count": 64,
    "synthetic_values_transferred_count": 64,
    "synthetic_templates_written_count": 5,
    "target_template_count": 5,
    "blockers_closed_by_proof": 0,
    "boundary_violation_count": 0,
}

REQUIRED_DOC_TOKENS = [
    "commercial_sprint_human_input_pipeline_synthetic_proof_v0_1: true",
    "status: pass_synthetic_pipeline_mechanics_hold_real_human_input_required",
    "proof_scope: quick_fill_to_workbook_to_temp_template_transfer_only_no_real_evidence",
    "synthetic_fixture_used: true",
    "real_human_input_used: false",
    "synthetic_value_row_count: 64",
    "quick_fill_row_count: 64",
    "workbook_row_count: 65",
    "import_ready_row_count: 64",
    "synthetic_import_apply_performed: true",
    "synthetic_workbook_written: true",
    "synthetic_transfer_apply_performed: true",
    "synthetic_values_transferred: true",
    "synthetic_values_transferred_count: 64",
    "synthetic_templates_written: true",
    "synthetic_templates_written_count: 5",
    "target_template_count: 5",
    "official_artifacts_restored_to_hold: true",
    "official_artifacts_restored_to_safe_no_write: true",
    "official_importer_apply_performed_after_restore: false",
    "official_applier_apply_performed_after_restore: false",
    "official_workbook_written: false",
    "official_templates_written: false",
    "validators_run_on_real_input: false",
    "real_evidence_created: false",
    "evidence_collection_authorized: false",
    "execution_authorized: false",
    "evidence_builder_executed: false",
    "blocker_closure_authorized: false",
    "blockers_closed_by_proof: 0",
    "boundary_violation_count: 0",
    "production_ready: false",
    "customer_validated: false",
    "product_launched: false",
    "private_core_exposed: false",
]

REQUIRED_GATE_TOKENS = [
    "answer: conditional",
    "recommend_for_mechanical_pipeline_proof: true",
    "recommend_for_synthetic_fixture_validation: true",
    "recommend_for_real_evidence: false",
    "recommend_for_real_human_input_substitution: false",
    "recommend_for_validator_execution: false",
    "recommend_for_evidence_collection: false",
    "recommend_for_evidence_builder_execution: false",
    "recommend_for_blocker_closure: false",
    "recommend_for_product_launch: false",
    "recommend_for_production_readiness_claim: false",
]

FORBIDDEN_DOC_TOKENS = [
    "real_human_input_used: true",
    "official_workbook_written: true",
    "official_templates_written: true",
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
    "recommend_for_real_evidence: true",
    "recommend_for_validator_execution: true",
    "recommend_for_evidence_collection: true",
    "recommend_for_evidence_builder_execution: true",
    "recommend_for_blocker_closure: true",
    "recommend_for_product_launch: true",
    "recommend_for_production_readiness_claim: true",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_PIPELINE_SYNTHETIC_PROOF_SMOKE: FAIL {message}")


def read_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def require_token(text: str, token: str, label: str) -> None:
    if token not in text:
        fail(f"{label} missing token {token}")


def restore_current_validator_approval_state() -> None:
    """Restore the workspace to the current human-approved template-transfer state."""

    subprocess.run(
        [
            sys.executable,
            "scripts/saee_commercial_sprint_human_input_template_transfer_applier.py",
            "--workbook-csv",
            str(IMPORTED_WORKBOOK_CSV),
            "--apply",
            "--confirm-human-approved-transfer",
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_post_transfer_validator_sequencer.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_validator_approval_request_packet.py"],
        cwd=ROOT,
        check=True,
    )
    applier = read_json(APPLIER_JSON)
    if applier.get("status") != "template_transfer_applied_pending_validator_approval":
        fail("official applier was not restored to current applied state")
    if applier.get("apply_performed") is not True:
        fail("official applier apply_performed must be true after current-state restore")
    if applier.get("human_filled_templates_written") is not True:
        fail("official applier templates must be written after current-state restore")
    approval = read_json(
        SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.local.json"
    )
    if approval.get("status") != "hold_validator_approval_required":
        fail("validator approval packet was not restored to hold_validator_approval_required")
    if approval.get("validators_run") is not False:
        fail("validator approval packet must keep validators_run false")


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)
    payload = read_json(OUT_JSON)

    if payload.get("status") != "pass_synthetic_pipeline_mechanics_hold_real_human_input_required":
        fail("unexpected synthetic proof status")
    if payload.get("proof_type") != "synthetic_mechanical_pipeline_proof":
        fail("unexpected proof_type")
    if (
        payload.get("proof_scope")
        != "quick_fill_to_workbook_to_temp_template_transfer_only_no_real_evidence"
    ):
        fail("unexpected proof_scope")
    for flag, expected in EXPECTED_TRUE.items():
        if payload.get(flag) != expected:
            fail(f"{flag} must be {expected}")
    for flag in EXPECTED_FALSE:
        if payload.get(flag) is not False:
            fail(f"{flag} must be false")
    for flag, expected in EXPECTED_NUMBERS.items():
        if payload.get(flag) != expected:
            fail(f"{flag} must be {expected}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")
    if len(payload.get("target_summaries", [])) != 5:
        fail("target_summaries must contain 5 template targets")

    importer = read_json(IMPORTER_JSON)
    applier = read_json(APPLIER_JSON)
    if importer.get("status") != "ready_for_apply_pending_explicit_human_command":
        fail("official importer status was not restored")
    if importer.get("apply_performed") is not False:
        fail("official importer apply_performed must be false")
    if importer.get("workbook_written") is not False:
        fail("official importer workbook_written must be false")
    if applier.get("status") != "hold_human_input_required":
        fail("official applier status was not restored")
    if applier.get("apply_performed") is not False:
        fail("official applier apply_performed must be false")
    if applier.get("human_filled_templates_written") is not False:
        fail("official applier human_filled_templates_written must be false")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 5:
        fail("synthetic proof CSV must contain 5 template target rows")

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser"]
    found_runner_tokens = [token for token in forbidden_runner_tokens if token in runner_text]
    if found_runner_tokens:
        fail("runner suggests external access: " + ", ".join(found_runner_tokens))

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
    combined = "\n".join(docs.values())
    found = [token for token in FORBIDDEN_DOC_TOKENS if token in combined]
    if found:
        fail("forbidden doc tokens found: " + ", ".join(found))

    restore_current_validator_approval_state()

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_PIPELINE_SYNTHETIC_PROOF_SMOKE: PASS "
        f"status={payload['status']} "
        "synthetic_templates_written_count=5 "
        "official_artifacts_restored_to_current_validator_approval_state=true "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
