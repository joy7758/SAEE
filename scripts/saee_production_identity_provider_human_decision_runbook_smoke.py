#!/usr/bin/env python3
"""Smoke check for the production identity-provider human decision runbook."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_production_identity_provider_human_decision_runbook.py"
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_human_decision_runbook.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_human_decision_runbook.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/"
    "production_identity_provider_human_decision_runbook.csv"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_SMOKE: FAIL: "
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
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK: PASS"
        in result.stdout,
        "runner did not print PASS",
    )
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, TOP_DOC, GATE]:
        require(path.exists(), f"{path} missing")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "production_identity_provider_human_decision_runbook_v0_1": True,
        "runbook_type": "saee_production_identity_provider_human_decision_runbook",
        "runbook_version": "v0.1",
        "runbook_scope": "local_human_identity_provider_decision_procedure",
        "status": "hold_human_identity_provider_decision_required",
        "target_blocker_id": "production_identity_provider",
        "runbook_ready": True,
        "step_count": 6,
        "completion_helper_available": True,
        "explicit_input_generation_supported": True,
        "approval_input_validator_available": True,
        "separate_evidence_builder_request_required": True,
        "human_decision_recorded": False,
        "human_filled_input_generated": False,
        "identity_provider_selected_by_codex": False,
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
        "blockers_closed_by_runbook": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 6, "CSV must contain six runbook steps")
    row_ids = {row["step_id"] for row in rows}
    for step_id in [
        "PIDP-HUMAN-001",
        "PIDP-HUMAN-002",
        "PIDP-HUMAN-003",
        "PIDP-HUMAN-004",
        "PIDP-HUMAN-005",
        "PIDP-HUMAN-006",
    ]:
        require(step_id in row_ids, f"missing step {step_id}")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE]
    )
    for token in [
        "production_identity_provider_human_decision_runbook_v0_1: true",
        "hold_human_identity_provider_decision_required",
        "runbook_ready: true",
        "human_decision_recorded: false",
        "human_filled_input_generated: false",
        "identity_provider_selected_by_codex: false",
        "identity_provider_contacted: false",
        "jwks_fetched: false",
        "production_auth_enabled: false",
        "production_ready: false",
        "blockers_closed_by_runbook: false",
        "answer: recommend",
        "recommend_for_human_identity_provider_decision_guidance: true",
        "recommend_for_production: false",
    ]:
        require(token in combined, f"missing token {token}")

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
        "/phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_V0_1.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_human_decision_runbook.local.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_human_decision_runbook.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_human_decision_runbook.csv",
        "/docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_identity_provider_human_decision_runbook.py",
        "/scripts/saee_production_identity_provider_human_decision_runbook_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("production_identity_provider_human_decision_runbook_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key, value in expected.items():
        if key in {"runbook_type", "runbook_version", "runbook_scope"}:
            continue
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print("SAEE_PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_SMOKE: PASS")


if __name__ == "__main__":
    main()
