#!/usr/bin/env python3
"""Smoke check for the tenant storage approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_phase1_identity_tenant_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    input_template,
)
from scripts.saee_tenant_storage_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    TARGET_EVIDENCE_KEYS,
    build_validation,
)


VALIDATOR_SCRIPT = ROOT / "scripts/saee_tenant_storage_approval_input_validator.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: " + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    data = input_template()
    data["input_status"] = "human_review_complete"
    data["human_reviewer_name"] = "Human Tenant Storage Owner"
    data["review_date"] = "2026-07-05"
    data["evidence_source_notes"] = "Fixture-only tenant storage evidence review note."
    evidence_review = data["evidence_review"]
    source_notes = data["source_notes_by_key"]
    require(isinstance(evidence_review, dict), "template evidence_review dict")
    require(isinstance(source_notes, dict), "template source_notes dict")
    for key in TARGET_EVIDENCE_KEYS:
        evidence_review[key] = True
        source_notes[key] = f"Fixture source note for {key}."
    if unsafe:
        data["tenant_storage_isolated"] = True
        data["storage_behavior_modified"] = True
        data["migration_executed"] = True
        boundary = data["boundary_review"]
        require(isinstance(boundary, dict), "template boundary_review dict")
        boundary["tenant_storage_isolated"] = True
        boundary["storage_behavior_modified"] = True
        boundary["migration_executed"] = True
    return data


def main() -> None:
    require(VALIDATOR_SCRIPT.exists(), "validator script missing")
    default_run = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    expected_default = {
        "validator_type": "saee_tenant_storage_approval_input_validator",
        "validation_status": "hold",
        "input_complete": False,
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "tenant_storage_approved_by_validator": False,
        "tenant_storage_available_by_validator": False,
        "tenant_storage_isolation_evidence_complete_by_validator": False,
        "production_tenant_storage_evidence_built_by_validator": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "production_tenant_storage_enabled": False,
        "multi_tenant_production_ready": False,
        "tenant_authorization_enabled": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "production_database_modified": False,
        "storage_behavior_modified": False,
        "migration_executed": False,
        "live_customer_data_migrated": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "development_permission_granted": False,
    }
    for key, value in expected_default.items():
        require(default_summary.get(key) == value, f"default {key} must be {value}")
    require(default_summary["missing_required_text_fields"], "default misses text")
    require(default_summary["missing_evidence_review"], "default misses review")
    require(default_summary["missing_source_notes"], "default misses notes")
    require(DEFAULT_OUTPUT_PATH.exists(), "default validation output missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_path = tmp / "complete_input.json"
        unsafe_path = tmp / "unsafe_input.json"
        write_json(complete_path, complete_input())
        write_json(unsafe_path, complete_input(unsafe=True))
        complete_summary = build_validation(complete_path)
        unsafe_summary = build_validation(unsafe_path)

    require(complete_summary["validation_status"] == "pass", "complete input must pass")
    require(complete_summary["input_complete"] is True, "complete input complete")
    require(complete_summary["builder_ready"] is True, "complete input builder ready")
    require(
        complete_summary["blockers_closed_by_validator"] == 0,
        "complete input closes no blockers",
    )
    require(
        complete_summary["production_ready"] is False,
        "complete input does not make production ready",
    )
    require(
        complete_summary["tenant_storage_isolated"] is False,
        "complete input does not claim tenant storage isolation",
    )
    require(unsafe_summary["validation_status"] == "stop", "unsafe input stops")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe violations")
    require(unsafe_summary["builder_ready"] is False, "unsafe not builder ready")
    for flag in INPUT_FORBIDDEN_TRUE_KEYS:
        require(
            unsafe_summary.get(flag) is not True,
            f"unsafe summary must not publish true flag {flag}",
        )

    subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "tenant_storage_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_tenant_storage_input_pre_builder_check",
        "target_blocker_ids: tenant_storage_isolation",
        "blockers_closed_by_validator: 0",
        "tenant_storage_approved_by_validator: false",
        "tenant_storage_available_by_validator: false",
        "tenant_storage_isolation_evidence_complete_by_validator: false",
        "production_tenant_storage_evidence_built_by_validator: false",
        "tenant_storage_isolated: false",
        "production_tenant_storage_isolated: false",
        "production_tenant_storage_enabled: false",
        "multi_tenant_production_ready: false",
        "customer_data_processed: false",
        "storage_behavior_modified: false",
        "migration_executed: false",
        "production_ready: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_storage_behavior_change: false",
        "recommend_for_storage_migration: false",
        "recommend_for_customer_data_processing: false",
        "recommend_for_tenant_storage_enablement: false",
        "recommend_for_tenant_storage_isolation_claim: false",
        "recommend_for_blocker_closure: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/tenant_storage_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/tenant_storage_approval_input_validation.md",
        "/docs/strategy/SAEE_TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_tenant_storage_approval_input_validator.py",
        "/scripts/saee_tenant_storage_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("tenant_storage_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "hold",
        "validator_type": "saee_tenant_storage_approval_input_validator",
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "tenant_storage_approved_by_validator": False,
        "tenant_storage_available_by_validator": False,
        "tenant_storage_isolation_evidence_complete_by_validator": False,
        "production_tenant_storage_evidence_built_by_validator": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "production_tenant_storage_enabled": False,
        "multi_tenant_production_ready": False,
        "customer_data_processed": False,
        "storage_behavior_modified": False,
        "migration_executed": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=hold builder_ready=false blockers_closed_by_validator=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
