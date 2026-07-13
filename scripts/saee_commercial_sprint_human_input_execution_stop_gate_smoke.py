#!/usr/bin/env python3
"""Smoke check for commercial sprint human input execution stop gate."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "commercial_sprint_human_input_execution_stop_gate_v0_1": True,
        "gate_type": "local_codex_execution_stop_gate_for_missing_human_values",
        "gate_scope": "human_quick_fill_blocker_only_no_values_no_execution",
        "status": "hold_context_or_value_review_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "quick_fill_row_count": 64,
        "completed_value_row_count": 64,
        "missing_value_row_count": 0,
        "ready_for_human_input_row_count": 64,
        "missing_context_row_count": 0,
        "human_input_required": False,
        "human_fill_only": False,
        "allowed_next_actor": "separate_human_approved_local_validator",
        "codex_may_continue_generating_execution_materials": False,
        "codex_may_fill_values": False,
        "codex_may_run_import": False,
        "codex_may_run_real_input_validators": False,
        "codex_may_collect_evidence": False,
        "codex_may_close_blockers": False,
        "blockers_closed_by_gate": 0,
    }
    for key, expected in expected_values.items():
        require(payload.get(key) == expected, f"{key} must be {expected!r}")

    false_flags = [
        "codex_execution_allowed",
        "workbook_import_allowed",
        "validator_execution_on_real_input_allowed",
        "template_transfer_allowed",
        "evidence_collection_allowed",
        "evidence_builder_execution_allowed",
        "blocker_closure_allowed",
        "production_launch_allowed",
        "development_permission_granted",
        "human_values_filled_by_codex",
        "quick_fill_values_entered_by_codex",
        "workbook_import_performed",
        "workbook_written",
        "validators_run_on_real_input",
        "values_transferred",
        "human_filled_templates_written",
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
        "payment_collected",
        "revenue_validated",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for key in false_flags:
        require(payload.get(key) is False, f"{key} must be false")

    rows = payload.get("gate_rows", [])
    require(len(rows) == 3, "gate_rows must contain 3 entries")
    require(
        rows[0].get("decision") == "allow_next_local_review",
        "first gate must allow local review only",
    )

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 3, "CSV must contain 3 gate rows")

    docs = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE])
    required_tokens = [
        "commercial_sprint_human_input_execution_stop_gate_v0_1: true",
        "gate_scope: human_quick_fill_blocker_only_no_values_no_execution",
        "status: hold_context_or_value_review_required",
        "missing_value_row_count: 0",
        "codex_execution_allowed: false",
        "workbook_import_allowed: false",
        "validator_execution_on_real_input_allowed: false",
        "evidence_collection_allowed: false",
        "blocker_closure_allowed: false",
        "production_launch_allowed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_human_quick_fill: false",
        "recommend_for_workbook_import_approval_review: true",
        "recommend_for_codex_execution: false",
        "recommend_for_workbook_import: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
    ]
    for token in required_tokens:
        require(token in docs, f"docs missing {token}")

    forbidden_tokens = [
        "codex_execution_allowed: true",
        "workbook_import_allowed: true",
        "validator_execution_on_real_input_allowed: true",
        "evidence_collection_allowed: true",
        "blocker_closure_allowed: true",
        "production_launch_allowed: true",
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "recommend_for_codex_execution: true",
        "recommend_for_workbook_import: true",
        "recommend_for_validator_execution: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden_tokens if token in docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_execution_stop_gate.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_execution_stop_gate.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_execution_stop_gate.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_execution_stop_gate_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_execution_stop_gate.py",
        "/scripts/saee_commercial_sprint_human_input_execution_stop_gate_smoke.py",
    ]
    for token in required_llms:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = agent_index.get("commercial_sprint_human_input_execution_stop_gate_v0_1", {})
    require(entry.get("status") == "hold_context_or_value_review_required", "agent-index status mismatch")
    require(entry.get("missing_value_row_count") == 0, "agent-index missing value count mismatch")
    for key in [
        "codex_execution_allowed",
        "workbook_import_allowed",
        "validator_execution_on_real_input_allowed",
        "evidence_collection_allowed",
        "blocker_closure_allowed",
        "production_launch_allowed",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_SMOKE: PASS "
        f"missing_value_row_count={payload['missing_value_row_count']} "
        f"codex_execution_allowed={str(payload['codex_execution_allowed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )


if __name__ == "__main__":
    main()
