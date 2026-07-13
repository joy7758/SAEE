#!/usr/bin/env python3
"""Smoke check for the SAEE SLA evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_sla_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_sla_evidence_path.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SLA_EVIDENCE_PATH_SMOKE: FAIL: " + message)


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
    require(result["sla_evidence_path_v0_1"] is True, "path flag true")
    require(
        result["path_type"] == "local_fixture_only_sla_evidence_path",
        "path type changed",
    )
    require(result["path_status"] == "pass_fixture_only", "fixture path must pass")
    require(result["fixture_only"] is True, "fixture only true")
    require(result["real_sla_terms_approved"] is False, "real SLA approval false")
    require(result["real_legal_review_completed"] is False, "real legal review false")
    require(result["builder_status"] == "pass", "builder pass")
    require(result["builder_input_complete"] is True, "fixture input complete")
    require(result["sla_available_for_review"] is True, "SLA available in fixture")
    require(result["sla_blocker_path_proven"] is True, "SLA path proven")
    require(
        result["support_profile_target_blockers_satisfied"] == ["sla"],
        "only sla should be satisfied",
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
    require(result["production_launch_status_after_fixture"] == "hold", "launch hold")
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
        "staffed_support_started",
        "support_case_created",
        "customer_communication_sent",
        "sla_published",
        "sla_approved_by_codex",
        "legal_review_completed_by_codex",
        "support_hours_published_by_codex",
        "response_targets_published_by_codex",
        "on_call_rotation_started",
        "support_operations_started",
        "production_sla_claim_published",
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
        "sla_evidence_path_v0_1: true",
        "path_type: local_fixture_only_sla_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_sla_terms_approved: false",
        "sla_blocker_path_proven: true",
        "support_profile_target_blockers_satisfied_count: 1",
        "support_profile_production_blocker_count: 23",
        "support_profile_production_support_available: false",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_sla_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_support_operations: false",
        "recommend_for_sla_publication: false",
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
        "real_sla_terms_approved: true",
        "\"real_sla_terms_approved\": true",
        "sla_published: true",
        "\"sla_published\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "support_vendor_contacted: true",
        "\"support_vendor_contacted\": true",
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_support_operations: true",
        "recommend_for_sla_publication: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/SLA_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/sla_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/sla_evidence_path_report.md",
        "/docs/strategy/SAEE_SLA_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_sla_evidence_path.py",
        "/scripts/saee_sla_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("sla_evidence_path_v0_1", {})
    expected = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_sla_evidence_path",
        "fixture_only": True,
        "real_sla_terms_approved": False,
        "real_legal_review_completed": False,
        "sla_blocker_path_proven": True,
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
        "sla_published": False,
        "support_operations_started": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_SLA_EVIDENCE_PATH_SMOKE: PASS "
        "fixture_only=true sla_path_proven=true "
        "production_blockers_after_fixture=23 blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
