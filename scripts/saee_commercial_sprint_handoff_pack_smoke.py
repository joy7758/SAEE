#!/usr/bin/env python3
"""Smoke check for the commercial sprint handoff pack."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_handoff_pack.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_handoff_pack.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_handoff_pack.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_handoff_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HANDOFF_PACK_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HANDOFF_PACK_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HANDOFF_PACK_SMOKE: FAIL: {message}")


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_handoff_pack.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_handoff_pack_v0_1": True,
        "pack_type": "local_human_handoff_index_for_current_commercial_sprint",
        "pack_scope": "selected_blocker_human_input_surfaces_only",
        "status": "ready_for_human_sprint_handoff",
        "selected_blocker_count": 5,
        "handoff_ready_count": 5,
        "human_input_required": True,
        "human_review_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blockers_closed_by_pack": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}, got {payload.get(key)!r}")
    rows = payload.get("rows", [])
    if len(rows) != 5:
        fail("rows must contain five selected blockers")
    ids = [row.get("blocker_id") for row in rows]
    if ids != [
        "support_contact",
        "pricing_page",
        "formal_security_review",
        "production_restore_policy",
        "production_monitoring",
    ]:
        fail(f"unexpected blocker order: {ids}")
    if any(row.get("handoff_status") != "ready_for_human_input" for row in rows):
        fail("all handoff rows must be ready_for_human_input")
    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 5:
        fail("CSV must contain five rows")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    for token in [
        "commercial_sprint_handoff_pack_v0_1: true",
        "status: ready_for_human_sprint_handoff",
        "selected_blocker_count: 5",
        "handoff_ready_count: 5",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_pack: 0",
        "production_ready: false",
        "answer: recommend",
        "recommend_for_human_handoff: true",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        if token not in combined:
            fail(f"missing token {token}")
    print(
        "SAEE_COMMERCIAL_SPRINT_HANDOFF_PACK_SMOKE: PASS "
        "status=ready_for_human_sprint_handoff selected_blocker_count=5 "
        "handoff_ready_count=5 evidence_collection_authorized=false "
        "blockers_closed_by_pack=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
