#!/usr/bin/env python3
"""Smoke test the support-group closure review packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_group_closure_review_packet.py"
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SUMMARY = SUPPORT_DIR / "support_group_closure_review_packet.local.json"
REPORT = SUPPORT_DIR / "support_group_closure_review_packet.md"
CSV = SUPPORT_DIR / "support_group_closure_review_packet.csv"
BOUNDARY = SUPPORT_DIR / "support_group_closure_review_packet_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_SMOKE: FAIL " + message)


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
    require("SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "support_group_closure_review_packet_v0_1": True,
        "review_type": "local_support_group_closure_review_packet_no_auto_closure",
        "status": "ready_for_human_final_closure_review_no_auto_closure",
        "target_blocker_group": "support",
        "support_group_refresh_status": "support_group_human_filled_evidence_complete_for_review_only",
        "support_contact_gap_review_status": "hold_support_group_complete_pending_go_no_go_and_closure_review",
        "combined_support_evidence_available": True,
        "production_support_available": True,
        "support_group_evidence_complete": True,
        "support_contact_available_for_review": True,
        "support_group_closure_candidate_count": 4,
        "support_group_missing_candidate_count": 0,
        "ready_for_human_final_closure_review": True,
        "separate_final_closure_approval_required": True,
        "blocker_closure_authorized": False,
        "blockers_closed_by_packet": 0,
        "development_permission_granted": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
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
    rows = payload.get("closure_review_rows", [])
    require(len(rows) == 4, "must review four support blockers")
    require(all(row.get("evidence_complete") is True for row in rows), "all evidence rows must be complete")
    require(
        all(row.get("closure_review_status") == "ready_for_human_final_closure_review" for row in rows),
        "all rows must be ready for human final closure review",
    )
    require(all(row.get("execution_allowed") is False for row in rows), "row execution must be false")
    require(all(row.get("development_allowed") is False for row in rows), "row development must be false")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "support_group_closure_review_packet_v0_1: true",
        "ready_for_human_final_closure_review_no_auto_closure",
        "blocker_closure_authorized=false",
        "blockers_closed_by_packet=0",
        "No support contact published by Codex",
        "No SLA published by Codex",
        "No on-call rotation started by Codex",
        "answer: ready_for_human_final_closure_review_no_auto_closure",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_packet=1",
        "blocker_closure_authorized=true",
        "development_permission_granted=true",
        "execution_authorized=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_GATE.md",
        "/scripts/saee_support_group_closure_review_packet.py",
        "/scripts/saee_support_group_closure_review_packet_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("support_group_closure_review_packet_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "support_group_evidence_complete",
        "production_support_available",
        "support_group_closure_candidate_count",
        "ready_for_human_final_closure_review",
        "separate_final_closure_approval_required",
        "blocker_closure_authorized",
        "blockers_closed_by_packet",
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
        "Support Group Closure Review Packet v0.1",
        "support_group_closure_review_packet_v0_1",
        "ready_for_human_final_closure_review_no_auto_closure",
        "support_group_closure_candidate_count=4",
        "blockers_closed_by_packet=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print("SAEE_SUPPORT_GROUP_CLOSURE_REVIEW_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
