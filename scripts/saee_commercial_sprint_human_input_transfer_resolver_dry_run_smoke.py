#!/usr/bin/env python3
"""Smoke check for commercial sprint human input transfer resolver dry run."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_RESOLVER_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_RESOLVER_DRY_RUN_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_RESOLVER_DRY_RUN_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    for script in [
        "scripts/saee_commercial_sprint_human_input_workbook.py",
        "scripts/saee_commercial_sprint_human_input_workbook_validator.py",
        "scripts/saee_commercial_sprint_human_input_transfer_map.py",
        "scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run.py",
    ]:
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_transfer_resolver_dry_run_v0_1": True,
        "dry_run_type": "local_template_pointer_resolution_only",
        "dry_run_scope": "resolve_transfer_map_targets_without_value_transfer",
        "status": "pass_mapping_resolved_hold_human_input_required",
        "mapping_row_count": 65,
        "resolved_mapping_row_count": 65,
        "unresolved_mapping_row_count": 0,
        "target_template_count": 5,
        "all_target_templates_known": True,
        "all_pointers_resolved": True,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_resolver_dry_run": 0,
        "boundary_violation_count": 0,
        "production_ready": False,
        "customer_validated": False,
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
        "task_candidates_executed": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must remain empty")
    if payload.get("unresolved_mappings") != []:
        fail("unresolved_mappings must remain empty")
    rows = payload.get("resolver_rows", [])
    if len(rows) != 65:
        fail("resolver_rows must contain 65 rows")
    if any(row.get("pointer_resolved") is not True for row in rows):
        fail("all pointers must resolve")
    if any(row.get("value_transferred") is not False for row in rows):
        fail("no values may be transferred")
    if any(row.get("template_written") is not False for row in rows):
        fail("no human-filled templates may be written")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 65:
        fail("CSV must contain 65 resolver rows")

    required_tokens = [
        "commercial_sprint_human_input_transfer_resolver_dry_run_v0_1: true",
        "status: pass_mapping_resolved_hold_human_input_required",
        "dry_run_scope: resolve_transfer_map_targets_without_value_transfer",
        "mapping_row_count: 65",
        "resolved_mapping_row_count: 65",
        "unresolved_mapping_row_count: 0",
        "all_pointers_resolved: true",
        "ready_for_template_transfer: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_resolver_dry_run: 0",
        "production_ready: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")
    runner = (
        ROOT / "scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_RESOLVER_DRY_RUN_SMOKE: PASS "
        f"status={payload['status']} "
        f"mapping_row_count={payload['mapping_row_count']} "
        f"resolved_mapping_row_count={payload['resolved_mapping_row_count']} "
        f"values_transferred={str(payload['values_transferred']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
