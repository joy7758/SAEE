#!/usr/bin/env python3
"""Smoke check for SAEE commercial evidence sprint sequencer v0.1."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_evidence_sprint_sequencer.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_sprint_sequencer"
OUTPUT_JSON = OUTPUT_DIR / "commercial_evidence_sprint_sequencer.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_evidence_sprint_sequencer.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_evidence_sprint_sequencer.csv"
OUTPUT_BOUNDARY = OUTPUT_DIR / "commercial_evidence_sprint_sequencer_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER_RECOMMENDATION_GATE.md"

PASS_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER_SMOKE: PASS"
FAIL_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_SEQUENCER_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, OUTPUT_BOUNDARY, README_PATH, DOC_PATH, GATE_PATH]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    data = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_evidence_sprint_sequencer_v0_1": True,
        "sequencer_type": "saee_commercial_evidence_sprint_sequencer",
        "sequencer_scope": "local_read_only_commercial_evidence_sprint_ordering",
        "status": "hold_human_sprint_selection_required",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "total_required_evidence_item_count": 149,
        "total_missing_production_evidence_count": 112,
        "sequenced_blocker_count": 24,
        "top_candidate_count": 5,
        "current_next_human_input_blocker_id": "formal_security_review",
        "closure_candidate_count": 0,
        "blockers_closed_by_sequencer": 0,
        "recommended_default_decision": "hold",
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
        "owner_assigned_by_codex": False,
        "sprint_execution_authorized": False,
        "sprint_evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
    }
    for key, value in expected.items():
        require(data.get(key) == value, f"{key} must be {value}")

    require(
        data.get("selection_bucket_counts")
        == {
            "blocked_by_dependency": 15,
            "ready_engineering_review": 3,
            "ready_external_human_review": 6,
        },
        "selection bucket counts changed",
    )
    require(data.get("engineering_required_candidate_count") == 9, "engineering count changed")
    require(data.get("external_dependency_candidate_count") == 19, "external dependency count changed")

    top = data.get("top_sprint_candidates", [])
    require(len(top) == 5, "top_sprint_candidates must contain five rows")
    require(
        top[0].get("blocker_id") == "formal_security_review",
        "first candidate must be formal_security_review",
    )
    require(
        top[0].get("selection_bucket") == "ready_external_human_review",
        "formal_security_review must remain ready for external human review",
    )
    for row in top:
        require(row.get("default_decision") == "hold", "top rows default decision must be hold")
        require(row.get("execution_allowed_by_sequencer") is False, "execution must be false")
        require(row.get("evidence_collection_authorized") is False, "evidence collection must be false")
        require(
            row.get("blocker_closure_allowed_by_sequencer") is False,
            "blocker closure must be false",
        )

    sequenced = data.get("sequenced_blockers", [])
    require(len(sequenced) == 24, "sequenced_blockers must contain 24 rows")
    require(
        all(row.get("requires_human_approval") is True for row in sequenced),
        "all sequenced rows must require human approval",
    )

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 24, "CSV must contain 24 rows")
    require(
        rows[0].get("blocker_id") == "formal_security_review",
        "CSV first row must be formal_security_review",
    )
    require(rows[0].get("execution_allowed_by_sequencer") == "False", "CSV execution must be false")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, OUTPUT_BOUNDARY, README_PATH, DOC_PATH, GATE_PATH]
    )
    for token in [
        "commercial_evidence_sprint_sequencer_v0_1: true",
        "status: hold_human_sprint_selection_required",
        "sequencer_scope: local_read_only_commercial_evidence_sprint_ordering",
        "sequenced_blocker_count: 24",
        "top_candidate_count: 5",
        "current_next_human_input_blocker_id: formal_security_review",
        "closure_candidate_count: 0",
        "blockers_closed_by_sequencer: 0",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "sprint_execution_authorized: false",
        "sprint_evidence_collection_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: recommend",
        "recommend_for_sprint_selection_guidance: true",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        require(token in combined, "missing doc token " + token)

    forbidden = [
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
        "sprint_execution_authorized: true",
        '"sprint_execution_authorized": true',
        "sprint_evidence_collection_authorized: true",
        '"sprint_evidence_collection_authorized": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
        "recommend_for_production_readiness_claim: true",
    ]
    data_text = json.dumps(data, sort_keys=True)
    found = [token for token in forbidden if token in combined or token in data_text]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print(
        PASS_PREFIX
        + " status=hold_human_sprint_selection_required sequenced_blockers=24 "
        + "top_candidate=formal_security_review blockers_closed_by_sequencer=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
