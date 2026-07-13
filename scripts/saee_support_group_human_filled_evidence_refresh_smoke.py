#!/usr/bin/env python3
"""Smoke test for support group human-filled evidence refresh."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/support_evidence"
SUMMARY = BASE / "support_group_human_filled_evidence_refresh.local.json"
PROFILE = BASE / "support_group_human_filled_evidence_refresh_profile.local.json"
COMBINED = BASE / "production_support_sla_evidence.combined_from_all_support_human_filled.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    PROFILE,
    COMBINED,
    BASE / "support_group_human_filled_evidence_refresh.md",
    BASE / "support_group_human_filled_evidence_refresh_boundary_audit.md",
    ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md",
]


FALSE_KEYS = [
    "production_ready",
    "customer_validated",
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
    "support_operations_started",
    "sla_published_by_codex",
    "on_call_rotation_started_by_codex",
    "development_permission_granted",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH_SMOKE: FAIL: " + message)


def main() -> None:
    for path in REQUIRED:
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    require(summary.get("support_group_human_filled_evidence_refresh_v0_1") is True, "flag")
    require(
        summary.get("status") == "support_group_human_filled_evidence_complete_for_review_only",
        "unexpected status",
    )
    require(summary.get("support_contact_evidence_complete") is True, "support contact incomplete")
    require(summary.get("customer_support_evidence_complete") is True, "customer support incomplete")
    require(summary.get("sla_evidence_complete") is True, "SLA incomplete")
    require(summary.get("on_call_rotation_evidence_complete") is True, "on-call incomplete")
    require(summary.get("production_support_available") is True, "support lane should be locally complete")
    require(summary.get("blockers_closed_by_refresh") == 0, "must close no blockers")
    require(summary.get("accepted_for_blocker_closure_count") == 0, "accepted closure count must be 0")
    require(summary.get("separate_go_no_go_profile_required") is True, "go/no-go profile required")
    require(summary.get("separate_human_launch_approval_required") is True, "launch approval required")
    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    require(profile.get("profile_status") == "pass", "profile must pass")
    require(profile.get("production_support_available") is True, "profile support unavailable")
    require(profile.get("production_ready") is False, "profile must not claim production ready")
    require(profile.get("customer_validated") is False, "profile must not claim customer validated")
    require(profile.get("blockers_closed_by_profile") == 0, "profile closes no blockers")

    combined = json.loads(COMBINED.read_text(encoding="utf-8"))
    require(combined.get("support_evidence_type") == "production_support_sla_evidence", "combined type")
    for key in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "external_calls_made",
        "customer_contacted",
        "support_vendor_contacted",
    ]:
        require(combined.get(key) is False, f"combined {key} must be false")

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("support_group_human_filled_evidence_refresh_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    require(entry.get("status") == summary["status"], "agent-index status mismatch")
    require(entry.get("production_support_available") is True, "agent-index support unavailable")
    require(entry.get("blockers_closed_by_refresh") == 0, "agent-index closes no blockers")
    for key in FALSE_KEYS:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh_boundary_audit.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh_profile.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.combined_from_all_support_human_filled.local.json",
        "/docs/strategy/SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH_GATE.md",
    ]:
        require(item in llms, f"llms.txt missing {item}")

    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED)
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "customer validation is complete",
        "production readiness is complete",
    ]:
        require(forbidden not in combined_text, f"forbidden claim found: {forbidden}")

    print("SAEE_SUPPORT_GROUP_HUMAN_FILLED_EVIDENCE_REFRESH_SMOKE: PASS")


if __name__ == "__main__":
    main()
