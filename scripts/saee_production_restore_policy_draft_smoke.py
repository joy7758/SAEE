#!/usr/bin/env python3
"""Smoke check for the SAEE production restore policy draft."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_DRAFT_V0_1.md"
DRAFT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft.local.json"
)
DRAFT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft.md"
)
BOUNDARY_AUDIT = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft_boundary_audit.md"
)
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_DRAFT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRODUCTION_RESTORE_POLICY_DRAFT_SMOKE: FAIL " + message)


def main() -> int:
    for path in [TOP_DOC, DRAFT_JSON, DRAFT_MD, BOUNDARY_AUDIT, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    draft = json.loads(DRAFT_JSON.read_text(encoding="utf-8"))
    expected = {
        "draft_type": "saee_production_restore_policy_draft",
        "draft_version": "v0.1",
        "draft_status": "draft_not_approved",
        "review_scope": "production_restore_policy_draft_for_human_review_only",
        "blocker_target": "production_restore_policy",
        "draft_policy_available": True,
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "blocker_closure_allowed_by_draft": False,
        "production_restore_policy_available": False,
        "production_restore_policy_approved": False,
        "backup_retention_policy_approved": False,
        "tenant_restore_boundary_approved": False,
        "customer_data_restore_approved": False,
        "production_data_operations_ready": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "production_data_path_modified": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "production_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(draft.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "restore_authority_and_approval",
        "service_scope_and_data_classification",
        "backup_retention_and_encryption",
        "proposed_rpo_rto_targets",
        "tenant_data_scope_and_isolation",
        "customer_data_handling_boundary",
        "credential_and_secret_exclusion",
        "private_core_exclusion",
        "restore_execution_controls",
        "incident_response_handoff",
        "customer_notification_boundary",
        "restore_evidence_retention",
        "post_restore_review",
    }
    require(required_sections <= set(draft.get("policy_sections", [])), "missing policy sections")
    targets = draft.get("proposed_targets", {})
    require(targets.get("target_status") == "proposed_not_approved", "targets must be proposed")
    require(targets.get("backup_retention_days") == 30, "backup retention target changed")
    require(targets.get("public_shell_metadata_rpo_hours") == 24, "RPO target changed")
    require(targets.get("public_shell_metadata_rto_hours") == 4, "RTO target changed")

    combined = "\n".join(
        [
            TOP_DOC.read_text(encoding="utf-8"),
            DRAFT_MD.read_text(encoding="utf-8"),
            BOUNDARY_AUDIT.read_text(encoding="utf-8"),
            GATE.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_restore_policy_draft_v0_1: true",
        "draft_status: draft_not_approved",
        "blocker_target: production_restore_policy",
        "blocker_closure_allowed_by_draft: false",
        "production_restore_policy_available: false",
        "production_restore_policy_approved: false",
        "production_data_operations_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_policy_review: true",
        "recommend_for_production_restore_policy_claim: false",
        "recommend_for_live_restore_execution: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing tokens: " + ", ".join(missing_tokens))

    forbidden_tokens = [
        "production_restore_policy_available: true",
        '"production_restore_policy_available": true',
        "production_restore_policy_approved: true",
        '"production_restore_policy_approved": true',
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "recommend_for_blocker_closure: true",
        "recommend_for_live_restore_execution: true",
        "recommend_for_production_readiness_claim: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_DRAFT_V0_1.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft_boundary_audit.md",
        "/docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_DRAFT_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_restore_policy_draft.py",
        "/scripts/saee_production_restore_policy_draft_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_restore_policy_draft_v0_1", {})
    for key, expected_value in expected.items():
        if key == "generated_at":
            continue
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_DRAFT_SMOKE: PASS "
        "draft_not_approved=true production_restore_policy_available=false "
        "production_ready=false private_core_exposed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
