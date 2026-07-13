#!/usr/bin/env python3
"""Smoke check for the production IdP evidence-builder request template."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = (
    ROOT
    / "scripts/saee_production_identity_provider_evidence_builder_request_template.py"
)
OUTPUT_TEMPLATE = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_evidence_builder_request.template.json"
)
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_evidence_builder_request.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_evidence_builder_request.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_evidence_builder_request.csv"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE_SMOKE: FAIL: "
            + message
        )


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE: PASS"
        in result.stdout,
        "runner did not print PASS",
    )
    for path in [OUTPUT_TEMPLATE, OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, TOP_DOC, GATE]:
        require(path.exists(), f"{path} missing")

    template = read_json(OUTPUT_TEMPLATE)
    require(
        template.get("template_type")
        == "saee_production_identity_provider_evidence_builder_request",
        "template type mismatch",
    )
    require(template.get("request_status") == "template_not_filled", "template status")
    require(
        template.get("target_builder") == "scripts/saee_phase1_identity_tenant_evidence_builder.py",
        "target builder mismatch",
    )
    acknowledgements = template.get("human_acknowledgements")
    require(isinstance(acknowledgements, dict), "acknowledgements missing")
    require(len(acknowledgements) == 11, "acknowledgement count mismatch")
    require(
        all(value is False for value in acknowledgements.values()),
        "acknowledgements must default false",
    )

    payload = read_json(OUTPUT_JSON)
    expected = {
        "production_identity_provider_evidence_builder_request_template_v0_1": True,
        "request_template_type": "saee_production_identity_provider_evidence_builder_request_template",
        "request_template_version": "v0.1",
        "request_scope": "separate_human_approval_for_phase1_identity_tenant_evidence_builder",
        "status": "hold_human_evidence_builder_request_required",
        "target_blocker_id": "production_identity_provider",
        "target_builder": "scripts/saee_phase1_identity_tenant_evidence_builder.py",
        "request_template_ready": True,
        "required_item_count": 15,
        "completed_item_count": 0,
        "missing_item_count": 15,
        "blockers_closed_by_request_template": 0,
        "request_approved": False,
        "approval_input_validator_passed": False,
        "human_filled_input_available": False,
        "evidence_builder_execution_authorized": False,
        "evidence_builder_executed": False,
        "phase1_builder_output_created_by_request": False,
        "production_identity_provider_selected_by_codex": False,
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
        "external_calls_made_by_codex": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 15, "CSV must contain 15 completion rows")
    require(sum(1 for row in rows if row["complete"] == "true") == 0, "no row complete")
    for item_id in [f"PIDP-EBR-{index:03d}" for index in range(1, 16)]:
        require(any(row["item_id"] == item_id for row in rows), "missing " + item_id)

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE]
    )
    for token in [
        "production_identity_provider_evidence_builder_request_template_v0_1: true",
        "hold_human_evidence_builder_request_required",
        "request_template_ready: true",
        "request_approved: false",
        "evidence_builder_execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_request_template: 0",
        "production_ready: false",
        "answer: recommend",
        "recommend_for_separate_human_evidence_builder_request: true",
        "recommend_for_builder_execution: false",
        "recommend_for_production: false",
    ]:
        require(token in combined, "missing token " + token)

    runner = RUNNER.read_text(encoding="utf-8")
    for forbidden in [
        "os.environ",
        "os.getenv",
        "getenv(",
        "environ[",
        "requests.",
        "urllib",
        "subprocess.run",
    ]:
        require(forbidden not in runner, "runner contains forbidden token " + forbidden)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE_V0_1.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.template.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.local.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.csv",
        "/docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_identity_provider_evidence_builder_request_template.py",
        "/scripts/saee_production_identity_provider_evidence_builder_request_template_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("production_identity_provider_evidence_builder_request_template_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key, value in expected.items():
        if key in {"request_template_type", "request_template_version", "request_scope"}:
            continue
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print("SAEE_PRODUCTION_IDENTITY_PROVIDER_EVIDENCE_BUILDER_REQUEST_TEMPLATE_SMOKE: PASS")


if __name__ == "__main__":
    main()
