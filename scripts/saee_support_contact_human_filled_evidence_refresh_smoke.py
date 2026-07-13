#!/usr/bin/env python3
"""Smoke test for support-contact human-filled evidence refresh."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SUMMARY = BASE / "support_contact_human_filled_evidence_refresh.local.json"
BUILDER_OUTPUT = BASE / "support_contact_evidence_builder_output.from_bridge_human_filled.local.json"
SUPPORT_OUTPUT = BASE / "production_support_sla_evidence.from_support_contact_human_filled.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    BUILDER_OUTPUT,
    SUPPORT_OUTPUT,
    BASE / "support_contact_human_filled_evidence_refresh.md",
    BASE / "support_contact_human_filled_evidence_refresh_boundary_audit.md",
    ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md",
]


FALSE_KEYS = [
    "production_support_available",
    "customer_validated",
    "production_ready",
    "product_launched",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "customer_contacted",
    "support_contact_published_by_codex",
    "support_contact_test_performed_by_codex",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH_SMOKE: FAIL: " + message)


def main() -> None:
    for path in REQUIRED:
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    require(summary.get("support_contact_human_filled_evidence_refresh_v0_1") is True, "flag")
    require(
        summary.get("status") == "support_contact_human_filled_evidence_ready_for_review_only",
        "unexpected status",
    )
    require(summary.get("target_blocker_id") == "support_contact", "wrong blocker")
    require(summary.get("input_exists") is True, "input must exist")
    require(summary.get("input_complete") is True, "input must be complete")
    require(summary.get("builder_status") == "pass", "builder must pass")
    require(
        summary.get("support_contact_available_for_review") is True,
        "support contact evidence must be reviewable",
    )
    require(summary.get("blockers_closed_by_refresh") == 0, "must close no blockers")
    require(summary.get("accepted_for_blocker_closure_count") == 0, "accepted count must be 0")
    require(summary.get("separate_go_no_go_profile_required") is True, "go/no-go profile required")
    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")
    require(summary.get("customer_support_available") is False, "customer support remains false")
    require(summary.get("sla_available") is False, "SLA remains false")
    require(summary.get("on_call_rotation_available") is False, "on-call remains false")

    builder = json.loads(BUILDER_OUTPUT.read_text(encoding="utf-8"))
    require(builder.get("status") == "pass", "builder output must pass")
    require(builder.get("input_complete") is True, "builder input complete")
    require(builder.get("support_contact_available_for_review") is True, "builder reviewable")
    require(builder.get("production_support_available") is False, "builder production support false")
    require(builder.get("blockers_closed_by_builder") == 0, "builder closes no blockers")

    support = json.loads(SUPPORT_OUTPUT.read_text(encoding="utf-8"))
    for key in [
        "customer_validated",
        "production_ready",
        "product_launched",
        "private_core_exposed",
        "codex_published_support_contact",
        "codex_sent_support_contact_test",
    ]:
        require(support.get(key) is False, f"support output {key} must be false")

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("support_contact_human_filled_evidence_refresh_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    require(entry.get("status") == summary["status"], "agent-index status mismatch")
    require(entry.get("support_contact_available_for_review") is True, "agent-index reviewable")
    require(entry.get("blockers_closed_by_refresh") == 0, "agent-index closes no blockers")
    for key in FALSE_KEYS:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh_boundary_audit.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_output.from_bridge_human_filled.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_support_contact_human_filled.local.json",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md",
    ]:
        require(item in llms, f"llms.txt missing {item}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED)
    for forbidden in [
        "customer_validated=true",
        "production_ready=true",
        "product_launched=true",
        "private_core_exposed=true",
        "production_support_available=true",
        "customer validation is complete",
        "production readiness is complete",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    print("SAEE_SUPPORT_CONTACT_HUMAN_FILLED_EVIDENCE_REFRESH_SMOKE: PASS")


if __name__ == "__main__":
    main()
