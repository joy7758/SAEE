#!/usr/bin/env python3
"""Smoke check for the SAEE customer-support evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_customer_support_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_customer_support_evidence_path.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CUSTOMER_SUPPORT_EVIDENCE_PATH_SMOKE: FAIL: " + message)


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    run = subprocess.run(
        [sys.executable, str(RUNNER), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    result = json.loads(run.stdout)
    require(result["customer_support_evidence_path_v0_1"] is True, "path flag true")
    require(
        result["path_type"] == "local_fixture_only_customer_support_evidence_path",
        "path type changed",
    )
    require(result["path_status"] == "pass_fixture_only", "fixture path must pass")
    require(result["fixture_only"] is True, "fixture only true")
    require(result["real_customer_support_configured"] is False, "real support false")
    require(result["staffed_support_started"] is False, "staffed support false")
    require(result["support_case_created"] is False, "support case false")
    require(result["customer_communication_sent"] is False, "customer communication false")
    require(result["builder_status"] == "pass", "builder pass")
    require(result["builder_input_complete"] is True, "fixture input complete")
    require(
        result["customer_support_available_for_review"] is True,
        "customer support available in fixture",
    )
    require(
        result["customer_support_blocker_path_proven"] is True,
        "customer support path proven",
    )
    require(
        result["support_profile_target_blockers_satisfied"] == ["customer_support"],
        "only customer_support should be satisfied",
    )
    require(
        result["support_profile_target_blockers_satisfied_count"] == 1,
        "one support blocker satisfied in fixture",
    )
    require(
        result["support_profile_production_blocker_count"] == 23,
        "fixture should leave 23 production blockers",
    )
    require(
        result["support_profile_production_support_available"] is False,
        "production support remains false",
    )
    require(result["commercial_status_after_fixture"] == "hold", "commercial hold")
    require(
        result["production_launch_status_after_fixture"] == "hold",
        "launch hold",
    )
    require(
        result["production_blocker_count_after_fixture"] == 23,
        "go/no-go leaves 23 blockers",
    )
    require(result["blockers_closed_by_path"] == 0, "path closes no blockers")
    for key in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "customer_contacted",
        "support_vendor_contacted",
        "support_contact_published",
        "support_contact_test_sent",
        "sla_published",
        "on_call_rotation_started",
        "support_operations_started",
        "customer_support_claim_published",
    ]:
        require(result[key] is False, f"{key} must be false")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    persisted = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    require(persisted == result, "persisted output differs")

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "customer_support_evidence_path_v0_1: true",
        "path_type: local_fixture_only_customer_support_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_customer_support_configured: false",
        "customer_support_blocker_path_proven: true",
        "support_profile_target_blockers_satisfied_count: 1",
        "support_profile_production_blocker_count: 23",
        "support_profile_production_support_available: false",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_customer_support_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_support_operations: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)
    for token in [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "staffed_support_started: true",
        "\"staffed_support_started\": true",
        "support_case_created: true",
        "\"support_case_created\": true",
        "customer_communication_sent: true",
        "\"customer_communication_sent\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "support_vendor_contacted: true",
        "\"support_vendor_contacted\": true",
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_support_operations: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/CUSTOMER_SUPPORT_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/customer_support_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/customer_support_evidence_path_report.md",
        "/docs/strategy/SAEE_CUSTOMER_SUPPORT_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_customer_support_evidence_path.py",
        "/scripts/saee_customer_support_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("customer_support_evidence_path_v0_1", {})
    expected = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_customer_support_evidence_path",
        "fixture_only": True,
        "real_customer_support_configured": False,
        "customer_support_blocker_path_proven": True,
        "support_profile_target_blockers_satisfied_count": 1,
        "support_profile_production_blocker_count": 23,
        "production_support_available": False,
        "blockers_closed_by_path": 0,
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
        "support_vendor_contacted": False,
        "staffed_support_started": False,
        "support_case_created": False,
        "customer_communication_sent": False,
        "support_operations_started": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_CUSTOMER_SUPPORT_EVIDENCE_PATH_SMOKE: PASS "
        "fixture_only=true customer_support_path_proven=true "
        "production_blockers_after_fixture=23 blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
