#!/usr/bin/env python3
"""Smoke check for the SAEE combined data-operations evidence profile."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_data_operations_evidence_profile import (
    DEFAULT_COMBINED_EVIDENCE,
    DEFAULT_PROFILE_JSON,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_profile,
)
from scripts.saee_production_restore_policy_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    build_from_input,
)
from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_data_operations_evidence import RESTORE_POLICY_KEYS


PROFILE_SCRIPT = ROOT / "scripts/saee_data_operations_evidence_profile.py"
RESTORE_TESTED_EVIDENCE = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.from_restore_tested.local.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_DATA_OPERATIONS_EVIDENCE_PROFILE_SMOKE: FAIL: " + message)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_policy_input(*, unsafe: bool = False) -> dict[str, object]:
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
            "combined profile validation."
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


def go_no_go(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(PROFILE_SCRIPT.exists(), "profile script missing")
    require(RESTORE_TESTED_EVIDENCE.exists(), "restore-tested evidence missing")

    default_run = subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_profile = json.loads(default_run.stdout)
    require(default_profile["profile_status"] == "hold", "default profile status hold")
    require(
        default_profile["restore_tested_available_for_go_no_go"] is True,
        "default profile must keep restore-tested signal",
    )
    require(
        default_profile["production_restore_policy_available_for_go_no_go"] is False,
        "default restore policy unavailable",
    )
    require(
        default_profile["production_data_operations_ready"] is False,
        "default data operations not ready",
    )
    require(default_profile["profile_satisfied_production_checks"] == 1, "default one satisfied")
    require(default_profile["profile_production_blocker_count"] == 23, "default 23 blockers")
    require(default_profile["data_operations_satisfied_blockers"] == ["restore_tested"], "default satisfied list")
    require(default_profile["blockers_closed_by_profile"] == 0, "default closes no blockers")
    require(DEFAULT_PROFILE_JSON.exists(), "default profile JSON missing")
    require(DEFAULT_COMBINED_EVIDENCE.exists(), "default combined evidence missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_policy_input_path = tmp / "complete_restore_policy_input.json"
        complete_policy_output_path = tmp / "complete_restore_policy_builder.json"
        complete_policy_evidence_path = tmp / "complete_restore_policy_evidence.json"
        complete_profile_path = tmp / "complete_data_ops_profile.json"
        complete_combined_path = tmp / "complete_combined_data_ops_evidence.json"
        unsafe_policy_input_path = tmp / "unsafe_restore_policy_input.json"
        unsafe_policy_output_path = tmp / "unsafe_restore_policy_builder.json"
        unsafe_policy_evidence_path = tmp / "unsafe_restore_policy_evidence.json"
        unsafe_profile_path = tmp / "unsafe_data_ops_profile.json"
        unsafe_combined_path = tmp / "unsafe_combined_data_ops_evidence.json"

        write_json(complete_policy_input_path, complete_policy_input())
        write_json(unsafe_policy_input_path, complete_policy_input(unsafe=True))
        build_from_input(
            complete_policy_input_path,
            complete_policy_output_path,
            complete_policy_evidence_path,
            write_documentation=False,
        )
        build_from_input(
            unsafe_policy_input_path,
            unsafe_policy_output_path,
            unsafe_policy_evidence_path,
            write_documentation=False,
        )
        complete_profile = build_profile(
            RESTORE_TESTED_EVIDENCE,
            complete_policy_evidence_path,
            complete_profile_path,
            complete_combined_path,
        )
        unsafe_profile = build_profile(
            RESTORE_TESTED_EVIDENCE,
            unsafe_policy_evidence_path,
            unsafe_profile_path,
            unsafe_combined_path,
        )
        complete_go_no_go = go_no_go(complete_combined_path)

    require(complete_profile["profile_status"] == "pass", "complete fixture profile pass")
    require(
        complete_profile["restore_tested_available_for_go_no_go"] is True,
        "complete profile restore tested",
    )
    require(
        complete_profile["production_restore_policy_available_for_go_no_go"] is True,
        "complete profile restore policy available",
    )
    require(
        complete_profile["production_data_operations_ready"] is True,
        "complete profile data operations ready",
    )
    require(
        complete_profile["data_operations_satisfied_blockers"]
        == ["restore_tested", "production_restore_policy"],
        "complete data ops blockers satisfied",
    )
    require(
        complete_go_no_go["satisfied_production_checks"] == 2,
        "complete profile satisfies two go/no-go checks",
    )
    require(
        complete_go_no_go["production_blocker_count"] == 22,
        "complete profile leaves 22 blockers",
    )
    require(complete_go_no_go["commercial_status"] == "hold", "commercial remains hold")
    require(complete_go_no_go["production_ready"] is False, "production ready false")
    require(
        complete_profile["blockers_closed_by_profile"] == 0,
        "complete profile closes no blockers by itself",
    )
    require(unsafe_profile["profile_status"] == "stop", "unsafe profile stops")
    require(
        unsafe_profile["source_boundary_violation_count"] > 0,
        "unsafe profile records source violation",
    )
    require(
        unsafe_profile["production_data_operations_ready"] is False,
        "unsafe data operations not ready",
    )

    subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT)],
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
        "data_operations_evidence_profile_v0_1: true",
        "profile_scope: combined_restore_tested_and_restore_policy_evidence_to_go_no_go",
        "default_profile_status: hold",
        "restore_tested_available_for_go_no_go: true",
        "production_restore_policy_available_for_go_no_go: false",
        "production_data_operations_ready: false",
        "profile_production_blocker_count: 23",
        "blockers_closed_by_profile: 0",
        "answer: conditional",
        "recommend_for_human_go_no_go_review: true",
        "recommend_for_blocker_closure_by_profile_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_live_restore: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/DATA_OPERATIONS_EVIDENCE_PROFILE_V0_1.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence_profile.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.combined_profile.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence_profile_report.md",
        "/docs/strategy/SAEE_DATA_OPERATIONS_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md",
        "/scripts/saee_data_operations_evidence_profile.py",
        "/scripts/saee_data_operations_evidence_profile_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("data_operations_evidence_profile_v0_1", {})
    expected = {
        "status": "local_combined_data_operations_profile_hold",
        "profile_scope": "combined_restore_tested_and_restore_policy_evidence_to_go_no_go",
        "restore_tested_available_for_go_no_go": True,
        "production_restore_policy_available_for_go_no_go": False,
        "production_data_operations_ready": False,
        "profile_satisfied_production_checks": 1,
        "profile_production_blocker_count": 23,
        "blockers_closed_by_profile": 0,
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
        "SAEE_DATA_OPERATIONS_EVIDENCE_PROFILE_SMOKE: PASS "
        "default_restore_tested=true default_policy=false default_blockers=23 "
        "complete_fixture_data_ops_ready=true complete_blockers=22 "
        "blockers_closed_by_profile=0"
    )


if __name__ == "__main__":
    main()
