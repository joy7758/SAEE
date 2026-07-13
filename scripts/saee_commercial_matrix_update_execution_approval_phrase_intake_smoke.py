#!/usr/bin/env python3
"""Smoke test matrix-update approval phrase intake."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests"
SUMMARY = OUT_DIR / "commercial_matrix_update_execution_approval_phrase_intake.local.json"
REPORT = OUT_DIR / "commercial_matrix_update_execution_approval_phrase_intake.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_GATE.md"
HUMAN_FILLED = OUT_DIR / "commercial_matrix_update_execution_approval_input.human_filled.local.json"
EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_SMOKE: FAIL "
        + message
    )


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
    if HUMAN_FILLED.exists():
        fail("default smoke expects no human-filled approval file")

    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE: PASS" in result.stdout,
        "runner did not pass",
    )
    require(not HUMAN_FILLED.exists(), "default run must not create human-filled approval")
    for path in [SUMMARY, REPORT, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_matrix_update_execution_approval_phrase_intake_v0_1": True,
        "intake_type": "exact_phrase_to_structured_human_approval",
        "status": "hold_exact_approval_phrase_required",
        "exact_phrase_required": True,
        "phrase_provided": False,
        "phrase_matches_exactly": False,
        "write_human_filled_requested": False,
        "human_filled_approval_written": False,
        "human_execution_approved_by_phrase_intake": False,
        "ready_for_approval_validator": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_phrase_intake": 0,
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
    require(payload.get("exact_phrase") == EXACT_APPROVAL_PHRASE, "exact phrase mismatch")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, TOP_DOC, GATE])
    for token in [
        "commercial_matrix_update_execution_approval_phrase_intake_v0_1: true",
        "hold_exact_approval_phrase_required",
        "human_filled_approval_written: `false`",
        "matrix_update_executed: `false`",
        "canonical_gap_matrix_modified: `false`",
        "blocker_closure_authorized: `false`",
        "production_ready: `false`",
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
        "blockers_closed_by_phrase_intake=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_phrase_intake.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_phrase_intake.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_phrase_intake_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("commercial_matrix_update_execution_approval_phrase_intake_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "phrase_matches_exactly",
        "human_filled_approval_written",
        "human_execution_approved_by_phrase_intake",
        "ready_for_approval_validator",
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "blocker_closure_authorized",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    # Verify exact phrase logic can create the expected approval file, then restore
    # the default no-file state before returning.
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--phrase",
            EXACT_APPROVAL_PHRASE,
            "--write-human-filled",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("human_filled_approval_written=true" in result.stdout, "exact phrase path did not write")
    human_filled = read_json(HUMAN_FILLED)
    require(
        human_filled.get("human_decision") == "approve_matrix_update_execution_review_ready_markers_only",
        "human decision mismatch",
    )
    for key in [
        "approve_matrix_update_execution_review_ready_markers_only",
        "confirm_no_blocker_closure",
        "confirm_no_pricing_publication",
        "confirm_no_checkout_enablement",
        "confirm_no_production_ready_claim",
        "confirm_no_customer_validation_claim",
        "confirm_no_product_launch",
    ]:
        require(human_filled.get(key) is True, f"{key} must be true in generated approval")
    HUMAN_FILLED.unlink()
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, capture_output=True, check=True)

    print("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_PHRASE_INTAKE_SMOKE: PASS")


if __name__ == "__main__":
    main()
