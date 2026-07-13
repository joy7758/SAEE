#!/usr/bin/env python3
"""Smoke check for the production identity-provider input completion helper."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_identity_provider_approval_input_validator import (
    build_validation,
)

HELPER = ROOT / "scripts/saee_production_identity_provider_input_completion_helper.py"
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_input_completion.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_input_completion.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_input_completion.csv"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_SMOKE: FAIL: "
            + message
        )


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def main() -> None:
    require(HELPER.exists(), "helper missing")
    result = subprocess.run(
        [sys.executable, str(HELPER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER: PASS"
        in result.stdout,
        "helper did not print PASS",
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        generated_input = (
            Path(tmpdir) / "production_identity_provider_input.human_filled.local.json"
        )
        generated = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--generate-input",
                "--output-input",
                str(generated_input),
                "--human-reviewer-name",
                "Human Security Owner",
                "--review-date",
                "2026-07-06",
                "--selected-provider-name",
                "Example OIDC Provider",
                "--decision-summary",
                "Fixture-only human-provided identity-provider input for smoke coverage.",
                "--selected-provider-slot",
                "idp_candidate_a",
                "--candidate-source-note",
                "Fixture-only candidate source note supplied by smoke test.",
                "--confirm-production-identity-provider-selected",
                "true",
                "--confirm-identity-provider-admin-owner-named",
                "true",
                "--confirm-oidc-issuer-verified",
                "true",
                "--confirm-oidc-audience-approved",
                "true",
                "--confirm-jwks-rotation-policy-reviewed",
                "true",
                "--source-note-production-identity-provider-selected",
                "Fixture source note: provider selected by human owner.",
                "--source-note-identity-provider-admin-owner-named",
                "Fixture source note: admin owner named.",
                "--source-note-oidc-issuer-verified",
                "Fixture source note: issuer reviewed.",
                "--source-note-oidc-audience-approved",
                "Fixture source note: audience approved.",
                "--source-note-jwks-rotation-policy-reviewed",
                "Fixture source note: JWKS rotation policy reviewed.",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        require("generated_input=" in generated.stdout, "generated input not reported")
        generated_payload = read_json(generated_input)
        require(
            generated_payload.get("input_status")
            == "human_filled_identity_provider_local_input",
            "generated input status mismatch",
        )
        generated_validation = build_validation(generated_input)
        require(
            generated_validation["validation_status"] == "pass",
            "generated input must pass validator",
        )
        require(generated_validation["builder_ready"] is True, "generated builder ready")
        require(
            generated_validation["blockers_closed_by_validator"] == 0,
            "generated input closes no blockers",
        )
        require(
            generated_validation["production_ready"] is False,
            "generated input does not claim production ready",
        )
        require(
            generated_validation["codex_contacted_identity_provider"] is False,
            "generated input does not contact identity provider",
        )
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, TOP_DOC, GATE]:
        require(path.exists(), f"{path} missing")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "production_identity_provider_input_completion_helper_v0_1": True,
        "helper_type": "saee_production_identity_provider_input_completion_helper",
        "helper_version": "v0.1",
        "helper_scope": "local_identity_provider_human_input_completion_sheet",
        "target_blocker_id": "production_identity_provider",
        "status": "hold_human_identity_provider_input_required",
        "completion_sheet_ready": True,
        "input_complete": False,
        "builder_ready": False,
        "required_item_count": 15,
        "completed_item_count": 0,
        "missing_item_count": 15,
        "blockers_closed_by_helper": 0,
        "generated_input_supported": True,
        "production_identity_provider_selected": False,
        "production_identity_provider_available": False,
        "production_identity_provider_configured": False,
        "identity_provider_contacted": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "tokens_validated_in_production": False,
        "production_auth_enabled": False,
        "production_auth_ready": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "rbac_enforced_in_production": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "development_permission_granted": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
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
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(
        payload.get("missing_required_text_fields")
        == [
            "human_reviewer_name",
            "review_date",
            "selected_provider_name",
            "decision_summary",
        ],
        "missing text fields mismatch",
    )
    require(
        payload.get("missing_evidence_review")
        == [
            "production_identity_provider_selected",
            "identity_provider_admin_owner_named",
            "oidc_issuer_verified",
            "oidc_audience_approved",
            "jwks_rotation_policy_reviewed",
        ],
        "missing evidence review mismatch",
    )
    require(
        payload.get("missing_source_notes")
        == [
            "production_identity_provider_selected",
            "identity_provider_admin_owner_named",
            "oidc_issuer_verified",
            "oidc_audience_approved",
            "jwks_rotation_policy_reviewed",
        ],
        "missing source notes mismatch",
    )
    require(
        payload.get("selected_candidate_missing_fields") == ["selected_provider_slot"],
        "selected candidate missing fields mismatch",
    )

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 15, "completion CSV must have 15 rows")
    row_ids = {row["item_id"] for row in rows}
    for item_id in [
        "PIDP-TEXT-human_reviewer_name",
        "PIDP-TEXT-review_date",
        "PIDP-TEXT-selected_provider_name",
        "PIDP-TEXT-decision_summary",
        "PIDP-EVIDENCE-production_identity_provider_selected",
        "PIDP-EVIDENCE-identity_provider_admin_owner_named",
        "PIDP-EVIDENCE-oidc_issuer_verified",
        "PIDP-EVIDENCE-oidc_audience_approved",
        "PIDP-EVIDENCE-jwks_rotation_policy_reviewed",
        "PIDP-NOTE-production_identity_provider_selected",
        "PIDP-NOTE-identity_provider_admin_owner_named",
        "PIDP-NOTE-oidc_issuer_verified",
        "PIDP-NOTE-oidc_audience_approved",
        "PIDP-NOTE-jwks_rotation_policy_reviewed",
        "PIDP-SLOT-selected_provider_slot",
    ]:
        require(item_id in row_ids, f"missing CSV row {item_id}")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE]
    )
    for token in [
        "production_identity_provider_input_completion_helper_v0_1: true",
        "hold_human_identity_provider_input_required",
        "production_identity_provider_selected: false",
        "identity_provider_contacted: false",
        "jwks_fetched: false",
        "production_auth_enabled: false",
        "production_ready: false",
        "generated_input_supported: true",
        "answer: recommend",
        "recommend_for_local_human_input_completion: true",
        "recommend_for_production: false",
    ]:
        require(token in combined, f"missing token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_V0_1.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_input_completion.local.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_input_completion.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_input_completion.csv",
        "/docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_identity_provider_input_completion_helper.py",
        "/scripts/saee_production_identity_provider_input_completion_helper_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("production_identity_provider_input_completion_helper_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key, value in expected.items():
        if key in {
            "helper_type",
            "helper_version",
            "helper_scope",
            "required_item_count",
            "completed_item_count",
            "missing_item_count",
        }:
            continue
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print("SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_SMOKE: PASS")


if __name__ == "__main__":
    main()
