#!/usr/bin/env python3
"""Smoke test for Phase 1 identity/tenant state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_phase1_identity_tenant_state_reconciliation.py"
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/"
    "phase_1_identity_tenant_state_reconciliation"
)
SUMMARY = OUT_DIR / "phase_1_identity_tenant_state_reconciliation.local.json"
REPORT = OUT_DIR / "phase_1_identity_tenant_state_reconciliation.md"
BOUNDARY = OUT_DIR / "phase_1_identity_tenant_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
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
        "SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION: PASS" in result.stdout,
        "runner did not pass",
    )
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "phase_1_identity_tenant_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_phase1_identity_tenant_state_reconciliation_no_production_enablement_no_closure",
        "status": "ready_for_human_phase1_identity_tenant_review_no_closure",
        "production_identity_provider_ready_for_review": True,
        "oauth_oidc_ready_for_review": True,
        "rbac_ready_for_review": True,
        "tenant_storage_isolation_ready_for_review": True,
        "combined_phase_1_profile_ready": True,
        "ready_for_review_count": 4,
        "human_filled_evidence_item_count": 33,
        "missing_required_evidence_count": 0,
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "recommendation_gate": "conditional",
        "would_recommend_to_potential_customer": "conditional",
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "production_auth_enabled": False,
        "rbac_enforced_in_production": False,
        "tenant_authorization_enabled": False,
        "storage_migration_executed": False,
        "production_database_modified": False,
        "production_tenant_storage_enabled": False,
        "production_tenant_storage_isolated": False,
        "customer_data_processed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_reconciliation": 0,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(payload.get("target_blocker_ids") == [
        "production_identity_provider",
        "oauth_oidc",
        "rbac",
        "tenant_storage_isolation",
    ], "target blockers mismatch")
    require(all(payload.get("gap_matrix_open_by_blocker", {}).values()), "canonical blockers must remain open")
    require(all(payload.get("closure_board_not_ready_by_blocker", {}).values()), "closure board must remain not ready")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Phase 1 Identity/Tenant State Reconciliation",
        "recommendation_gate: conditional",
        "production_auth_enabled=false",
        "rbac_enforced_in_production=false",
        "production_tenant_storage_isolated=false",
        "storage_migration_executed=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "answer: hold_human_phase1_identity_tenant_review_required_no_production_enablement_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "production_auth_enabled=true",
        "rbac_enforced_in_production=true",
        "production_tenant_storage_isolated=true",
        "storage_migration_executed=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_phase1_identity_tenant_state_reconciliation.py",
        "/scripts/saee_phase1_identity_tenant_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    entry = read_json(ROOT / "agent-index.json").get(
        "phase_1_identity_tenant_state_reconciliation_v0_1"
    )
    require(isinstance(entry, dict), "agent-index entry missing")
    for key in [
        "status",
        "target_blocker_ids",
        "production_identity_provider_ready_for_review",
        "oauth_oidc_ready_for_review",
        "rbac_ready_for_review",
        "tenant_storage_isolation_ready_for_review",
        "combined_phase_1_profile_ready",
        "ready_for_review_count",
        "human_filled_evidence_item_count",
        "recommendation_gate",
        "production_auth_enabled",
        "rbac_enforced_in_production",
        "storage_migration_executed",
        "production_tenant_storage_isolated",
        "blockers_closed_by_reconciliation",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Phase 1 Identity/Tenant State Reconciliation v0.1",
        "ready_for_review_count=4",
        "production_identity_provider_ready_for_review=true",
        "oauth_oidc_ready_for_review=true",
        "rbac_ready_for_review=true",
        "tenant_storage_isolation_ready_for_review=true",
        "recommendation_gate=conditional",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    runner_text = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["requests.", "urllib.", "httpx.", "webbrowser", "selenium"]:
        require(forbidden not in runner_text, f"runner must not call external services: {forbidden}")

    print(
        "SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_SMOKE: PASS "
        "status=ready_for_human_phase1_identity_tenant_review_no_closure "
        "ready_for_review_count=4 blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
