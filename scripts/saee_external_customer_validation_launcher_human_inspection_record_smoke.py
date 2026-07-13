#!/usr/bin/env python3
"""Smoke test for the customer-validation launcher human inspection record."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_local_session_launcher"
)
SUMMARY = BASE / "launcher_human_inspection_record.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    BASE / "launcher_human_inspection_record.md",
    BASE / "launcher_human_inspection_boundary_audit.md",
    ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LAUNCHER_HUMAN_INSPECTION_GATE.md",
]


FALSE_KEYS = [
    "external_customer_session_performed",
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    for path in REQUIRED:
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    require(
        summary.get("external_customer_validation_launcher_human_inspection_record_v0_1")
        is True,
        "inspection flag must be true",
    )
    require(
        summary.get("status") == "launcher_human_inspection_confirmed_no_issue",
        "unexpected inspection status",
    )
    require(summary.get("human_inspection_confirmed") is True, "human inspection must be true")
    require(summary.get("human_reported_issue_count") == 0, "issue count must be 0")
    require(summary.get("current_goal_blocker") == "customer_validated", "wrong blocker")
    require(summary.get("human_external_session_required") is True, "human external session required")
    require(summary.get("blockers_closed_by_inspection") == 0, "inspection must close no blockers")
    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("external_customer_validation_launcher_human_inspection_record_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    require(entry.get("status") == summary["status"], "agent-index status mismatch")
    require(entry.get("human_inspection_confirmed") is True, "agent-index inspection must be true")
    require(entry.get("human_reported_issue_count") == 0, "agent-index issue count must be 0")
    require(entry.get("blockers_closed_by_inspection") == 0, "agent-index blockers must remain open")
    for key in FALSE_KEYS:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_record.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_record.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_boundary_audit.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LAUNCHER_HUMAN_INSPECTION_GATE.md",
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
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_LAUNCHER_HUMAN_INSPECTION_RECORD_SMOKE: PASS")


if __name__ == "__main__":
    main()
