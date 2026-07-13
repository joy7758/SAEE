#!/usr/bin/env python3
"""Smoke check for the SAEE commercial blocker dependency plan."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan"
PLAN_JSON = PLAN_DIR / "dependency_plan.local.json"
PLAN_MD = PLAN_DIR / "dependency_plan.local.md"
PLAN_CSV = PLAN_DIR / "dependency_plan.local.csv"
README_PATH = PLAN_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [PLAN_JSON, PLAN_MD, PLAN_CSV, README_PATH, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))

    expected_false = [
        "task_candidates_executed",
        "development_permission_granted",
        "execution_authorized",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "customer_contacted",
        "customer_validated",
        "production_ready",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
    ]
    for key in expected_false:
        require(plan.get(key) is False, f"{key} must be false")

    expected_values = {
        "plan_type": "saee_commercial_blocker_dependency_plan",
        "plan_scope": "local_commercial_blocker_dependency_planning",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "planned_blocker_count": 24,
        "open_blocker_count": 24,
        "phase_count": 5,
        "blockers_closed_by_plan": 0,
        "plan_status": "hold",
        "human_review_required": True,
    }
    for key, value in expected_values.items():
        require(plan.get(key) == value, f"{key} must be {value}")

    phases = plan.get("phases", [])
    blockers = plan.get("blockers", [])
    require(len(phases) == 5, "plan must contain 5 phases")
    require(len(blockers) == 24, "plan must contain 24 blockers")
    require(
        sum(int(phase["blocker_count"]) for phase in phases) == 24,
        "phase blocker counts must sum to 24",
    )

    blocker_ids = {item["blocker_id"] for item in blockers}
    required_blockers = {
        "production_identity_provider",
        "oauth_oidc",
        "rbac",
        "tenant_storage_isolation",
        "production_monitoring",
        "external_alert_delivery",
        "on_call_rotation",
        "sla",
        "support_contact",
        "customer_support",
        "formal_security_review",
        "privacy_legal_review",
        "data_processing_agreement",
        "vulnerability_management",
        "pilot_results",
        "customer_validated",
        "pricing_page",
        "payment_provider",
        "invoice_process",
        "tax_review",
        "refund_policy",
        "tenant_billing_isolation",
        "restore_tested",
        "production_restore_policy",
    }
    require(blocker_ids == required_blockers, "plan blocker set must match go/no-go blockers")

    for phase in phases:
        require(phase.get("execution_allowed_by_phase") is False, "phase execution must be false")
        require(phase.get("closure_allowed_by_phase") is False, "phase closure must be false")
        require(phase.get("requires_human_approval") is True, "phase human approval required")
        require(phase.get("default_decision") == "hold", "phase default decision must be hold")

    for item in blockers:
        require(item.get("status") == "open", "each blocker stays open")
        require(item.get("default_decision") == "hold", "each blocker defaults to hold")
        require(item.get("requires_human_approval") is True, "human approval required")
        require(
            item.get("requires_separate_execution_request") is True,
            "separate execution request required",
        )
        require(item.get("execution_allowed_by_plan") is False, "execution not allowed")
        require(item.get("closure_allowed_by_plan") is False, "closure not allowed")
        require(item.get("required_evidence"), "required evidence text present")
        require(item.get("owner_review_lane"), "owner review lane present")
        for dep in item.get("depends_on_blockers", []):
            require(dep in blocker_ids, f"dependency {dep} must be a known blocker")

    with PLAN_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 24, "CSV must contain 24 blocker rows")

    combined_docs = "\n".join(
        [
            PLAN_MD.read_text(encoding="utf-8"),
            README_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "local_commercial_blocker_dependency_planning",
        "production_launch_status: hold",
        "production_blocker_count: 24",
        "planned_blocker_count: 24",
        "phase_count: 5",
        "blockers_closed_by_plan: 0",
        "execution_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

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
        "blockers_closed_by_plan: 1",
        '"blockers_closed_by_plan": 1',
        "external_calls_made: true",
        '"external_calls_made": true',
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_V0_1.md",
        "/docs/strategy/SAEE_COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/README.md",
        "/phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json",
        "/phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.md",
        "/phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.csv",
        "/scripts/saee_commercial_blocker_dependency_plan.py",
        "/scripts/saee_commercial_blocker_dependency_plan_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_blocker_dependency_plan_v0_1", {})
    expected_entry = {
        "status": "hold",
        "commercial_blocker_dependency_plan_v0_1": True,
        "plan_scope": "local_commercial_blocker_dependency_planning",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "planned_blocker_count": 24,
        "open_blocker_count": 24,
        "phase_count": 5,
        "blockers_closed_by_plan": 0,
        "execution_authorized": False,
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
        "SAEE_COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_SMOKE: PASS "
        "production_blockers=24 planned_blockers=24 phase_count=5 "
        "blockers_closed_by_plan=0 production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
