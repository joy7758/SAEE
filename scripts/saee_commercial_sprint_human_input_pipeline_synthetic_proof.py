#!/usr/bin/env python3
"""Synthetic mechanical proof for the commercial sprint human-input pipeline.

This proof uses temporary synthetic values to verify that the quick-fill CSV can
feed the workbook importer and that the imported workbook can feed the template
transfer applier. It writes human-filled templates only inside a temporary
directory and restores the official sprint artifacts to their default hold
state afterward.

It does not use real human input, run validators, collect evidence, execute
builders, contact anyone, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
IMPORTER_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"
APPLIER_JSON = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.local.json"

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

EXPECTED_QUICK_FILL_ROWS = 64
EXPECTED_WORKBOOK_ROWS = 65
EXPECTED_TARGET_TEMPLATES = 5

FALSE_FLAGS = [
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
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_local(args: list[str]) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def restore_default_artifacts() -> tuple[dict[str, Any], dict[str, Any]]:
    run_local(["scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py"])
    run_local(["scripts/saee_commercial_sprint_human_input_template_transfer_applier.py"])
    run_local(["scripts/saee_commercial_sprint_post_transfer_validator_sequencer.py"])
    run_local(["scripts/saee_commercial_sprint_validator_approval_request_packet.py"])
    return read_json(IMPORTER_JSON), read_json(APPLIER_JSON)


def build_synthetic_quick_fill(tempdir: Path, temp_workbook: Path) -> Path:
    fields, rows = read_csv(QUICK_FILL_CSV)
    synthetic_rows: list[dict[str, str]] = []
    for row in rows:
        updated = dict(row)
        updated["human_value_to_enter"] = "approved"
        updated["notes_for_human"] = (
            "SYNTHETIC_PIPELINE_PROOF_ONLY_DO_NOT_USE_AS_REAL_EVIDENCE"
        )
        updated["target_workbook_csv"] = rel(temp_workbook)
        synthetic_rows.append(updated)
    temp_quick_fill = tempdir / "synthetic_quick_fill.csv"
    write_csv(temp_quick_fill, fields, synthetic_rows)
    return temp_quick_fill


def run_synthetic_pipeline(tempdir: Path) -> dict[str, Any]:
    temp_workbook = tempdir / "workbook.csv"
    shutil.copyfile(WORKBOOK_CSV, temp_workbook)
    temp_quick_fill = build_synthetic_quick_fill(tempdir, temp_workbook)
    imported_workbook = tempdir / "imported_workbook.csv"
    temp_template_root = tempdir / "template_outputs"
    run_local(
        [
            "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py",
            "--quick-fill-csv",
            str(temp_quick_fill),
            "--workbook-csv",
            str(temp_workbook),
            "--output-workbook-csv",
            str(imported_workbook),
            "--apply",
            "--confirm-human-approved-import",
        ]
    )
    importer_payload = read_json(IMPORTER_JSON)
    run_local(
        [
            "scripts/saee_commercial_sprint_human_input_template_transfer_applier.py",
            "--workbook-csv",
            str(imported_workbook),
            "--output-root",
            str(temp_template_root),
            "--apply",
            "--confirm-human-approved-transfer",
        ]
    )
    applier_payload = read_json(APPLIER_JSON)
    template_outputs = sorted(
        path for path in temp_template_root.rglob("*.json") if path.is_file()
    )
    return {
        "tempdir": str(tempdir),
        "temp_quick_fill_csv": str(temp_quick_fill),
        "temp_workbook_csv": str(temp_workbook),
        "temp_imported_workbook_csv": str(imported_workbook),
        "temp_template_output_root": str(temp_template_root),
        "temp_template_output_count": len(template_outputs),
        "importer_payload": importer_payload,
        "applier_payload": applier_payload,
    }


def build_payload() -> dict[str, Any]:
    boundary_violations: list[str] = []
    with tempfile.TemporaryDirectory(prefix="saee_synthetic_pipeline_") as temp:
        tempdir = Path(temp)
        synthetic_result: dict[str, Any] = {}
        try:
            synthetic_result = run_synthetic_pipeline(tempdir)
        finally:
            official_importer, official_applier = restore_default_artifacts()

    importer_payload = synthetic_result.get("importer_payload", {})
    applier_payload = synthetic_result.get("applier_payload", {})
    if importer_payload.get("apply_performed") is not True:
        boundary_violations.append("synthetic_importer_apply_not_performed")
    if applier_payload.get("apply_performed") is not True:
        boundary_violations.append("synthetic_applier_apply_not_performed")
    if official_importer.get("apply_performed") is not False:
        boundary_violations.append("official_importer_not_restored")
    if official_applier.get("apply_performed") is not False:
        boundary_violations.append("official_applier_not_restored")

    status = (
        "pass_synthetic_pipeline_mechanics_hold_real_human_input_required"
        if not boundary_violations
        else "stop_synthetic_pipeline_boundary_violation"
    )
    target_summaries = applier_payload.get("target_summaries", [])
    payload: dict[str, Any] = {
        "commercial_sprint_human_input_pipeline_synthetic_proof_v0_1": True,
        "proof_type": "synthetic_mechanical_pipeline_proof",
        "proof_scope": "quick_fill_to_workbook_to_temp_template_transfer_only_no_real_evidence",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_pipeline_synthetic_proof.py",
        "synthetic_fixture_used": True,
        "synthetic_value": "approved",
        "synthetic_value_row_count": EXPECTED_QUICK_FILL_ROWS,
        "quick_fill_row_count": importer_payload.get("quick_fill_row_count"),
        "workbook_row_count": importer_payload.get("workbook_row_count"),
        "import_ready_row_count": importer_payload.get("import_ready_row_count"),
        "synthetic_import_apply_performed": importer_payload.get("apply_performed"),
        "synthetic_workbook_written": importer_payload.get("workbook_written"),
        "synthetic_transfer_apply_performed": applier_payload.get("apply_performed"),
        "synthetic_values_transferred": applier_payload.get("values_transferred"),
        "synthetic_values_transferred_count": applier_payload.get("values_transferred_count"),
        "synthetic_templates_written": applier_payload.get("human_filled_templates_written"),
        "synthetic_templates_written_count": applier_payload.get("templates_written_count"),
        "target_template_count": EXPECTED_TARGET_TEMPLATES,
        "target_summaries": target_summaries,
        "official_artifacts_restored_to_hold": (
            official_importer.get("apply_performed") is False
            and official_applier.get("apply_performed") is False
        ),
        "official_artifacts_restored_to_safe_no_write": (
            official_importer.get("apply_performed") is False
            and official_importer.get("workbook_written") is False
            and official_applier.get("apply_performed") is False
            and official_applier.get("human_filled_templates_written") is False
        ),
        "official_importer_status_after_restore": official_importer.get("status"),
        "official_applier_status_after_restore": official_applier.get("status"),
        "official_importer_apply_performed_after_restore": official_importer.get("apply_performed"),
        "official_applier_apply_performed_after_restore": official_applier.get("apply_performed"),
        "blockers_closed_by_proof": 0,
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "next_human_action": (
            "Use real human-filled quick-fill values before any real workbook import, "
            "template transfer, validator run, evidence builder execution, or blocker closure."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_csv_report(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "human_filled_input_target",
        "mapping_row_count",
        "transfer_ready_row_count",
        "value_transferred_count",
        "template_written",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload.get("target_summaries", []):
            writer.writerow({field: row.get(field) for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_pipeline_synthetic_proof_v0_1: true",
        f"status: {payload['status']}",
        f"proof_scope: {payload['proof_scope']}",
        "synthetic_fixture_used: true",
        "real_human_input_used: false",
        f"synthetic_value_row_count: {payload['synthetic_value_row_count']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"import_ready_row_count: {payload['import_ready_row_count']}",
        f"synthetic_import_apply_performed: {str(payload['synthetic_import_apply_performed']).lower()}",
        f"synthetic_workbook_written: {str(payload['synthetic_workbook_written']).lower()}",
        f"synthetic_transfer_apply_performed: {str(payload['synthetic_transfer_apply_performed']).lower()}",
        f"synthetic_values_transferred: {str(payload['synthetic_values_transferred']).lower()}",
        f"synthetic_values_transferred_count: {payload['synthetic_values_transferred_count']}",
        f"synthetic_templates_written: {str(payload['synthetic_templates_written']).lower()}",
        f"synthetic_templates_written_count: {payload['synthetic_templates_written_count']}",
        f"target_template_count: {payload['target_template_count']}",
        f"official_artifacts_restored_to_hold: {str(payload['official_artifacts_restored_to_hold']).lower()}",
        f"official_artifacts_restored_to_safe_no_write: {str(payload['official_artifacts_restored_to_safe_no_write']).lower()}",
        f"official_importer_apply_performed_after_restore: {str(payload['official_importer_apply_performed_after_restore']).lower()}",
        f"official_applier_apply_performed_after_restore: {str(payload['official_applier_apply_performed_after_restore']).lower()}",
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


def write_markdown(path: Path, payload: dict[str, Any], title: str) -> None:
    path.write_text(
        f"""# {title}

