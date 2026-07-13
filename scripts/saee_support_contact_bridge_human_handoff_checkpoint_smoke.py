#!/usr/bin/env python3
"""Smoke check for support-contact bridge human handoff checkpoint."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
OUT_JSON = OUT_DIR / "support_contact_bridge_human_handoff_checkpoint.local.json"
OUT_MD = OUT_DIR / "support_contact_bridge_human_handoff_checkpoint.md"
OUT_BOUNDARY = OUT_DIR / "support_contact_bridge_human_handoff_checkpoint_boundary_audit.md"
TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT_SMOKE: FAIL: {message}")


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/saee_support_contact_bridge_human_handoff_checkpoint.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "support_contact_bridge_human_handoff_checkpoint_v0_1": True,
        "checkpoint_type": "human_only_support_contact_bridge_handoff",
        "checkpoint_scope": "local_human_handoff_status_and_commands_only",
        "status": "ready_for_human_bridge_input",
        "target_blocker_id": "support_contact",
        "validator_dry_run_status": "pass_fixture_only",
        "validator_dry_run_fixture_only": True,
        "local_validators_invoked_in_fixture": True,
        "first_owner_validator_fixture_status": "pass",
        "support_contact_approval_validator_fixture_status": "pass",
        "human_input_required": True,
        "human_real_input_required": True,
        "ready_for_evidence_collection": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blockers_closed_by_checkpoint": 0,
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
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}, got {payload.get(key)!r}")
    if payload.get("missing_prerequisites") != []:
        fail("missing_prerequisites must be empty")
    if len(payload.get("post_fill_commands", [])) != 4:
        fail("post_fill_commands must contain four commands")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    for token in [
        "support_contact_bridge_human_handoff_checkpoint_v0_1: true",
        "status: ready_for_human_bridge_input",
        "human_input_required: true",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_checkpoint: 0",
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
        "SAEE_SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT_SMOKE: PASS "
        "status=ready_for_human_bridge_input human_input_required=true "
        "evidence_collection_authorized=false blockers_closed_by_checkpoint=0 "
        "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
