#!/usr/bin/env python3
"""Smoke check for the SAEE commercial launch blocker work order."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_launch_blocker_work_order import build_work_order


JSON_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.json"
MD_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "work order JSON missing")
    require(MD_PATH.exists(), "work order Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    artifact = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    current = build_work_order()
    require(artifact == current, "stored work order must match current go/no-go blockers")
    require(artifact["work_order_type"] == "commercial_launch_blocker_work_order", "wrong type")
    require(artifact["work_order_status"] == "hold", "work order must hold")
    require(artifact["commercial_status"] == "hold", "commercial status must hold")
    require(artifact["production_launch_status"] == "hold", "production launch must hold")
    require(artifact["production_blocker_count"] >= 20, "expected explicit production blockers")
    require(len(artifact["blockers"]) == artifact["production_blocker_count"], "blocker count mismatch")
    require(artifact["blockers_closed"] == 0, "no blockers should be closed")
    require(
        artifact["locally_preparable_blocker_count"] == 4,
        "expected four locally preparable blockers",
    )
    require(
        artifact["external_dependency_blocker_count"] == 20,
        "expected twenty external dependency blockers",
    )
    require(
        artifact["engineering_implementation_blocker_count"] == 9,
        "expected nine engineering implementation blockers",
    )
    require(
        artifact["locally_preparable_blockers"]
        == ["rbac", "tenant_storage_isolation", "tenant_billing_isolation", "restore_tested"],
        "locally preparable blocker list changed",
    )
    require(
        artifact["resolution_lane_counts"]
        == {
            "customer_validation_evidence": 2,
            "engineering_local_design": 4,
            "engineering_with_external_service": 5,
            "human_operations_evidence": 5,
            "legal_business_approval": 8,
        },
        "resolution lane counts changed",
    )
    require(
        artifact["sequence_group_counts"]
        == {
            "billing_and_packaging": 6,
            "customer_validation_and_launch": 2,
            "data_operations": 2,
            "identity_and_tenant_boundary": 4,
            "operations_resilience": 3,
            "support_security_legal": 7,
        },
        "sequence group counts changed",
    )
    require(artifact["human_approval_required"] is True, "human approval required")
    require(artifact["task_candidates_executed"] is False, "must not execute tasks")
    require(artifact["development_permission_granted"] is False, "must not grant development permission")
    require(artifact["runtime_modified"] is False, "must not modify runtime")
    require(artifact["backend_modified"] is False, "must not modify backend")
    require(artifact["kernel_modified"] is False, "must not modify kernel")
    require(artifact["api_schema_modified"] is False, "must not modify API schema")
    require(artifact["private_core_exposed"] is False, "must not expose private core")
    require(artifact["product_launched"] is False, "must not launch product")
    require(artifact["customer_contacted"] is False, "must not contact customers")
    require(artifact["customer_validated"] is False, "must not claim customer validation")
    require(artifact["production_ready"] is False, "must not claim production readiness")
    require(artifact["public_sdk_released"] is False, "must not release SDK")
    require(artifact["external_calls_made"] is False, "must not call external services")
    require(artifact["external_model_api_called"] is False, "must not call external model APIs")
    require(artifact["external_ai_assistant_tested"] is False, "must not test external assistants")

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
    blocker_ids = {item["blocker_id"] for item in artifact["blockers"]}
    missing = sorted(required_blockers - blocker_ids)
    require(not missing, "missing blockers: " + ", ".join(missing))

    for item in artifact["blockers"]:
        require(item["status"] == "open", f"{item['blocker_id']} must be open")
        require(item["requires_human_approval"] is True, f"{item['blocker_id']} must require approval")
        require(
            item["execution_allowed_by_this_work_order"] is False,
            f"{item['blocker_id']} must not allow execution",
        )
        require(
            item["can_close_without_evidence"] is False,
            f"{item['blocker_id']} must require evidence",
        )
        require("resolution_lane" in item, f"{item['blocker_id']} missing resolution lane")
        require("sequence_group" in item, f"{item['blocker_id']} missing sequence group")
        require(
            isinstance(item.get("can_prepare_locally_now"), bool),
            f"{item['blocker_id']} local prep flag must be boolean",
        )
        require(
            isinstance(item.get("external_dependency_required"), bool),
            f"{item['blocker_id']} external dependency flag must be boolean",
        )
        require(
            isinstance(item.get("engineering_implementation_required"), bool),
            f"{item['blocker_id']} engineering flag must be boolean",
        )

    combined_docs = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "work_order_status: hold",
        "commercial_status: hold",
        "production_launch_status: hold",
        "locally_preparable_blocker_count: 4",
        "external_dependency_blocker_count: 20",
        "engineering_implementation_blocker_count: 9",
        "## Resolution Lane Counts",
        "engineering_local_design: 4",
        "## Locally Preparable Blockers",
        "task_candidates_executed: false",
        "development_permission_granted: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined_docs]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.md",
        "/phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.json",
        "/docs/strategy/SAEE_COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_launch_blocker_work_order.py",
        "/scripts/saee_commercial_launch_blocker_work_order_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_launch_blocker_work_order_v0_1", {})
    expected = {
        "status": "hold",
        "work_order_type": "commercial_launch_blocker_work_order",
        "production_blocker_count": artifact["production_blocker_count"],
        "blockers_closed": 0,
        "locally_preparable_blocker_count": 4,
        "external_dependency_blocker_count": 20,
        "engineering_implementation_blocker_count": 9,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "human_approval_required": True,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_SMOKE: PASS "
        f"production_blockers={artifact['production_blocker_count']} "
        "blockers_closed=0 production_ready=false product_launched=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
