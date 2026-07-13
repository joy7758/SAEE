#!/usr/bin/env python3
"""Smoke test the support-contact closure-gap review."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_contact_closure_gap_review.py"
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SUMMARY = SUPPORT_DIR / "support_contact_closure_gap_review.local.json"
REPORT = SUPPORT_DIR / "support_contact_closure_gap_review.md"
CSV = SUPPORT_DIR / "support_contact_closure_gap_review.csv"
BOUNDARY = SUPPORT_DIR / "support_contact_closure_gap_review_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_SMOKE: FAIL " + message)


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
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "support_contact_closure_gap_review_v0_1": True,
        "review_type": "local_support_contact_closure_gap_review_no_closure",
        "status": "hold_support_group_complete_pending_go_no_go_and_closure_review",
        "target_blocker_id": "support_contact",
        "support_group_refresh_status": "support_group_human_filled_evidence_complete_for_review_only",
        "support_group_evidence_complete": True,
        "evidence_builder_executed": True,
        "support_contact_available_for_review": True,
        "production_support_available": True,
        "closure_ready_for_human_final_review": False,
        "gap_group_count": 4,
        "missing_evidence_group_count": 0,
        "missing_evidence_item_count": 0,
        "blockers_closed_by_gap_review": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_sent_by_codex": False,
        "blocker_closure_authorized": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")

    groups = {row.get("group_id"): row for row in payload.get("gap_rows", [])}
    require(groups.get("support_contact", {}).get("missing_count") == 0, "support_contact group must be complete")
    require(groups.get("customer_support", {}).get("missing_count") == 0, "customer_support missing count")
    require(groups.get("sla", {}).get("missing_count") == 0, "sla missing count")
    require(groups.get("on_call", {}).get("missing_count") == 0, "on_call missing count")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "support_contact_closure_gap_review_v0_1: true",
        "hold_support_group_complete_pending_go_no_go_and_closure_review",
        "production_support_available=true",
        "closure_ready_for_human_final_review=false",
        "blockers_closed_by_gap_review=0",
        "No support contact published by Codex",
        "answer: hold_support_group_complete_pending_go_no_go_and_closure_review",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_gap_review=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_GATE.md",
        "/scripts/saee_support_contact_closure_gap_review.py",
        "/scripts/saee_support_contact_closure_gap_review_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("support_contact_closure_gap_review_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "target_blocker_id",
        "support_contact_available_for_review",
        "production_support_available",
        "closure_ready_for_human_final_review",
        "missing_evidence_item_count",
        "blockers_closed_by_gap_review",
        "accepted_for_blocker_closure_count",
        "customer_validated",
        "production_ready",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Support Contact Closure Gap Review v0.1",
        "support_contact_closure_gap_review_v0_1",
        "hold_support_group_complete_pending_go_no_go_and_closure_review",
        "missing_evidence_item_count=0",
        "blockers_closed_by_gap_review=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print("SAEE_SUPPORT_CONTACT_CLOSURE_GAP_REVIEW_SMOKE: PASS")


if __name__ == "__main__":
    main()
