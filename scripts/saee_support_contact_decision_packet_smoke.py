#!/usr/bin/env python3
"""Smoke test for the SAEE support-contact decision packet."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = OUTPUT_DIR / "support_contact_decision_packet.local.json"
OUTPUT_MD = OUTPUT_DIR / "support_contact_decision_packet.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "support_contact_decision_input.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "support_contact_decision_packet_boundary_audit.md"
DOC_PATH = (
    ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_DECISION_PACKET_V0_1.md"
)
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_DECISION_PACKET_RECOMMENDATION_GATE.md"
)

TARGET_KEYS = {
    "customer_facing_support_contact_configured",
    "support_contact_owner_named",
    "abuse_handling_path_defined",
    "customer_notice_route_defined",
    "support_contact_test_recorded",
}

REQUIRED_FALSE_FLAGS = [
    "support_contact_available",
    "support_contact_configured",
    "customer_facing_support_contact_configured",
    "customer_support_available",
    "production_support_available",
    "support_process_available",
    "sla_available",
    "on_call_rotation_available",
    "support_vendor_contacted",
    "customer_contacted",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "production_ready",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "support_contact_published_by_codex",
    "support_contact_test_performed_by_codex",
    "blockers_closed_by_packet",
    "task_candidates_executed",
    "development_permission_granted",
]


def fail(message: str) -> None:
    print("SAEE_SUPPORT_CONTACT_DECISION_PACKET_SMOKE: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_TEMPLATE, OUTPUT_BOUNDARY, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    packet = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    template = json.loads(OUTPUT_TEMPLATE.read_text(encoding="utf-8"))

    require(packet.get("packet_type") == "saee_support_contact_decision_packet", "wrong packet type")
    require(packet.get("packet_version") == "v0.1", "wrong packet version")
    require(packet.get("status") == "ready_for_human_review_not_execution", "wrong status")
    require(packet.get("blocker_target") == "support_contact", "wrong blocker")
    require(packet.get("human_review_required") is True, "human review required")
    require(
        packet.get("separate_execution_approval_required") is True,
        "separate execution approval required",
    )
    require(set(packet.get("target_support_evidence_keys", [])) == TARGET_KEYS, "target keys drifted")
    require(len(packet.get("candidate_contact_slots", [])) == 2, "expected two contact slots")

    for flag in REQUIRED_FALSE_FLAGS:
        require(packet.get(flag) is False, f"{flag} must be false")
        require(template.get("boundary_review", {}).get(flag) is False, f"template {flag} false")

    require(
        template.get("template_type") == "saee_support_contact_decision_input",
        "wrong template type",
    )
    require(
        template.get("input_status") == "template_not_filled",
        "template must remain unfilled",
    )
    require(set(template.get("evidence_review", {})) == TARGET_KEYS, "template evidence keys drifted")
    require(
        all(value is False for value in template.get("evidence_review", {}).values()),
        "template evidence review must remain false",
    )
    require(
        all(not str(value).strip() for value in template.get("source_notes_by_key", {}).values()),
        "template source notes must remain blank",
    )

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, OUTPUT_BOUNDARY, DOC_PATH, GATE_PATH]
    )
    required_phrases = [
        "ready_for_human_review_not_execution",
        "support_contact",
        "support_contact_available: false",
        "support_contact_configured: false",
        "customer_facing_support_contact_configured: false",
        "support_contact_published_by_codex: false",
        "support_contact_test_performed_by_codex: false",
        "blockers_closed_by_packet: false",
        "recommend_for_blocker_closure: false",
        "No support contact published by Codex",
        "No support contact configured",
        "No support contact test performed by Codex",
        "No blocker closure",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in combined]
    require(not missing, "missing boundary phrases: " + ", ".join(missing))

    forbidden_tokens = [
        "support_contact_available: true",
        "\"support_contact_available\": true",
        "support_contact_configured: true",
        "\"support_contact_configured\": true",
        "customer_facing_support_contact_configured: true",
        "\"customer_facing_support_contact_configured\": true",
        "customer_support_available: true",
        "\"customer_support_available\": true",
        "production_support_available: true",
        "\"production_support_available\": true",
        "support_process_available: true",
        "\"support_process_available\": true",
        "sla_available: true",
        "\"sla_available\": true",
        "on_call_rotation_available: true",
        "\"on_call_rotation_available\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "support_vendor_contacted: true",
        "\"support_vendor_contacted\": true",
        "production_ready: true",
        "\"production_ready\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "support_contact_published_by_codex: true",
        "\"support_contact_published_by_codex\": true",
        "support_contact_test_performed_by_codex: true",
        "\"support_contact_test_performed_by_codex\": true",
        "blockers_closed_by_packet: true",
        "\"blockers_closed_by_packet\": true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]
    searchable = "\n".join([combined, json.dumps(packet)])
    found = [token for token in forbidden_tokens if token in searchable]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_DECISION_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_decision_packet.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_decision_packet.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.template.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_decision_packet_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_DECISION_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_support_contact_decision_packet.py",
        "/scripts/saee_support_contact_decision_packet_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("support_contact_decision_packet_v0_1", {})
    expected_index = {
        "status": "ready_for_human_review_not_execution",
        "packet_type": "saee_support_contact_decision_packet",
        "blocker_target": "support_contact",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "support_contact_available": False,
        "support_contact_configured": False,
        "customer_facing_support_contact_configured": False,
        "customer_support_available": False,
        "production_support_available": False,
        "support_process_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "product_launched": False,
        "production_ready": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_performed_by_codex": False,
        "blockers_closed_by_packet": False,
        "development_permission_granted": False,
    }
    for flag, expected in expected_index.items():
        require(entry.get(flag) == expected, f"agent-index {flag} must be {expected}")

    print("SAEE_SUPPORT_CONTACT_DECISION_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
