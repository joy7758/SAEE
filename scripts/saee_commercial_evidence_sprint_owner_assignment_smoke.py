#!/usr/bin/env python3
"""Smoke check for the commercial evidence sprint owner assignment packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
PACKET_JSON = SPRINT_DIR / "owner_assignment_packet.local.json"
PACKET_MD = SPRINT_DIR / "owner_assignment_packet.md"
PACKET_CSV = SPRINT_DIR / "owner_assignment_packet.csv"
BOUNDARY_PATH = SPRINT_DIR / "owner_assignment_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_RECOMMENDATION_GATE.md"
SCRIPT_PATH = ROOT / "scripts/saee_commercial_evidence_sprint_owner_assignment.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_SMOKE: FAIL " + message
        )


def main() -> int:
    for path in [
        PACKET_JSON,
        PACKET_MD,
        PACKET_CSV,
        BOUNDARY_PATH,
        TOP_DOC,
        GATE_PATH,
        SCRIPT_PATH,
    ]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_commercial_evidence_sprint_owner_assignment",
        "status": "hold_owner_assignment_required",
        "assignment_scope": "local_owner_assignment_template_for_selected_evidence_sprint",
        "source_sprint_status": "hold_human_review_only",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "selected_blocker_count": 5,
        "assigned_owner_count": 0,
        "unassigned_owner_count": 5,
        "all_owners_assigned": False,
        "human_owner_assignment_required": True,
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "blockers_closed_by_assignment": 0,
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
        "payment_collected": False,
        "revenue_validated": False,
        "production_claim_added": False,
        "launch_claim_added": False,
        "customer_validation_claim_added": False,
    }
    for key, value in expected.items():
        require(packet.get(key) == value, f"{key} must be {value}")

    required_ids = [
        "support_contact",
        "pricing_page",
        "formal_security_review",
        "production_restore_policy",
        "production_monitoring",
    ]
    require(packet.get("selected_blocker_ids") == required_ids, "selected blocker ids changed")
    rows = packet.get("assignment_rows", [])
    require(len(rows) == 5, "assignment row count must be 5")
    for row in rows:
        require(row.get("assignment_status") == "unassigned", "row must be unassigned")
        require(row.get("assigned_human_owner") == "", "owner must be blank")
        require(row.get("target_review_date") == "", "target date must be blank")
        require(row.get("requires_human_owner") is True, "human owner required")
        require(row.get("requires_human_approval") is True, "human approval required")
        require(row.get("requires_separate_execution_request") is True, "separate execution required")
        require(row.get("evidence_collection_authorized") is False, "collection must be false")
        require(row.get("execution_authorized") is False, "execution must be false")
        require(row.get("closure_authorized") is False, "closure must be false")
        require(row.get("owner_contacted_by_codex") is False, "owner contact must be false")
        require(row.get("first_evidence_record_ids"), "evidence samples must be retained")
        require(row.get("first_evidence_keys"), "evidence keys must be retained")

    report = PACKET_MD.read_text(encoding="utf-8")
    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE_PATH.read_text(encoding="utf-8")
    for token in [
        "Status: hold_owner_assignment_required.",
        "selected_blocker_count: 5",
        "assigned_owner_count: 0",
        "unassigned_owner_count: 5",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_assignment: 0",
        "production_ready: false",
    ]:
        require(token in report or token in top_doc, f"missing report/doc token {token}")
    for token in [
        "recommend_for_owner_assignment_planning: true",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_customer_contact: false",
        "recommend_for_product_launch: false",
    ]:
        require(token in gate, f"gate missing {token}")
    for token in [
        "owner_contacted_by_codex: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "Final boundary decision: local owner assignment planning only.",
    ]:
        require(token in boundary, f"boundary missing {token}")

    combined = "\n".join([report, boundary, top_doc, gate, json.dumps(packet)])
    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "owner_contacted_by_codex: true",
        '"owner_contacted_by_codex": true',
        "task_candidates_executed: true",
        '"task_candidates_executed": true',
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claims present: " + ", ".join(found))

    csv_lines = PACKET_CSV.read_text(encoding="utf-8").strip().splitlines()
    require(len(csv_lines) == 6, "CSV must have header + 5 rows")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_packet.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_packet.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_packet.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_evidence_sprint_owner_assignment.py",
        "/scripts/saee_commercial_evidence_sprint_owner_assignment_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_sprint_owner_assignment_v0_1", {})
    for key, value in {
        "commercial_evidence_sprint_owner_assignment_v0_1": True,
        "status": "hold_owner_assignment_required",
        "packet_type": "saee_commercial_evidence_sprint_owner_assignment",
        "assignment_scope": "local_owner_assignment_template_for_selected_evidence_sprint",
        "selected_blocker_count": 5,
        "assigned_owner_count": 0,
        "unassigned_owner_count": 5,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "owner_contacted_by_codex": False,
        "blockers_closed_by_assignment": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_SMOKE: PASS "
        "selected_blockers=5 assigned_owner_count=0 execution_authorized=false "
        "blockers_closed_by_assignment=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
