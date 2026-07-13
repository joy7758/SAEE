#!/usr/bin/env python3
"""Smoke check for the SAEE commercial next evidence sprint."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.local.json"
)
REPORT_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.md"
)
CSV_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.csv"
)
BOUNDARY_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint_boundary_audit.md"
)
README_PATH = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_NEXT_EVIDENCE_SPRINT_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_NEXT_EVIDENCE_SPRINT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_NEXT_EVIDENCE_SPRINT_SMOKE: FAIL " + message)


def main() -> int:
    for path in [SPRINT_PATH, REPORT_PATH, CSV_PATH, BOUNDARY_PATH, README_PATH, DOC_PATH, GATE_PATH]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    sprint = json.loads(SPRINT_PATH.read_text(encoding="utf-8"))
    expected_flags = {
        "sprint_type": "saee_commercial_next_evidence_sprint",
        "sprint_status": "hold_human_review_only",
        "sprint_scope": "local_next_evidence_sprint_planning",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "blockers_closed_by_sprint": 0,
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
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
        "customer_data_collected": False,
        "customer_data_processed": False,
        "payment_collected": False,
        "revenue_validated": False,
        "production_claim_added": False,
        "launch_claim_added": False,
        "customer_validation_claim_added": False,
    }
    for key, value in expected_flags.items():
        require(sprint.get(key) == value, f"{key} must be {value}")

    selected = sprint.get("selected_blockers", [])
    require(1 <= len(selected) <= 5, "selected blockers must be 1-5")
    require(sprint.get("selected_blocker_count") == len(selected), "selected count drift")
    require(sprint.get("ready_for_human_review_blocker_count", 0) >= len(selected), "selection too broad")
    require(sprint.get("blockers_ready_to_close") == [], "no blockers ready to close")
    for row in selected:
        require(row.get("dependency_state") == "ready_for_human_review", "row must be ready")
        require(row.get("requires_human_approval") is True, "row must require human approval")
        require(
            row.get("requires_separate_execution_request") is True,
            "row must require separate execution request",
        )
        require(row.get("default_decision") == "hold", "default decision must be hold")
        require(row.get("evidence_collection_allowed_by_sprint") is False, "collection must be false")
        require(row.get("execution_allowed_by_sprint") is False, "execution must be false")
        require(row.get("closure_allowed_by_sprint") is False, "closure must be false")
        require(row.get("first_evidence_items"), "row must keep evidence samples")

    report = REPORT_PATH.read_text(encoding="utf-8")
    gate = GATE_PATH.read_text(encoding="utf-8")
    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
    csv_text = CSV_PATH.read_text(encoding="utf-8")
    for token in [
        "Status: hold_human_review_only.",
        "blockers_closed_by_sprint: 0",
        "execution_authorized: false",
        "production_ready: false",
    ]:
        require(token in report, f"report missing {token}")
    for token in [
        "recommend_for_human_evidence_prioritization: true",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
    ]:
        require(token in gate, f"gate missing {token}")
    for token in [
        "task_candidates_executed: false",
        "blockers_closed_by_sprint: 0",
        "Final boundary decision: local next-evidence planning only.",
    ]:
        require(token in boundary, f"boundary missing {token}")
    require(len(csv_text.strip().splitlines()) == len(selected) + 1, "CSV row count drift")

    forbidden_tokens = [
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
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
    ]
    combined = "\n".join([report, gate, boundary, README_PATH.read_text(encoding="utf-8")])
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/README.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint_boundary_audit.md",
        "/scripts/saee_commercial_next_evidence_sprint.py",
        "/scripts/saee_commercial_next_evidence_sprint_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_next_evidence_sprint_v0_1", {})
    for key, value in {
        "commercial_next_evidence_sprint_v0_1": True,
        "sprint_type": "saee_commercial_next_evidence_sprint",
        "sprint_status": "hold_human_review_only",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "blockers_closed_by_sprint": 0,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_COMMERCIAL_NEXT_EVIDENCE_SPRINT_SMOKE: PASS "
        f"selected_blockers={sprint['selected_blocker_count']} "
        f"blockers_closed_by_sprint={sprint['blockers_closed_by_sprint']} "
        f"production_ready={str(sprint['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
