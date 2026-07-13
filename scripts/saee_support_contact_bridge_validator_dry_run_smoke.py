#!/usr/bin/env python3
"""Smoke check for support contact bridge validator dry run v0.1."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_contact_bridge_validator_dry_run.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
OUT_JSON = OUT_DIR / "support_contact_bridge_validator_dry_run.local.json"
OUT_MD = OUT_DIR / "support_contact_bridge_validator_dry_run.md"
OUT_BOUNDARY = OUT_DIR / "support_contact_bridge_validator_dry_run_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_BRIDGE_VALIDATOR_DRY_RUN_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_BRIDGE_VALIDATOR_DRY_RUN_RECOMMENDATION_GATE.md"

PASS_PREFIX = "SAEE_SUPPORT_CONTACT_BRIDGE_VALIDATOR_DRY_RUN_SMOKE: PASS"
FAIL_PREFIX = "SAEE_SUPPORT_CONTACT_BRIDGE_VALIDATOR_DRY_RUN_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    for path in [OUT_JSON, OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "support_contact_bridge_validator_dry_run_v0_1": True,
        "dry_run_type": "fixture_only_bridge_to_validator_compatibility_check",
        "dry_run_scope": "local_tempfile_fixture_validator_compatibility_only",
        "status": "pass_fixture_only",
        "target_blocker_id": "support_contact",
        "fixture_only": True,
        "combined_input_fixture_used": True,
        "temp_exports_only": True,
        "local_validators_invoked": True,
        "first_owner_validator_validation_status": "pass",
        "first_owner_assignment_complete": True,
        "support_contact_approval_validation_status": "pass",
        "support_contact_approval_input_complete": True,
        "support_contact_approval_builder_ready": True,
        "ready_for_evidence_collection": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blockers_closed_by_dry_run": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "human_real_input_required": True,
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
        require(data.get(key) == value, f"{key} must be {value}")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    for token in [
        "support_contact_bridge_validator_dry_run_v0_1: true",
        "status: pass_fixture_only",
        "dry_run_scope: local_tempfile_fixture_validator_compatibility_only",
        "fixture_only: true",
        "local_validators_invoked: true",
        "first_owner_validator_validation_status: pass",
        "support_contact_approval_validation_status: pass",
        "ready_for_evidence_collection: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_dry_run: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: recommend",
        "recommend_for_fixture_only_validator_compatibility: true",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        require(token in combined, "missing doc token " + token)
    print(
        PASS_PREFIX
        + " status=pass_fixture_only fixture_only=true local_validators_invoked=true "
        + "blockers_closed_by_dry_run=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
