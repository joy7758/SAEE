#!/usr/bin/env python3
"""Smoke check for the matrix-update approval copy card."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_execution_approval_copy_card.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests"
SUMMARY = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card.local.json"
REPORT = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card.md"
HTML = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card.html"
AUDIT = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_GATE.md"
HUMAN_FILLED = OUT_DIR / "commercial_matrix_update_execution_approval_input.human_filled.local.json"

EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_SMOKE: FAIL: "
            + message
        )


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain a JSON object")
    return data


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    if HUMAN_FILLED.exists():
        HUMAN_FILLED.unlink()
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD: PASS" in result.stdout,
        "runner did not print PASS",
    )
    for path in [SUMMARY, REPORT, HTML, AUDIT, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_matrix_update_execution_approval_copy_card_v0_1": True,
        "card_type": "local_exact_phrase_copy_helper_no_execution",
        "status": "ready_for_exact_phrase_human_approval_no_execution",
        "exact_phrase_required": True,
        "exact_approval_phrase": EXACT_APPROVAL_PHRASE,
        "human_filled_approval_exists": False,
        "human_filled_approval_written": False,
        "human_execution_approved": False,
        "ready_for_matrix_update_execution": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_copy_card": 0,
        "open_blocker_count_reduced": False,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(int(payload.get("open_blocker_count", 0)) >= 1, "open blocker count must remain nonzero")
    require(not HUMAN_FILLED.exists(), "copy card must not write human-filled approval")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, HTML, AUDIT, TOP_DOC, GATE])
    for token in [
        EXACT_APPROVAL_PHRASE,
        "matrix_update_executed: false",
        "canonical_gap_matrix_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_copy_card: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
    ]:
        require(token in combined, "missing token " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.html",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_approval_copy_card.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_copy_card_smoke.py",
    ]:
        require(token in llms, "llms.txt missing " + token)

    entry = read_json(ROOT / "agent-index.json").get(
        "commercial_matrix_update_execution_approval_copy_card_v0_1"
    )
    require(isinstance(entry, dict), "agent-index entry missing")
    for key in [
        "status",
        "human_filled_approval_written",
        "human_execution_approved",
        "ready_for_matrix_update_execution",
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "blocker_closure_authorized",
        "blockers_closed_by_copy_card",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} mismatch")

    print("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_SMOKE: PASS")


if __name__ == "__main__":
    main()
