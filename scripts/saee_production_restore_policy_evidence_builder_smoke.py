#!/usr/bin/env python3
"""Smoke check for the SAEE production-restore-policy evidence builder."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_data_operations_evidence import (
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
    evaluate_production_data_operations_evidence,
)
from scripts.saee_production_restore_policy_evidence_builder import (
    DEFAULT_DATA_OPS_OUTPUT_PATH,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    INPUT_FORBIDDEN_TRUE_KEYS,
    REPORT_PATH,
    build_from_input,
)


BUILDER_SCRIPT = ROOT / "scripts/saee_production_restore_policy_evidence_builder.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER_SMOKE: FAIL: "
            + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    policy_review = {key: True for key in RESTORE_POLICY_KEYS}
    source_notes = {
        key: f"Human-reviewed production restore policy source note for {key}."
        for key in RESTORE_POLICY_KEYS
    }
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["production_ready"] = True
    return {
        "template_type": "saee_production_restore_policy_approval_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-04",
        "data_operations_owner": "Fixture Data Operations Owner",
        "security_owner": "Fixture Security Owner",
        "privacy_legal_owner": "Fixture Privacy Legal Owner",
        "incident_response_owner": "Fixture Incident Response Owner",
        "decision_summary": (
            "Fixture-only production restore policy approval evidence for "
            "deterministic smoke validation."
        ),
        "policy_evidence_review": policy_review,
        "source_notes_by_key": source_notes,
        "boundary_review": boundary_review,
        "policy_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://production-restore-policy/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in RESTORE_POLICY_KEYS
        ],
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "policy_approved_by_codex": False,
        "restore_policy_published_by_codex": False,
        "live_restore_authorized_by_codex": False,
        "customer_notification_sent_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_restore_policy_claim_published": False,
        "production_restore_policy_effective_for_customers": False,
    }


def data_ops_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_data_operations_evidence(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(BUILDER_SCRIPT.exists(), "builder script missing")

    default_run = subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    require(default_summary["status"] == "hold", "default builder status must hold")
    require(default_summary["input_complete"] is False, "default input must be incomplete")
    require(
        default_summary["production_restore_policy_available_for_review"] is False,
        "default restore policy must not be available",
    )
    require(
        default_summary["production_data_operations_ready"] is False,
        "default production data operations must be false",
    )
    require(default_summary["blockers_closed_by_builder"] == 0, "no default closure")
    require(DEFAULT_INPUT_PATH.exists(), "default input template missing")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    require(DEFAULT_DATA_OPS_OUTPUT_PATH.exists(), "default data ops evidence missing")

    default_evidence = json.loads(DEFAULT_DATA_OPS_OUTPUT_PATH.read_text(encoding="utf-8"))
    for key in RESTORE_TEST_KEYS + RESTORE_POLICY_KEYS:
        require(default_evidence.get(key) is False, f"default evidence {key} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_input_path = tmp / "complete_restore_policy_input.json"
        complete_output_path = tmp / "complete_builder_output.json"
        complete_data_ops_path = tmp / "complete_data_ops_evidence.json"
        unsafe_input_path = tmp / "unsafe_restore_policy_input.json"
        unsafe_output_path = tmp / "unsafe_builder_output.json"
        unsafe_data_ops_path = tmp / "unsafe_data_ops_evidence.json"

        write_json(complete_input_path, complete_input())
        write_json(unsafe_input_path, complete_input(unsafe=True))

        complete_summary = build_from_input(
            complete_input_path,
            complete_output_path,
            complete_data_ops_path,
            write_documentation=False,
        )
        unsafe_summary = build_from_input(
            unsafe_input_path,
            unsafe_output_path,
            unsafe_data_ops_path,
            write_documentation=False,
        )
        complete_readiness = data_ops_readiness(complete_data_ops_path)
        unsafe_readiness = data_ops_readiness(unsafe_data_ops_path)
        complete_go_no_go = commercial_status(complete_data_ops_path)

    unsatisfied_ids = {
        item["blocker_id"] for item in complete_go_no_go["unsatisfied_blockers"]
    }
    require(complete_summary["status"] == "pass", "complete fixture summary pass")
    require(complete_summary["input_complete"] is True, "complete fixture input complete")
    require(
        complete_summary["production_restore_policy_available_for_review"] is True,
        "complete fixture restore policy available",
    )
    require(
        complete_summary["production_data_operations_ready"] is False,
        "complete fixture still not full data operations",
    )
    require(
        complete_readiness["production_restore_policy_available"] is True,
        "complete readiness restore policy available",
    )
    require(complete_readiness["restore_tested"] is False, "restore tested remains separate")
    require(complete_readiness["status"] == "hold", "complete data ops readiness hold")
    require(
        complete_go_no_go["satisfied_production_checks"] == 1,
        "complete fixture satisfies one go/no-go blocker",
    )
    require(
        complete_go_no_go["production_blocker_count"] == 23,
        "complete fixture leaves 23 blockers",
    )
    require(
        "production_restore_policy" not in unsatisfied_ids,
        "production restore policy blocker should be satisfied by fixture evidence",
    )
    require("restore_tested" in unsatisfied_ids, "restore tested remains unsatisfied")
    require(
        complete_summary["blockers_closed_by_builder"] == 0,
        "complete fixture closes no blockers by itself",
    )
    require(unsafe_summary["status"] == "stop", "unsafe fixture stops")
    require(unsafe_summary["input_boundary_violation_count"] > 0, "unsafe violations")
    require(
        unsafe_readiness["production_restore_policy_available"] is False,
        "unsafe restore policy remains unavailable",
    )

    subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "production_restore_policy_evidence_builder_v0_1: true",
        "builder_scope: human_filled_production_restore_policy_to_production_data_operations_evidence",
        "required_evidence_item_count: 6",
        "- status: hold",
        "default_output_status: hold",
        "blockers_closed_by_builder: 0",
        "production_restore_policy_available: false",
        "production_data_operations_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "recommend_for_production_launch: false",
        "recommend_for_live_restore: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.template.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.from_restore_policy.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_evidence_builder_report.md",
        "/scripts/saee_production_restore_policy_evidence_builder.py",
        "/scripts/saee_production_restore_policy_evidence_builder_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_restore_policy_evidence_builder_v0_1", {})
    expected = {
        "status": "local_builder_available_default_hold",
        "builder_scope": (
            "human_filled_production_restore_policy_to_production_data_operations_evidence"
        ),
        "production_restore_policy_available_for_review": False,
        "production_restore_policy_available": False,
        "restore_tested": False,
        "production_data_operations_ready": False,
        "blockers_closed_by_builder": 0,
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
        "production_data_path_modified": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_restore_policy_available=true "
        "restore_tested=false production_data_operations_ready=false "
        "blockers_closed_by_builder=0"
    )


if __name__ == "__main__":
    main()
