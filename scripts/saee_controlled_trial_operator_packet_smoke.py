#!/usr/bin/env python3
"""Smoke check for the SAEE controlled trial operator packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_CONTROLLED_TRIAL_OPERATOR_PACKET_SMOKE: FAIL: {message}")


def read(relpath: str) -> str:
    path = ROOT / relpath
    if not path.is_file():
        fail(f"missing {relpath}")
    return path.read_text(encoding="utf-8")


def require_tokens(relpath: str, tokens: list[str]) -> None:
    text = read(relpath)
    missing = [token for token in tokens if token not in text]
    if missing:
        fail(f"{relpath} missing tokens: {', '.join(missing)}")


def main() -> None:
    required_files = [
        "phase_b_product/validation/CONTROLLED_TRIAL_OPERATOR_PACKET_V0_1.md",
        "phase_b_product/validation/controlled_trial_operator_packet/README.md",
        "phase_b_product/validation/controlled_trial_operator_packet/local_trial_session_template.json",
        "phase_b_product/validation/controlled_trial_operator_packet/local_trial_observation_sheet.md",
        "docs/strategy/SAEE_CONTROLLED_TRIAL_OPERATOR_PACKET_RECOMMENDATION_GATE.md",
    ]
    for relpath in required_files:
        if not (ROOT / relpath).is_file():
            fail(f"missing {relpath}")

    require_tokens(
        "phase_b_product/validation/CONTROLLED_TRIAL_OPERATOR_PACKET_V0_1.md",
        [
            "controlled_trial_operator_packet_v0_1: true",
            "packet_status: local_trial_operator_packet_available",
            "trial_scope: local_mvp_demo_observation",
            "trial_status: local_demo_available",
            "production_ready: false",
            "customer_validated: false",
            "customer_contacted: false",
            "customer_data_allowed: false",
            "paid_trial_enabled: false",
            "payment_provider_configured: false",
            "product_launched: false",
            "public_sdk_released: false",
            "external_ai_assistant_tested: false",
            "external_validation_claim: false",
            "private_core_exposed: false",
            "api_schema_modified: false",
            "runtime_modified: false",
            "backend_modified: false",
            "kernel_modified: false",
            "external_calls_made: false",
            "blockers_closed_by_packet: 0",
            "Run Demo Battle",
            "http://127.0.0.1:8765/",
            "http://127.0.0.1:8000/experiment/run",
        ],
    )
    require_tokens(
        "docs/strategy/SAEE_CONTROLLED_TRIAL_OPERATOR_PACKET_RECOMMENDATION_GATE.md",
        [
            "answer: conditional",
            "recommend_for_local_trial_operation: true",
            "recommend_for_customer_validation_claim: false",
            "recommend_for_production: false",
            "recommend_for_paid_trial: false",
            "recommend_for_external_validation_claim: false",
            "blockers_closed_by_packet: 0",
        ],
    )

    template = json.loads(
        read("phase_b_product/validation/controlled_trial_operator_packet/local_trial_session_template.json")
    )
    expected_template_values = {
        "controlled_trial_operator_packet_v0_1": True,
        "session_scope": "local_mvp_demo_observation",
        "trial_status": "local_demo_available",
    }
    for key, expected in expected_template_values.items():
        if template.get(key) != expected:
            fail(f"template {key} must be {expected!r}")
    if template.get("environment", {}).get("local_only") is not True:
        fail("template environment.local_only must be true")
    if template.get("environment", {}).get("external_calls_made") is not False:
        fail("template environment.external_calls_made must be false")

    boundary_flags = template.get("boundary_flags", {})
    for key in [
        "production_ready_claim_made",
        "customer_validation_claim_made",
        "customer_contacted",
        "customer_data_collected",
        "production_data_collected",
        "paid_trial_enabled",
        "payment_provider_configured",
        "external_ai_assistant_tested",
        "external_validation_claim_made",
        "private_core_exposed",
    ]:
        if boundary_flags.get(key) is not False:
            fail(f"template boundary_flags.{key} must be false")

    commercial = template.get("commercial_readiness", {})
    for key in ["production_ready", "customer_validated", "product_launched", "public_sdk_released"]:
        if commercial.get(key) is not False:
            fail(f"template commercial_readiness.{key} must be false")
    if commercial.get("blockers_closed_by_session") != 0:
        fail("template commercial_readiness.blockers_closed_by_session must be 0")

    combined_docs = "\n".join(
        read(path)
        for path in [
            "phase_b_product/validation/CONTROLLED_TRIAL_OPERATOR_PACKET_V0_1.md",
            "phase_b_product/validation/controlled_trial_operator_packet/README.md",
            "phase_b_product/validation/controlled_trial_operator_packet/local_trial_observation_sheet.md",
            "docs/strategy/SAEE_CONTROLLED_TRIAL_OPERATOR_PACKET_RECOMMENDATION_GATE.md",
        ]
    )
    forbidden = [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "external_validation_claim: true",
        "\"external_validation_claim\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
    ]
    found = [token for token in forbidden if token in combined_docs]
    if found:
        fail("forbidden positive claims found: " + ", ".join(found))

    llms = read("llms.txt")
    required_llms = [
        "/phase_b_product/validation/CONTROLLED_TRIAL_OPERATOR_PACKET_V0_1.md",
        "/phase_b_product/validation/controlled_trial_operator_packet/README.md",
        "/phase_b_product/validation/controlled_trial_operator_packet/local_trial_session_template.json",
        "/phase_b_product/validation/controlled_trial_operator_packet/local_trial_observation_sheet.md",
        "/docs/strategy/SAEE_CONTROLLED_TRIAL_OPERATOR_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_controlled_trial_operator_packet_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    if missing_llms:
        fail("llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads(read("agent-index.json"))
    entry = index.get("controlled_trial_operator_packet_v0_1", {})
    expected_index = {
        "status": "local_trial_operator_packet_available",
        "controlled_trial_operator_packet_v0_1": True,
        "trial_scope": "local_mvp_demo_observation",
        "trial_status": "local_demo_available",
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_data_allowed": False,
        "paid_trial_enabled": False,
        "payment_provider_configured": False,
        "product_launched": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "blockers_closed_by_packet": 0,
    }
    for key, expected in expected_index.items():
        if entry.get(key) != expected:
            fail(f"agent-index controlled_trial_operator_packet_v0_1 {key} must be {expected!r}")

    print(
        "SAEE_CONTROLLED_TRIAL_OPERATOR_PACKET_SMOKE: PASS "
        "local_trial_operator_packet_available=true "
        "production_ready=false "
        "customer_validated=false "
        "customer_contacted=false "
        "product_launched=false "
        "private_core_exposed=false "
        "blockers_closed_by_packet=0"
    )


if __name__ == "__main__":
    main()
