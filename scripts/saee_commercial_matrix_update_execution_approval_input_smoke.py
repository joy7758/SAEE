#!/usr/bin/env python3
"""Smoke test matrix-update execution approval input and validator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/saee_commercial_matrix_update_execution_approval_input.py"
VALIDATOR = ROOT / "scripts/saee_commercial_matrix_update_execution_approval_validator.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests"
TEMPLATE = OUT_DIR / "commercial_matrix_update_execution_approval_input.template.json"
PROMPT = OUT_DIR / "commercial_matrix_update_execution_approval_input.md"
VALIDATION = OUT_DIR / "commercial_matrix_update_execution_approval_validation.local.json"
VALIDATION_MD = OUT_DIR / "commercial_matrix_update_execution_approval_validation.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_GATE.md"
HUMAN_FILLED = OUT_DIR / "commercial_matrix_update_execution_approval_input.human_filled.local.json"


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT: PASS" in result.stdout, "builder did not pass")
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_VALIDATOR: PASS" in result.stdout, "validator did not pass")

    for path in [TEMPLATE, PROMPT, VALIDATION, VALIDATION_MD, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    require(not HUMAN_FILLED.exists(), "smoke expects no human-filled approval file yet")

    template = read_json(TEMPLATE)
    require(template.get("commercial_matrix_update_execution_approval_input_v0_1") is True, "template marker missing")
    require(template.get("human_decision") == "", "template human decision must be blank")
    require(template.get("approve_matrix_update_execution_review_ready_markers_only") is False, "template approval must default false")
    for key in [
        "confirm_no_blocker_closure",
        "confirm_no_pricing_publication",
        "confirm_no_checkout_enablement",
        "confirm_no_production_ready_claim",
        "confirm_no_customer_validation_claim",
        "confirm_no_product_launch",
    ]:
        require(template.get(key) is False, f"{key} must default false")

    payload = read_json(VALIDATION)
    expected = {
        "commercial_matrix_update_execution_approval_validation_v0_1": True,
        "status": "hold_human_execution_approval_input_required",
        "human_execution_approved": False,
        "ready_for_matrix_update_execution": False,
        "approval_input_complete": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_approval_validator": 0,
        "pricing_page_published": False,
        "checkout_enabled": False,
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
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require("human_filled_input_file" in payload.get("missing_fields", []), "missing file must be reported")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [PROMPT, VALIDATION_MD, TOP_DOC, GATE])
    for token in [
        "hold_human_execution_approval_input_required",
        "human_execution_approved=false",
        "matrix_update_executed=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_approval_input=0",
        "production_ready=false",
        "customer_validated=false",
        "answer: hold_human_execution_approval_input_required",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "matrix_update_executed=true",
        "canonical_gap_matrix_modified=true",
        "blocker_closure_authorized=true",
        "pricing_page_published=true",
        "checkout_enabled=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_input.template.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_input.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_approval_input.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_validator.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_input_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_matrix_update_execution_approval_input_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "human_execution_approved",
        "ready_for_matrix_update_execution",
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "blocker_closure_authorized",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")
    require(
        entry.get("make_target") == "make check-commercial-matrix-update-execution-approval-input",
        "make target mismatch",
    )

    print("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_SMOKE: PASS")


if __name__ == "__main__":
    main()
