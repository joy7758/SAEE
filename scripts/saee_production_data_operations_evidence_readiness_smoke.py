#!/usr/bin/env python3
"""Smoke check for SAEE Production Data Operations Evidence Readiness v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_data_operations_evidence import (
    evaluate_production_data_operations_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_SMOKE: FAIL: {message}")


def write_data_ops_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "data_operations_evidence_type": "production_data_operations_evidence",
        "production_like_restore_test_plan_approved": True,
        "isolated_restore_environment_used": True,
        "restore_integrity_checks_passed": True,
        "rto_rpo_observed_and_recorded": True,
        "tenant_scope_validated_if_customer_data_exists": True,
        "restore_test_report_reviewed": True,
        "production_restore_policy_approved": True,
        "backup_retention_policy_approved": True,
        "tenant_restore_boundary_approved": True,
        "credential_secret_exclusion_reviewed": True,
        "customer_notification_boundary_approved": True,
        "incident_response_handoff_approved": True,
        "production_ready": unsafe,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_data_operations_evidence(load_settings({}))
    require(
        local["production_data_operations_evidence_type"]
        == "production_data_operations_evidence_readiness",
        "wrong evidence type",
    )
    require(local["production_data_operations_evidence_readiness_v0_1"] is True, "readiness flag")
    require(local["status"] == "hold", "default evidence status must hold")
    require(local["data_operations_evidence_path_configured"] is False, "default path false")
    require(local["restore_tested"] is False, "default restore tested false")
    require(local["production_restore_tested"] is False, "default production restore false")
    require(
        local["production_restore_policy_available"] is False,
        "default production restore policy false",
    )
    require(local["production_restore_policy_approved"] is False, "default policy approval false")
    require(local["production_data_operations_ready"] is False, "default data ops ready false")
    require(local["production_ready"] is False, "default production false")
    require(local["customer_validated"] is False, "default customer validation false")
    require(local["product_launched"] is False, "default launch false")
    require(local["private_core_exposed"] is False, "default private core false")
    require(local["external_calls_made"] is False, "default external calls false")
    require(local["customer_contacted"] is False, "default customer contacted false")
    require(local["production_data_path_modified"] is False, "default data path false")
    require(local["live_restore_performed"] is False, "default live restore false")
    require(local["credentials_restored"] is False, "default credentials restored false")
    require(local["private_core_restored"] is False, "default private core restored false")

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "DATA_OPERATIONS_EVIDENCE.json"
        write_data_ops_evidence(evidence_path)
        settings = load_settings(
            {
                "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(evidence_path),
            }
        )
        configured = evaluate_production_data_operations_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_DATA_OPERATIONS_EVIDENCE.json"
        write_data_ops_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_data_operations_evidence(
            load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(unsafe_path)})
        )

    require(configured["status"] == "pass", "complete data ops evidence should pass")
    require(configured["restore_tested"] is True, "restore tested evidence true")
    require(configured["production_restore_tested"] is True, "production restore tested true")
    require(configured["production_restore_policy_available"] is True, "restore policy true")
    require(configured["production_restore_policy_approved"] is True, "restore policy approved true")
    require(configured["production_data_operations_ready"] is True, "data operations ready true")
    require(configured["production_ready"] is False, "evidence pass must not claim production")
    require(configured["customer_validated"] is False, "evidence pass must not claim customers")
    require(configured["product_launched"] is False, "evidence pass must not claim launch")
    require(configured["external_calls_made"] is False, "evidence pass must not call external")
    require(configured["customer_contacted"] is False, "evidence pass must not contact customers")
    require(configured["live_restore_performed"] is False, "evidence pass must not restore live")

    blocked = blocker_ids(go_no_go)
    for blocker in ["restore_tested", "production_restore_policy"]:
        require(blocker not in blocked, f"{blocker} should be satisfied by data ops evidence")
    require(go_no_go["commercial_status"] == "hold", "data ops evidence alone must not launch")
    require(go_no_go["production_launch_status"] == "hold", "production launch must still hold")
    require(go_no_go["production_ready"] is False, "go/no-go must keep production false")
    require(go_no_go["customer_validated"] is False, "go/no-go must keep customer validation false")
    require(go_no_go["product_launched"] is False, "go/no-go must keep launch false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go must keep private core false")

    require(unsafe["status"] == "stop", "unsafe evidence must stop")
    require("production_ready" in unsafe["boundary_violations"], "unsafe evidence must detect boundary")
    require(unsafe["production_ready"] is False, "unsafe output must still preserve production false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    for token in [
        "production_data_operations_evidence_readiness_v0_1: true",
        "default_status: hold",
        "data_operations_evidence_path_configured_default: false",
        "restore_tested_default: false",
        "production_restore_tested_default: false",
        "production_restore_policy_available_default: false",
        "production_data_operations_ready_default: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "live_restore_performed: false",
        "answer: conditional",
        "recommend_for_production_launch: false",
    ]:
        require(token in doc or token in gate, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_data_operations_evidence.py",
        "/scripts/saee_production_data_operations_evidence_readiness.py",
        "/scripts/saee_production_data_operations_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_data_operations_evidence_readiness_v0_1", {})
    expected = {
        "status": "production_data_operations_evidence_readiness_hold",
        "production_data_operations_evidence_readiness_v0_1": True,
        "data_operations_evidence_path_configured_default": False,
        "restore_tested_default": False,
        "production_restore_tested_default": False,
        "production_restore_policy_available_default": False,
        "production_data_operations_ready_default": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "live_restore_performed": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "data_ops_blockers_satisfied_by_evidence=true production_launch_status=hold "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
