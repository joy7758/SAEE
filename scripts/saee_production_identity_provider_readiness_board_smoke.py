#!/usr/bin/env python3
"""Smoke check for the SAEE production identity-provider readiness board."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOARD_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.local.json"
)
BOARD_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.md"
)
BOARD_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.csv"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_SMOKE: FAIL: " + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path | str) -> str:
    p = ROOT / path if isinstance(path, str) else path
    return p.read_text(encoding="utf-8")


def main() -> None:
    for path in [BOARD_JSON, BOARD_MD, BOARD_CSV, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path}")

    board = json.loads(read(BOARD_JSON))
    expected = {
        "production_identity_provider_readiness_board_v0_1": True,
        "board_type": "saee_production_identity_provider_readiness_board",
        "board_scope": "local_production_identity_provider_blocker_readiness_review",
        "target_blocker_id": "production_identity_provider",
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_human_closure_approval_required": True,
        "production_identity_provider_blocker_satisfied": False,
        "production_identity_provider_available": False,
        "production_identity_provider_selected": False,
        "production_identity_provider_approved_by_validator": False,
        "production_identity_provider_configured": False,
        "production_auth_enabled": False,
        "production_auth_ready": False,
        "production_tokens_validated_by_codex": False,
        "tokens_validated_in_production": False,
        "identity_provider_contacted_by_codex": False,
        "identity_provider_contacted": False,
        "jwks_fetched_by_codex": False,
        "jwks_fetched": False,
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
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, expected_value in expected.items():
        require(board.get(key) == expected_value, f"{key} drift")
    require(board.get("blockers_closed_by_board") == 0, "board must close zero blockers")
    require(board.get("readiness_step_count") == 5, "readiness step count must be 5")
    require(isinstance(board.get("steps"), list), "steps must be a list")
    require(len(board["steps"]) == 5, "steps length must be 5")
    require(board.get("status", "").startswith("hold_"), "board status must be hold")

    csv_text = read(BOARD_CSV)
    require("PIDB-001" in csv_text and "PIDB-005" in csv_text, "CSV missing PIDB rows")

    combined = "\n".join([read(BOARD_MD), read(TOP_DOC), read(GATE)])
    required_tokens = [
        "Status:",
        "production_identity_provider",
        "production_identity_provider_available: false",
        "production_identity_provider_selected: false",
        "production_identity_provider_configured: false",
        "production_auth_enabled: false",
        "production_auth_ready: false",
        "production_tokens_validated_by_codex: false",
        "tokens_validated_in_production: false",
        "identity_provider_contacted_by_codex: false",
        "identity_provider_contacted: false",
        "jwks_fetched_by_codex: false",
        "jwks_fetched: false",
        "oauth_oidc_available: false",
        "rbac_available: false",
        "rbac_enforced_in_production: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "development_permission_granted: false",
        "blockers_closed_by_board: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: recommend",
        "recommend_for_local_human_review: true",
        "recommend_for_production: false",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing doc tokens: " + ", ".join(missing))

    forbidden = [
        "production_identity_provider_available: true",
        "production_identity_provider_selected: true",
        "production_auth_enabled: true",
        "production_auth_ready: true",
        "production_tokens_validated_by_codex: true",
        "tokens_validated_in_production: true",
        "identity_provider_contacted_by_codex: true",
        "identity_provider_contacted: true",
        "jwks_fetched_by_codex: true",
        "jwks_fetched: true",
        "oauth_oidc_available: true",
        "rbac_available: true",
        "rbac_enforced_in_production: true",
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "product_launched: true",
        "private_core_exposed: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claims: " + ", ".join(found))

    llms = read("llms.txt")
    required_llms = [
        "/phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_V0_1.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.local.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.md",
        "/docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_identity_provider_readiness_board.py",
        "/scripts/saee_production_identity_provider_readiness_board_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads(read("agent-index.json"))
    entry = index.get("production_identity_provider_readiness_board_v0_1", {})
    expected_index = {
        "status": "hold_human_identity_provider_input_required",
        "production_identity_provider_readiness_board_v0_1": True,
        "target_blocker_id": "production_identity_provider",
        "blockers_closed_by_board": 0,
        "production_identity_provider_blocker_satisfied": False,
        "production_identity_provider_available": False,
        "production_identity_provider_selected": False,
        "production_identity_provider_configured": False,
        "production_auth_enabled": False,
        "production_auth_ready": False,
        "production_tokens_validated_by_codex": False,
        "tokens_validated_in_production": False,
        "identity_provider_contacted_by_codex": False,
        "identity_provider_contacted": False,
        "jwks_fetched_by_codex": False,
        "jwks_fetched": False,
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
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, expected_value in expected_index.items():
        require(entry.get(key) == expected_value, f"agent-index {key} drift")

    print(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_SMOKE: PASS "
        f"status={board['status']} "
        "blockers_closed_by_board=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
