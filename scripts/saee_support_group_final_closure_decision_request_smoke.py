#!/usr/bin/env python3
"""Smoke test the support-group final closure decision request."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_group_final_closure_decision_request.py"
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SUMMARY = SUPPORT_DIR / "support_group_final_closure_decision_request.local.json"
REPORT = SUPPORT_DIR / "support_group_final_closure_decision_request.md"
CSV = SUPPORT_DIR / "support_group_final_closure_decision_request.csv"
TEMPLATE = SUPPORT_DIR / "support_group_final_closure_decision_template.json"
BOUNDARY = SUPPORT_DIR / "support_group_final_closure_decision_request_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_SMOKE: FAIL " + message)


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
    require(
        "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST: PASS" in result.stdout,
        "runner did not pass",
    )
    for path in [SUMMARY, REPORT, CSV, TEMPLATE, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "support_group_final_closure_decision_request_v0_1": True,
        "request_type": "human_final_closure_decision_request_no_execution",
        "status": "ready_for_human_final_closure_decision_input",
        "target_blocker_group": "support",
        "source_packet_status": "ready_for_human_final_closure_review_no_auto_closure",
        "source_refresh_status": "support_group_human_filled_evidence_complete_for_review_only",
        "production_support_available": True,
        "support_group_evidence_complete": True,
        "support_group_closure_candidate_count": 4,
        "decision_row_count": 4,
        "recommended_approve_for_separate_matrix_update_count": 4,
        "recommended_human_decision": "approve_for_separate_matrix_update_request",
        "final_human_decision_recorded": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_request": 0,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_sent_by_codex": False,
        "sla_published_by_codex": False,
        "on_call_rotation_started_by_codex": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("target_blockers")
        == ["support_contact", "customer_support", "sla", "on_call_rotation"],
        "target blockers must be the support group",
    )
    rows = payload.get("decision_rows", [])
    require(len(rows) == 4, "must include four decision rows")
    require(all(row.get("evidence_complete") is True for row in rows), "all evidence rows complete")
    require(
        all(row.get("recommended_final_decision") == "approve_for_separate_matrix_update_request" for row in rows),
        "all rows should recommend separate matrix update approval",
    )
    require(
        all(row.get("closure_authorized_by_this_request") is False for row in rows),
        "request must not authorize closure",
    )
    require(
        all(row.get("matrix_update_authorized_by_this_request") is False for row in rows),
        "request must not authorize matrix update",
    )

    template = read_json(TEMPLATE)
    require(
        template.get("human_final_decision") == "approve_for_separate_matrix_update_request",
        "template decision must preserve human confirmation",
    )
    require(template.get("human_reviewer") == "张斌", "template reviewer must preserve human reviewer")
    require(template.get("decision_date") == "2026-07-09", "template decision date must preserve human date")
    require(bool(template.get("reason")), "template reason must preserve human reason")
    require(template.get("authorize_separate_matrix_update_request") is True, "template matrix update auth preserved")
    require(template.get("authorize_blocker_closure_now") is False, "template closure auth false")
    require(template.get("authorize_product_launch") is False, "template launch auth false")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "support_group_final_closure_decision_request_v0_1: true",
        "ready_for_human_final_closure_decision_input",
        "final_human_decision_recorded=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_request=0",
        "canonical_gap_matrix_modified=false",
        "answer: ready_for_human_final_closure_decision_input",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_request=1",
        "blocker_closure_authorized=true",
        "final_human_decision_recorded=true",
        "development_permission_granted=true",
        "execution_authorized=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_template.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_GATE.md",
        "/scripts/saee_support_group_final_closure_decision_request.py",
        "/scripts/saee_support_group_final_closure_decision_request_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("support_group_final_closure_decision_request_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "recommended_human_decision",
        "final_human_decision_recorded",
        "blocker_closure_authorized",
        "blockers_closed_by_request",
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "development_permission_granted",
        "execution_authorized",
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
        "Support Group Final Closure Decision Request v0.1",
        "support_group_final_closure_decision_request_v0_1",
        "ready_for_human_final_closure_decision_input",
        "recommended_human_decision=approve_for_separate_matrix_update_request",
        "final_human_decision_recorded=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_request=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print("SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_REQUEST_SMOKE: PASS")


if __name__ == "__main__":
    main()
