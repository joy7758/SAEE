#!/usr/bin/env python3
"""Smoke check for SAEE Production Data Operations Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_V0_1.json"
MD_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(data["production_data_operations_requirements_v0_1"] is True, "requirements flag true")
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")

    false_flags = [
        "production_data_operations_implemented",
        "restore_tested",
        "production_restore_tested",
        "production_restore_policy_available",
        "production_restore_policy_approved",
        "restore_to_live_path_enabled",
        "tenant_restore_available",
        "customer_data_restore_ready",
        "backup_encryption_review_completed",
        "rto_rpo_targets_approved",
        "disaster_recovery_runbook_available",
        "production_data_operations_ready",
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
        "production_data_path_modified",
        "live_restore_performed",
        "credentials_restored",
        "private_core_restored",
    ]
    for flag in false_flags:
        require(data[flag] is False, f"{flag} false")

    blockers = set(data["data_ops_blockers_covered_as_requirements"])
    require(blockers == {"restore_tested", "production_restore_policy"}, "data ops blockers mismatch")

    required_restore_controls = {
        "production_like_backup_source_defined",
        "isolated_restore_environment_defined",
        "restore_to_live_path_forbidden_without_approval",
        "restore_integrity_checks_defined",
        "rto_rpo_targets_defined",
        "tenant_restore_scope_defined",
        "rollback_after_restore_drill_defined",
        "restore_test_result_record_required",
    }
    require(
        required_restore_controls <= set(data["required_restore_test_controls"]),
        "missing restore test controls",
    )

    required_policy_sections = {
        "restore_authority_and_approval",
        "backup_retention_and_encryption",
        "tenant_data_scope_and_isolation",
        "customer_data_handling_boundary",
        "credential_and_secret_exclusion",
        "private_core_exclusion",
        "incident_response_handoff",
        "customer_notification_boundary",
        "restore_evidence_retention",
        "post_restore_review",
    }
    require(
        required_policy_sections <= set(data["required_production_restore_policy_sections"]),
        "missing restore policy sections",
    )

    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_data_operations_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_data_operations_implemented: false",
        "restore_tested: false",
        "production_restore_tested: false",
        "production_restore_policy_available: false",
        "production_restore_policy_approved: false",
        "restore_to_live_path_enabled: false",
        "tenant_restore_available: false",
        "customer_data_restore_ready: false",
        "production_data_operations_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "live_restore_performed: false",
        "answer: conditional",
        "recommend_for_requirements_definition: true",
        "recommend_for_restore_execution: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_data_operations_requirements.py",
        "/scripts/saee_production_data_operations_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_data_operations_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_data_operations_requirements_v0_1": True,
        "production_data_operations_implemented": False,
        "restore_tested": False,
        "production_restore_tested": False,
        "production_restore_policy_available": False,
        "restore_to_live_path_enabled": False,
        "tenant_restore_available": False,
        "customer_data_restore_ready": False,
        "production_data_operations_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true restore_tested=false "
        "production_restore_policy_available=false live_restore_performed=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
