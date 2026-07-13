#!/usr/bin/env python3
"""Smoke check for the production identity-provider approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_identity_provider_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_validation,
)
from scripts.saee_production_identity_provider_decision_packet import (
    FALSE_FLAGS,
    TARGET_KEYS,
)


VALIDATOR_SCRIPT = (
    ROOT / "scripts/saee_production_identity_provider_approval_input_validator.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: "
            + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    boundary = {flag: False for flag in FALSE_FLAGS}
    if unsafe:
        boundary["identity_provider_contacted_by_codex"] = True
    return {
        "template_type": "saee_production_identity_provider_decision_input",
        "template_version": "v0.1",
        "input_status": "human_review_complete",
        "human_reviewer_name": "Human Security Owner",
        "review_date": "2026-07-05",
        "selected_provider_name": "Example OIDC Provider",
        "decision_summary": "Fixture-only smoke input for validator coverage.",
        "evidence_review": {key: True for key in TARGET_KEYS},
        "source_notes_by_key": {
            key: f"Fixture source note for {key}." for key in TARGET_KEYS
        },
        "boundary_review": boundary,
        "candidate_provider_slots": [
            {
                "slot_id": "idp_candidate_a",
                "provider_name": "Example OIDC Provider",
                "oidc_supported": True,
                "admin_owner_named": True,
                "issuer_reviewed": True,
                "audience_reviewed": True,
                "jwks_rotation_reviewed": True,
                "human_source_note": "Fixture-only source note.",
            },
            {
                "slot_id": "idp_candidate_b",
                "provider_name": "",
                "oidc_supported": None,
                "admin_owner_named": None,
                "issuer_reviewed": None,
                "audience_reviewed": None,
                "jwks_rotation_reviewed": None,
                "human_source_note": "",
            },
            {
                "slot_id": "idp_candidate_c",
                "provider_name": "",
                "oidc_supported": None,
                "admin_owner_named": None,
                "issuer_reviewed": None,
                "audience_reviewed": None,
                "jwks_rotation_reviewed": None,
                "human_source_note": "",
            },
        ],
    }


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
        "validator_type": "saee_production_identity_provider_approval_input_validator",
        "validation_status": "hold",
        "input_complete": False,
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "production_identity_provider_selected_by_validator": False,
        "production_identity_provider_approved_by_validator": False,
        "production_identity_provider_available_by_validator": False,
        "production_auth_evidence_built_by_validator": False,
        "codex_contacted_identity_provider": False,
        "codex_fetched_jwks": False,
        "codex_validated_production_tokens": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "production_auth_enabled": False,
        "rbac_enforced_in_production": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
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
        complete_summary["production_auth_ready"] is False,
        "complete input does not make auth ready",
    )
    require(unsafe_summary["validation_status"] == "stop", "unsafe input stops")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe violations")
    require(unsafe_summary["builder_ready"] is False, "unsafe not builder ready")

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
        "production_identity_provider_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_production_identity_provider_input_pre_builder_check",
        "target_blocker_ids: production_identity_provider",
        "blockers_closed_by_validator: 0",
        "production_identity_provider_selected_by_validator: false",
        "production_identity_provider_approved_by_validator: false",
        "production_identity_provider_available_by_validator: false",
        "production_auth_evidence_built_by_validator: false",
        "codex_contacted_identity_provider: false",
        "codex_fetched_jwks: false",
        "codex_validated_production_tokens: false",
        "production_identity_provider_available: false",
        "oauth_oidc_available: false",
        "rbac_available: false",
        "production_auth_ready: false",
        "production_ready: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_identity_provider_selection: false",
        "recommend_for_identity_provider_contact: false",
        "recommend_for_jwks_fetch: false",
        "recommend_for_token_validation: false",
        "recommend_for_auth_enablement: false",
        "recommend_for_blocker_closure: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.template.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_approval_input_validation.md",
        "/docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_identity_provider_approval_input_validator.py",
        "/scripts/saee_production_identity_provider_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_identity_provider_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "hold",
        "validator_type": "saee_production_identity_provider_approval_input_validator",
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "production_identity_provider_selected_by_validator": False,
        "production_identity_provider_approved_by_validator": False,
        "production_identity_provider_available_by_validator": False,
        "production_auth_evidence_built_by_validator": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
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
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=hold builder_ready=false blockers_closed_by_validator=0 "
        "production_auth_ready=false"
    )


if __name__ == "__main__":
    main()
