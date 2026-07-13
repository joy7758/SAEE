#!/usr/bin/env python3
"""Smoke check for the SAEE Phase 1 identity and tenant evidence task packet."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task"
TASK_JSON = TASK_DIR / "phase_1_identity_tenant_evidence_task.local.json"
TASK_MD = TASK_DIR / "phase_1_identity_tenant_evidence_task.md"
CHECKLIST_MD = TASK_DIR / "phase_1_identity_tenant_evidence_checklist.md"
ENV_EXAMPLE = TASK_DIR / "phase_1_identity_tenant_evidence.env.example"
README_PATH = TASK_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_TASK_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_EVIDENCE_TASK_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_TASK_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [
        TASK_JSON,
        TASK_MD,
        CHECKLIST_MD,
        ENV_EXAMPLE,
        README_PATH,
        DOC_PATH,
        GATE_PATH,
    ]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    task = json.loads(TASK_JSON.read_text(encoding="utf-8"))
    expected_false = [
        "human_execution_authorized",
        "evidence_collection_authorized",
        "task_candidates_executed",
        "development_permission_granted",
        "phase_1_blockers_ready_to_close",
        "auth_blockers_ready_to_close",
        "tenant_storage_blocker_ready_to_close",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "landing_page_modified",
        "private_core_exposed",
        "product_launched",
        "customer_contacted",
        "customer_validated",
        "production_ready",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "identity_provider_contacted_by_codex",
        "jwks_fetched_by_codex",
        "production_tokens_validated_by_codex",
        "storage_migration_executed",
        "customer_data_processed",
    ]
    for key in expected_false:
        require(task.get(key) is False, f"{key} must be false")

    expected_values = {
        "task_type": "saee_phase_1_identity_tenant_evidence_task",
        "task_scope": "human_reviewed_phase_1_evidence_collection_plan",
        "source_phase_id": "phase_1_identity_and_tenant_boundary",
        "production_launch_status": "hold",
        "target_blocker_count": 4,
        "evidence_item_count": 33,
        "blockers_closed_by_task": 0,
        "task_status": "ready_for_human_review_not_execution",
        "default_decision": "hold",
        "ready_for_human_review": True,
        "human_approval_required": True,
    }
    for key, value in expected_values.items():
        require(task.get(key) == value, f"{key} must be {value}")

    target_blockers = task.get("target_blocker_ids", [])
    require(
        target_blockers
        == [
            "production_identity_provider",
            "oauth_oidc",
            "rbac",
            "tenant_storage_isolation",
        ],
        "target blockers must be the Phase 1 blocker set",
    )
    blockers = task.get("blockers", [])
    require(len(blockers) == 4, "must contain 4 blocker records")
    for blocker in blockers:
        require(blocker.get("status") == "open", "blocker must stay open")
        require(blocker.get("execution_allowed_by_plan") is False, "plan execution false")
        require(blocker.get("closure_allowed_by_plan") is False, "plan closure false")

    evidence_items = task.get("required_evidence_items", [])
    require(len(evidence_items) == 33, "must contain 33 evidence items")
    for item in evidence_items:
        require(item.get("provided") is False, "task packet provides no evidence")
        require(item.get("required_value") is True, "each evidence key requires true")

    docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [TASK_MD, CHECKLIST_MD, README_PATH, DOC_PATH, GATE_PATH]
    )
    required_tokens = [
        "human_reviewed_phase_1_evidence_collection_plan",
        "phase_1_identity_and_tenant_boundary",
        "production_launch_status: hold",
        "target_blocker_count: 4",
        "blockers_closed_by_task: 0",
        "human_execution_authorized: false",
        "evidence_collection_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "production_identity_provider",
        "oauth_oidc",
        "rbac",
        "tenant_storage_isolation",
    ]
    for token in required_tokens:
        require(token in docs, f"docs missing {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "human_execution_authorized: true",
        '"human_execution_authorized": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "blockers_closed_by_task: 1",
        '"blockers_closed_by_task": 1',
        "external_calls_made: true",
        '"external_calls_made": true',
    ]
    found = [token for token in forbidden_tokens if token in docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    env_text = ENV_EXAMPLE.read_text(encoding="utf-8")
    require("SAEE_PRODUCTION_AUTH_EVIDENCE_PATH" in env_text, "env example auth path missing")
    require(
        "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH" in env_text,
        "env example tenant path missing",
    )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_TASK_V0_1.md",
        "/docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_EVIDENCE_TASK_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task/README.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task/phase_1_identity_tenant_evidence_task.local.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task/phase_1_identity_tenant_evidence_task.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task/phase_1_identity_tenant_evidence_checklist.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task/phase_1_identity_tenant_evidence.env.example",
        "/scripts/saee_phase1_identity_tenant_evidence_task.py",
        "/scripts/saee_phase1_identity_tenant_evidence_task_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("phase_1_identity_tenant_evidence_task_v0_1", {})
    expected_entry = {
        "status": "ready_for_human_review_not_execution",
        "phase_1_identity_tenant_evidence_task_v0_1": True,
        "task_scope": "human_reviewed_phase_1_evidence_collection_plan",
        "source_phase_id": "phase_1_identity_and_tenant_boundary",
        "production_launch_status": "hold",
        "target_blocker_count": 4,
        "evidence_item_count": 33,
        "blockers_closed_by_task": 0,
        "human_execution_authorized": False,
        "evidence_collection_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, value in expected_entry.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_TASK_SMOKE: PASS "
        "target_blockers=4 evidence_items=33 blockers_closed_by_task=0 "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
