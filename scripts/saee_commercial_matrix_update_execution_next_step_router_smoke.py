#!/usr/bin/env python3
"""Smoke test matrix-update execution next-step router."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_execution_next_step_router.py"
MATRIX_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests"
SUMMARY = MATRIX_DIR / "commercial_matrix_update_execution_next_step_router.local.json"
REPORT = MATRIX_DIR / "commercial_matrix_update_execution_next_step_router.md"
BOUNDARY = MATRIX_DIR / "commercial_matrix_update_execution_next_step_router_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_GATE.md"
EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_matrix_update_execution_next_step_router_v0_1": True,
        "router_type": "matrix_update_execution_next_step_no_execution",
        "status": "waiting_for_exact_human_approval_phrase",
        "support_ready_for_phrase": True,
        "copy_card_ready": True,
        "phrase_intake_written": False,
        "approval_ready_for_matrix_update_execution": False,
        "exact_approval_phrase_required": True,
        "human_filled_approval_written": False,
        "human_execution_approved_by_router": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_router": 0,
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
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(payload.get("exact_approval_phrase") == EXACT_APPROVAL_PHRASE, "exact phrase drift")
    require(len(payload.get("approval_commands_after_exact_phrase", [])) >= 5, "command chain missing")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        EXACT_APPROVAL_PHRASE,
        "waiting_for_exact_human_approval_phrase",
        "human_filled_approval_written=false",
        "matrix_update_executed=false",
        "blockers_closed_by_router=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "matrix_update_executed=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_router=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_next_step_router.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_next_step_router.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_next_step_router.py",
        "/scripts/saee_commercial_matrix_update_execution_next_step_router_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_matrix_update_execution_next_step_router_v0_1")
    require(isinstance(entry, dict), "agent-index missing router entry")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Commercial Matrix Update Execution Next Step Router v0.1",
        "waiting_for_exact_human_approval_phrase",
        "production readiness",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_SMOKE: PASS "
        "status=waiting_for_exact_human_approval_phrase matrix_update_executed=false"
    )


if __name__ == "__main__":
    main()
