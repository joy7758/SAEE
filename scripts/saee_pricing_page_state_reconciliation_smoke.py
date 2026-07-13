#!/usr/bin/env python3
"""Smoke test for pricing-page state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_pricing_page_state_reconciliation.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_state_reconciliation"
SUMMARY = OUT_DIR / "pricing_page_state_reconciliation.local.json"
REPORT = OUT_DIR / "pricing_page_state_reconciliation.md"
BOUNDARY = OUT_DIR / "pricing_page_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRICING_PAGE_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_STATE_RECONCILIATION_GATE.md"
EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_PRICING_PAGE_STATE_RECONCILIATION_SMOKE: FAIL " + message)


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
    require("SAEE_PRICING_PAGE_STATE_RECONCILIATION: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "pricing_page_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_pricing_page_state_reconciliation_no_publication_no_closure",
        "target_blocker_id": "pricing_page",
        "human_review_required": True,
        "approval_input_complete": True,
        "approval_builder_ready": True,
        "builder_output_ready": True,
        "closure_review_ready": True,
        "matrix_update_request_ready": True,
        "matrix_update_execution_request_ready": True,
        "matrix_update_approval_copy_card_ready": True,
        "exact_approval_phrase_required": True,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "payment_provider_configured": False,
        "production_billing_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_reconciliation": 0,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
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
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("status") == "ready_for_exact_matrix_update_execution_approval_phrase_no_publication_no_auto_closure",
        "status must point to exact human phrase",
    )
    require(payload.get("resolved_current_path") == "matrix_update_approval_copy_card", "resolved path mismatch")
    require(payload.get("exact_approval_phrase") == EXACT_APPROVAL_PHRASE, "exact phrase drift")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Pricing Page State Reconciliation",
        EXACT_APPROVAL_PHRASE,
        "pricing_page_published=false",
        "checkout_enabled=false",
        "matrix_update_executed=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "No pricing page published by Codex",
        "answer: hold_human_review_required_no_publication_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "pricing_page_published=true",
        "checkout_enabled=true",
        "matrix_update_executed=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/PRICING_PAGE_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_state_reconciliation/pricing_page_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_state_reconciliation/pricing_page_state_reconciliation.md",
        "/docs/strategy/SAEE_PRICING_PAGE_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_pricing_page_state_reconciliation.py",
        "/scripts/saee_pricing_page_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("pricing_page_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index missing pricing_page_state_reconciliation_v0_1")
    for key in [
        "status",
        "target_blocker_id",
        "resolved_current_path",
        "closure_review_ready",
        "matrix_update_request_ready",
        "matrix_update_execution_request_ready",
        "matrix_update_approval_copy_card_ready",
        "pricing_page_published",
        "checkout_enabled",
        "matrix_update_executed",
        "blockers_closed_by_reconciliation",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Pricing Page State Reconciliation v0.1",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_PRICING_PAGE_STATE_RECONCILIATION_SMOKE: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
