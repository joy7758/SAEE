#!/usr/bin/env python3
"""Smoke test for the external customer-validation minimum session packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_minimum_session_packet"
)
SUMMARY = BASE / "external_customer_validation_minimum_session_packet.local.json"
TEMPLATE = BASE / "minimum_session_human_filled_template.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    TEMPLATE,
    BASE / "README.md",
    BASE / "MINIMUM_SESSION_QUESTIONS.md",
    BASE / "MINIMUM_SESSION_FILLING_GUIDE.md",
    BASE / "minimum_session_form.html",
    BASE / "BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_PACKET_GATE.md",
]


FALSE_KEYS = [
    "human_external_session_performed",
    "customer_contacted_by_codex",
    "customer_validated",
    "production_ready",
    "product_launched",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in REQUIRED:
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    require(
        summary.get("external_customer_validation_minimum_session_packet_v0_1") is True,
        "packet flag must be true",
    )
    require(
        summary.get("status") == "minimum_session_packet_ready_human_external_session_required",
        "unexpected packet status",
    )
    require(summary.get("current_goal_blocker") == "customer_validated", "wrong blocker")
    require(
        summary.get("local_static_form")
        == (
            "phase_b_product/commercial_readiness/customer_validation_evidence/"
            "external_customer_validation_minimum_session_packet/minimum_session_form.html"
        ),
        "local_static_form must point to minimum_session_form.html",
    )
    require(summary.get("minimum_question_count") == 12, "minimum_question_count must be 12")
    require(summary.get("uses_existing_importer_schema") is True, "must reuse importer schema")
    require(summary.get("human_external_session_required") is True, "human session required")
    require(summary.get("blockers_closed_by_packet") == 0, "blockers_closed_by_packet must be 0")
    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")

    require(
        template.get("external_customer_validation_session_entry_template_v0_1") is True,
        "template flag must be true",
    )
    require(template.get("human_entry_confirmed") is False, "template must not be confirmed")
    review = template.get("evidence_review", {})
    require(isinstance(review, dict), "evidence_review must be object")
    require(len(review) == 25, "evidence_review must contain 25 keys")
    require(all(value is False for value in review.values()), "review keys must start false")
    for key in [
        "customer_contacted",
        "customer_validated",
        "product_launched",
        "production_ready",
        "private_core_exposed",
        "public_validation_claim_published",
        "testimonial_published",
        "case_study_published",
    ]:
        require(template.get(key) is False, f"template {key} must be false")

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("external_customer_validation_minimum_session_packet_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    require(entry.get("status") == summary["status"], "agent-index status mismatch")
    for key in FALSE_KEYS:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/README.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_FILLING_GUIDE.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_human_filled_template.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/external_customer_validation_minimum_session_packet.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/BOUNDARY_AUDIT.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_PACKET_GATE.md",
    ]:
        require(item in llms, f"llms.txt missing {item}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED)
    form = (BASE / "minimum_session_form.html").read_text(encoding="utf-8")
    for token in [
        "SAEE 最小客户验证填写页",
        "生成 JSON",
        "external_customer_validation_session_entry.human_filled.local.json",
        "customer_validated: false",
        "production_ready: false",
        "private_core_exposed: false",
    ]:
        require(token in form, "minimum_session_form.html missing token: " + token)
    for forbidden in [
        "customer_validated=true",
        "production_ready=true",
        "product_launched=true",
        "private_core_exposed=true",
        "customer validation complete",
        "production ready",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
