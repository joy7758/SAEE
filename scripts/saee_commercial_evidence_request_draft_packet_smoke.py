#!/usr/bin/env python3
"""Smoke check for the SAEE commercial evidence request draft packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_evidence_request_draft_packet.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUTPUT_JSON = SPRINT_DIR / "evidence_request_draft_packet.local.json"
OUTPUT_MD = SPRINT_DIR / "evidence_request_draft_packet.md"
OUTPUT_CSV = SPRINT_DIR / "evidence_request_draft_packet.csv"
OUTPUT_BOUNDARY = SPRINT_DIR / "evidence_request_draft_boundary_audit.md"
README = SPRINT_DIR / "README.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_RECOMMENDATION_GATE.md"

PASS_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_SMOKE: PASS"
FAIL_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_SMOKE: FAIL "

SELECTED_IDS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def main() -> int:
    require(RUNNER.is_file(), "runner missing")
    subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, OUTPUT_BOUNDARY, README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    packet = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_evidence_request_draft_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_request_draft_packet",
        "packet_version": "v0.1",
        "status": "hold_separate_human_execution_request_required",
        "draft_scope": "local_evidence_request_drafts_for_selected_sprint_blockers",
        "source_sprint_status": "hold_human_review_only",
        "source_owner_assignment_complete": False,
        "selected_blocker_count": 5,
        "draft_request_count": 5,
        "selected_blocker_ids": SELECTED_IDS,
        "human_review_required": True,
        "human_owner_assignment_required": True,
        "separate_execution_approval_required": True,
        "separate_evidence_collection_request_required": True,
        "all_requests_default_hold": True,
        "requests_ready_for_execution": False,
        "blockers_closed_by_draft_packet": 0,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "owner_contacted_by_codex": False,
        "customer_data_collected": False,
        "customer_data_processed": False,
        "vendor_contacted": False,
        "payment_collected": False,
        "revenue_validated": False,
        "production_claim_added": False,
        "launch_claim_added": False,
        "customer_validation_claim_added": False,
    }
    for key, value in expected.items():
        require(packet.get(key) == value, f"{key} must be {value}")

    drafts = packet.get("request_drafts", [])
    require(isinstance(drafts, list), "request_drafts must be a list")
    require(len(drafts) == 5, "must contain five request drafts")
    require([draft.get("blocker_id") for draft in drafts] == SELECTED_IDS, "draft blocker ids drift")
    for index, draft in enumerate(drafts, start=1):
        require(draft.get("request_id") == f"ERD-{index:03d}", "request id sequence drift")
        require(draft.get("request_status") == "draft_only_hold", "draft status must hold")
        require(draft.get("request_type") == "commercial_evidence_collection_request_draft", "draft type mismatch")
        require(draft.get("assigned_human_owner") == "", "draft owner must remain blank")
        require(draft.get("owner_assignment_required") is True, "draft must require owner assignment")
        require(draft.get("owner_assignment_complete") is False, "draft owner assignment must be incomplete")
        require(draft.get("human_approval_required") is True, "draft must require human approval")
        require(draft.get("separate_execution_request_required") is True, "draft must require separate execution request")
        require(draft.get("evidence_collection_authorized") is False, "draft must not authorize evidence collection")
        require(draft.get("execution_authorized") is False, "draft must not authorize execution")
        require(draft.get("closure_authorized") is False, "draft must not authorize closure")
        require(draft.get("default_decision") == "hold", "draft must default hold")
        require(draft.get("evidence_item_count") == len(draft.get("evidence_items", [])), "evidence item count drift")
        require(draft.get("evidence_item_count", 0) >= 1, "draft must include evidence items")
        blocked_by = draft.get("blocked_by", [])
        require("human_owner_assignment" in blocked_by, "draft must be blocked by owner assignment")
        require("separate_execution_approval" in blocked_by, "draft must be blocked by execution approval")

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 5, "CSV must contain five rows")
    require([row["blocker_id"] for row in rows] == SELECTED_IDS, "CSV blocker ids drift")

    report = OUTPUT_MD.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    boundary = OUTPUT_BOUNDARY.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    combined = "\n".join([report, top_doc, gate, boundary, readme])
    for token in [
        "commercial_evidence_request_draft_packet_v0_1: true",
        "packet_type: saee_commercial_evidence_request_draft_packet",
        "status: hold_separate_human_execution_request_required",
        "draft_request_count: 5",
        "human_owner_assignment_required: true",
        "separate_execution_approval_required: true",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "requests_ready_for_execution: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_draft_packet: 0",
        "recommend_for_evidence_request_drafting: true",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "Final boundary decision: local evidence request drafting only.",
    ]:
        require(token in combined, "missing token " + token)

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "owner_contacted_by_codex: true",
        '"owner_contacted_by_codex": true',
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
        "recommend_for_production_readiness_claim: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_draft_packet.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_draft_packet.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_draft_packet.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_draft_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_REQUEST_DRAFT_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_request_draft_packet.py",
        "/scripts/saee_commercial_evidence_request_draft_packet_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_request_draft_packet_v0_1", {})
    for key, value in {
        "commercial_evidence_request_draft_packet_v0_1": True,
        "status": "hold_separate_human_execution_request_required",
        "packet_type": "saee_commercial_evidence_request_draft_packet",
        "draft_scope": "local_evidence_request_drafts_for_selected_sprint_blockers",
        "source_sprint_status": "hold_human_review_only",
        "source_owner_assignment_complete": False,
        "selected_blocker_count": 5,
        "draft_request_count": 5,
        "selected_blocker_ids": SELECTED_IDS,
        "human_review_required": True,
        "human_owner_assignment_required": True,
        "separate_execution_approval_required": True,
        "separate_evidence_collection_request_required": True,
        "requests_ready_for_execution": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "owner_contacted_by_codex": False,
        "blockers_closed_by_draft_packet": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        PASS_PREFIX
        + f" draft_request_count={packet['draft_request_count']}"
        + " evidence_collection_authorized=false execution_authorized=false"
        + " blockers_closed_by_draft_packet=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
