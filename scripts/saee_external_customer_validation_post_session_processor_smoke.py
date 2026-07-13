#!/usr/bin/env python3
"""Smoke test for the external customer-validation post-session processor."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_post_session_processor"
)
SUMMARY = BASE / "external_customer_validation_post_session_processor.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    BASE / "external_customer_validation_post_session_processor.md",
    BASE / "BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_POST_SESSION_PROCESSOR_GATE.md",
    ROOT / "scripts/saee_external_customer_validation_post_session_processor.py",
]


ALLOWED_STATUSES = {
    "hold_human_session_entry_missing",
    "hold_human_session_entry_incomplete",
    "hold_customer_validation_approval_input_incomplete",
    "hold_customer_validation_evidence_not_ready",
    "processed_customer_validation_evidence_ready_for_go_no_go_review",
}


FALSE_KEYS = [
    "customer_validated",
    "production_ready",
    "product_launched",
    "customer_contacted_by_codex",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "public_sdk_released",
    "public_validation_claim_published",
    "testimonial_published",
    "case_study_published",
    "commercial_production_ready",
    "commercial_customer_validated_claim",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in REQUIRED:
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    require(
        data.get("external_customer_validation_post_session_processor_v0_1") is True,
        "processor flag must be true",
    )
    require(data.get("status") in ALLOWED_STATUSES, "unexpected processor status")
    require(data.get("current_goal_blocker") == "customer_validated", "wrong blocker")
    require(data.get("recommended_path_locked") is True, "recommended path must be locked")
    require(data.get("recommended_path_id") == "minimum_session_packet", "wrong recommended path")
    require(
        data.get("recommended_form")
        == "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
        "recommended form must be the minimum session form",
    )
    require(
        data.get("recommended_questions")
        == "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
        "recommended questions must be the minimum session questions",
    )
    require(
        data.get("post_fill_command")
        == "python3 scripts/saee_external_customer_validation_post_session_processor.py",
        "post_fill_command mismatch",
    )
    require(
        data.get("post_fill_validation_command")
        == "python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py",
        "post_fill_validation_command mismatch",
    )
    require(data.get("blockers_closed_by_processor") == 0, "blockers must remain open")
    for key in FALSE_KEYS:
        require(data.get(key) is False, f"{key} must be false")

    if data.get("human_entry_exists") is False:
        require(data.get("status") == "hold_human_session_entry_missing", "missing entry must hold")
        require(data.get("evidence_builder_ran") is False, "builder must not run without entry")
        require(data.get("readiness_status") == "not_run", "readiness must not run without entry")
        require(
            "minimum session form" in data.get("next_human_action", ""),
            "missing-entry next action must name the minimum session form",
        )

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("external_customer_validation_post_session_processor_v0_1")
    require(isinstance(entry, dict), "agent-index missing processor entry")
    require(entry.get("status") == data.get("status"), "agent-index status mismatch")
    require(entry.get("recommended_path_locked") is True, "agent-index path lock missing")
    require(entry.get("recommended_path_id") == "minimum_session_packet", "agent-index wrong path")
    require(entry.get("recommended_form") == data.get("recommended_form"), "agent-index form mismatch")
    for key in [
        "customer_validated",
        "production_ready",
        "product_launched",
        "customer_contacted_by_codex",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
    ]:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/BOUNDARY_AUDIT.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_POST_SESSION_PROCESSOR_GATE.md",
        "/scripts/saee_external_customer_validation_post_session_processor.py",
        "/scripts/saee_external_customer_validation_post_session_processor_smoke.py",
    ]:
        require(item in llms, f"llms.txt missing {item}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED)
    for forbidden in [
        "customer_validated=true",
        "production_ready=true",
        "product_launched=true",
        "private_core_exposed=true",
        "customer validation is complete",
        "production readiness is complete",
        "customer validated: true",
        "production ready: true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")
    for required in [
        "recommended_path_locked: true",
        "recommended_path_id: `minimum_session_packet`",
        "minimum_session_form.html",
        "required_human_output:",
        "python3 scripts/saee_external_customer_validation_post_session_processor.py",
    ]:
        require(required in combined, f"required post-session route text missing: {required}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_POST_SESSION_PROCESSOR_SMOKE: PASS")


if __name__ == "__main__":
    main()
