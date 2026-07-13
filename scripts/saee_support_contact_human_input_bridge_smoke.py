#!/usr/bin/env python3
"""Smoke check for SAEE support contact human input bridge v0.1."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_contact_human_input_bridge.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
OUT_JSON = OUT_DIR / "support_contact_human_input_bridge.local.json"
OUT_MD = OUT_DIR / "support_contact_human_input_bridge.md"
OUT_CSV = OUT_DIR / "support_contact_human_input_bridge.csv"
OUT_BOUNDARY = OUT_DIR / "support_contact_human_input_bridge_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_RECOMMENDATION_GATE.md"

PASS_PREFIX = "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_SMOKE: PASS"
FAIL_PREFIX = "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, OUT_README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "support_contact_human_input_bridge_v0_1": True,
        "bridge_type": "saee_support_contact_human_input_bridge",
        "bridge_scope": "local_human_input_consolidation_only",
        "status": "hold_combined_human_input_required",
        "commercial_status": "hold",
        "target_blocker_id": "support_contact",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "first_owner_required_field_count": 5,
        "support_contact_required_metadata_field_count": 4,
        "support_contact_required_evidence_key_count": 5,
        "candidate_contact_slot_count": 2,
        "minimum_candidate_contact_slot_count": 1,
        "combined_input_row_count": 16,
        "completed_input_row_count": 0,
        "human_input_required": True,
        "human_review_required": True,
        "requires_separate_validator": True,
        "requires_separate_evidence_collection_request": True,
        "requires_separate_blocker_closure_approval": True,
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
        "support_contact_configured_by_codex": False,
        "support_contact_published_by_codex": False,
        "support_contact_tested_by_codex": False,
        "support_contact_available": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "support_vendor_contacted": False,
        "customer_facing_support_contact_configured": False,
        "customer_support_available": False,
        "production_support_available": False,
        "production_support_claim_published": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_bridge": 0,
    }
    for key, value in expected.items():
        require(data.get(key) == value, f"{key} must be {value}")

    rows = data.get("input_rows", [])
    require(len(rows) == 16, "input_rows must contain 16 rows")
    require(sum(1 for row in rows if row["input_group"] == "first_owner_input") == 5, "first owner row count")
    require(
        sum(1 for row in rows if row["input_group"] == "support_contact_decision_metadata") == 4,
        "metadata row count",
    )
    require(
        sum(1 for row in rows if row["input_group"] == "support_contact_evidence_review") == 5,
        "evidence row count",
    )
    require(
        sum(1 for row in rows if row["input_group"] == "support_contact_candidate_slot") == 2,
        "candidate slot row count",
    )
    require(all(row["codex_may_fill"] is False for row in rows), "codex_may_fill must be false")

    with OUT_CSV.open(newline="", encoding="utf-8") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 16, "CSV must contain 16 rows")
    require(csv_rows[0]["input_group"] == "first_owner_input", "CSV first row group changed")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_BOUNDARY, OUT_README, TOP_DOC, GATE]
    )
    for token in [
        "support_contact_human_input_bridge_v0_1: true",
        "status: hold_combined_human_input_required",
        "bridge_scope: local_human_input_consolidation_only",
        "target_blocker_id: support_contact",
        "combined_input_row_count: 16",
        "completed_input_row_count: 0",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_bridge: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: recommend",
        "recommend_for_human_input_consolidation: true",
        "recommend_for_support_contact_configuration: false",
        "recommend_for_support_contact_publication: false",
        "recommend_for_support_testing: false",
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
        "support_contact_configured: true",
        '"support_contact_configured": true',
        "support_contact_published: true",
        '"support_contact_published": true',
        "support_contact_test_performed: true",
        '"support_contact_test_performed": true',
        "recommend_for_support_contact_configuration: true",
        "recommend_for_support_contact_publication: true",
        "recommend_for_support_testing: true",
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
        + " status=hold_combined_human_input_required combined_input_row_count=16 "
        + "blockers_closed_by_bridge=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