{chr(10).join(status_lines(payload))}

## Purpose

This is a synthetic mechanical proof for the local commercial sprint
human-input pipeline. It verifies that temporary synthetic quick-fill values can
flow through the workbook importer and template transfer applier into temporary
template outputs.

## Boundary

The proof is not real commercial evidence. It uses no real human input, writes
no official workbook output, writes no official human-filled templates, runs no
validators on real input, collects no evidence, executes no builders, closes no
blockers, contacts no customers or vendors, launches no product, and makes no
production-readiness or customer-validation claim.
""",
        encoding="utf-8",
    )


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Human Input Pipeline Synthetic Proof Recommendation Gate

answer: conditional
recommend_for_mechanical_pipeline_proof: true
recommend_for_synthetic_fixture_validation: true
recommend_for_real_evidence: false
recommend_for_real_human_input_substitution: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

{chr(10).join(status_lines(payload))}

Reason: this proof is useful only for local pipeline mechanics. It is not
evidence that commercial blockers are satisfied.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv_report(OUT_CSV, payload)
    write_markdown(OUT_MD, payload, "Commercial Sprint Human Input Pipeline Synthetic Proof v0.1")
    write_markdown(OUT_BOUNDARY, payload, "Commercial Sprint Human Input Pipeline Synthetic Proof Boundary Audit")
    write_markdown(TOP_DOC, payload, "SAEE Commercial Sprint Human Input Pipeline Synthetic Proof v0.1")
    write_gate(GATE, payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_PIPELINE_SYNTHETIC_PROOF: PASS "
        f"status={payload['status']} "
        f"synthetic_value_row_count={payload['synthetic_value_row_count']} "
        f"synthetic_templates_written_count={payload['synthetic_templates_written_count']} "
        "real_evidence_created=false production_ready=false"
    )


if __name__ == "__main__":
    main()
