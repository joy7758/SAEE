#!/usr/bin/env python3
"""Smoke test for the external customer validation recruitment consent packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent"
SUMMARY = BASE / "external_customer_validation_recruitment_consent.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    BASE / "README.md",
    BASE / "INVITATION_MESSAGE_DRAFT.md",
    BASE / "PARTICIPANT_SCREENING_CHECKLIST.md",
    BASE / "CONSENT_AND_BOUNDARY_SCRIPT.md",
    BASE / "BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_RECRUITMENT_CONSENT_GATE.md",
]


EXPECTED_FALSE = [
    "codex_may_contact_customer",
    "codex_contacted_customer",
    "customer_contacted_by_codex",
    "human_session_performed",
    "human_result_entered",
    "customer_validated",
    "production_ready",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "external_model_api_called",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    for path in REQUIRED:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if data.get("external_customer_validation_recruitment_consent_v0_1") is not True:
        fail("summary missing external_customer_validation_recruitment_consent_v0_1=true")
    if data.get("status") != "prepared_for_human_outreach_no_contact_by_codex":
        fail("unexpected recruitment consent status")
    if data.get("current_goal_blocker") != "customer_validated":
        fail("current_goal_blocker must remain customer_validated")
    if data.get("planned_external_sessions") != 1:
        fail("planned_external_sessions must be 1")
    if data.get("human_outreach_required") is not True:
        fail("human_outreach_required must be true")
    if data.get("blockers_closed_by_packet") != 0:
        fail("blockers_closed_by_packet must be 0")
    for key in EXPECTED_FALSE:
        if data.get(key) is not False:
            fail(f"{key} must be false")

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("external_customer_validation_recruitment_consent_v0_1")
    if not entry:
        fail("agent-index missing external_customer_validation_recruitment_consent_v0_1")
    for key in EXPECTED_FALSE:
        if entry.get(key) is not False:
            fail(f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/README.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/BOUNDARY_AUDIT.md",
    ]
    for item in required_llms:
        if item not in llms:
            fail(f"llms.txt missing {item}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED if path.suffix == ".md")
    forbidden_claims = [
        "customer_validated=true",
        "production_ready=true",
        "product_launched=true",
        "private_core_exposed=true",
        "Codex sends",
        "Codex contacts",
    ]
    for needle in forbidden_claims:
        if needle in combined:
            fail(f"forbidden claim found: {needle}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_RECRUITMENT_CONSENT_SMOKE: PASS")


if __name__ == "__main__":
    main()
