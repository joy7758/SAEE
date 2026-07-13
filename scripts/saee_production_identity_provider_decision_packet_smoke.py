#!/usr/bin/env python3
"""Smoke test for the SAEE production identity-provider decision packet."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"
OUTPUT_JSON = OUTPUT_DIR / "production_identity_provider_decision_packet.local.json"
OUTPUT_MD = OUTPUT_DIR / "production_identity_provider_decision_packet.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "production_identity_provider_decision_input.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "production_identity_provider_decision_packet_boundary_audit.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_RECOMMENDATION_GATE.md"
)

TARGET_KEYS = {
    "production_identity_provider_selected",
    "identity_provider_admin_owner_named",
    "oidc_issuer_verified",
    "oidc_audience_approved",
    "jwks_rotation_policy_reviewed",
}

REQUIRED_FALSE_FLAGS = [
    "production_identity_provider_available",
    "oauth_oidc_available",
    "rbac_available",
    "production_auth_ready",
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
    "identity_provider_contacted_by_codex",
    "jwks_fetched_by_codex",
    "production_tokens_validated_by_codex",
    "production_auth_enabled",
    "rbac_enforced_in_production",
    "blockers_closed_by_packet",
    "task_candidates_executed",
    "development_permission_granted",
]


def fail(message: str) -> None:
    print(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_SMOKE: FAIL " + message,
        file=sys.stderr,
    )
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_TEMPLATE, OUTPUT_BOUNDARY, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    packet = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    template = json.loads(OUTPUT_TEMPLATE.read_text(encoding="utf-8"))

    require(
        packet.get("packet_type") == "saee_production_identity_provider_decision_packet",
        "wrong packet type",
    )
    require(packet.get("packet_version") == "v0.1", "wrong packet version")
    require(packet.get("status") == "ready_for_human_review_not_execution", "wrong status")
    require(packet.get("blocker_target") == "production_identity_provider", "wrong blocker")
    require(packet.get("human_review_required") is True, "human review required")
    require(
        packet.get("separate_execution_approval_required") is True,
        "separate execution approval required",
    )
    require(set(packet.get("target_auth_evidence_keys", [])) == TARGET_KEYS, "target keys drifted")
    require(len(packet.get("candidate_provider_slots", [])) == 3, "expected three provider slots")

    for flag in REQUIRED_FALSE_FLAGS:
        require(packet.get(flag) is False, f"{flag} must be false")
        require(template.get("boundary_review", {}).get(flag) is False, f"template {flag} false")

    require(
        set(template.get("evidence_review", {})) == TARGET_KEYS,
        "template evidence keys drifted",
    )
    require(
        all(value is False for value in template.get("evidence_review", {}).values()),
        "template must not prefill evidence",
    )
    require(
        all(value == "" for value in template.get("source_notes_by_key", {}).values()),
        "template must not prefill source notes",
    )

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, OUTPUT_BOUNDARY, DOC_PATH, GATE_PATH]
    )
    required_phrases = [
        "ready_for_human_review_not_execution",
        "production_identity_provider",
        "production_identity_provider_available: false",
        "identity_provider_contacted_by_codex: false",
        "jwks_fetched_by_codex: false",
        "production_tokens_validated_by_codex: false",
        "blockers_closed_by_packet: false",
        "recommend_for_blocker_closure: false",
        "No identity provider contacted",
        "No JWKS fetched",
        "No production token validation",
        "No blocker closure",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in combined]
    require(not missing, "missing boundary phrases: " + ", ".join(missing))

    forbidden_tokens = [
        "production_identity_provider_available: true",
        "\"production_identity_provider_available\": true",
        "oauth_oidc_available: true",
        "\"oauth_oidc_available\": true",
        "rbac_available: true",
        "\"rbac_available\": true",
        "production_auth_ready: true",
        "\"production_auth_ready\": true",
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "identity_provider_contacted_by_codex: true",
        "\"identity_provider_contacted_by_codex\": true",
        "jwks_fetched_by_codex: true",
        "\"jwks_fetched_by_codex\": true",
        "production_tokens_validated_by_codex: true",
        "\"production_tokens_validated_by_codex\": true",
        "blockers_closed_by_packet: true",
        "\"blockers_closed_by_packet\": true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]
    searchable = "\n".join([combined, json.dumps(packet), json.dumps(template)])
    found = [token for token in forbidden_tokens if token in searchable]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_packet.local.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_packet.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.template.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_packet_boundary_audit.md",
        "/docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_identity_provider_decision_packet.py",
        "/scripts/saee_production_identity_provider_decision_packet_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_identity_provider_decision_packet_v0_1", {})
    expected_index = {
        "status": "ready_for_human_review_not_execution",
        "packet_type": "saee_production_identity_provider_decision_packet",
        "blocker_target": "production_identity_provider",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "blockers_closed_by_packet": False,
        "development_permission_granted": False,
    }
    for flag, expected in expected_index.items():
        require(entry.get(flag) == expected, f"agent-index {flag} must be {expected}")

    print("SAEE_PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
