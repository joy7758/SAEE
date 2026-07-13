#!/usr/bin/env python3
"""Smoke-check SAEE public signal final human review record."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "strategy_intake/public_signal_runs/run_001"

REQUIRED_FILES = [
    RUN_DIR / "FINAL_HUMAN_REVIEW_DECISION.md",
    RUN_DIR / "FINAL_HUMAN_REVIEW_DECISION.json",
    RUN_DIR / "APPROVED_BUT_NOT_EXECUTED.md",
    RUN_DIR / "HELD_CANDIDATES.md",
    RUN_DIR / "FINAL_REVIEW_BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_PUBLIC_SIGNAL_RUN_001_FINAL_REVIEW_GATE.md",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_PUBLIC_SIGNAL_FINAL_REVIEW_SMOKE: FAIL {message}")


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    record = json.loads((RUN_DIR / "FINAL_HUMAN_REVIEW_DECISION.json").read_text(encoding="utf-8"))
    expected = {
        "final_human_decision_made": True,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_model_api_called": False,
    }
    bad = [key for key, value in expected.items() if record.get(key) is not value]
    if bad:
        fail("final review boundary flags drifted: " + ", ".join(bad))

    decisions = record.get("decisions", [])
    if len(decisions) != record.get("summary", {}).get("total_candidates"):
        fail("decision count must match summary total_candidates")
    if not decisions:
        fail("at least one final decision is required")

    allowed_final_decisions = {
        "final_approve_documentation_only",
        "final_approve_reference_only",
        "final_hold",
        "final_reject_boundary_risk",
        "final_reject_low_relevance",
    }
    approved_ids = []
    held_ids = []
    for decision in decisions:
        candidate_id = decision.get("candidate_id")
        final_decision = decision.get("final_decision")
        if final_decision not in allowed_final_decisions:
            fail(f"invalid final_decision for {candidate_id}")
        if decision.get("execution_allowed") is not False:
            fail(f"{candidate_id} grants execution permission")
        if decision.get("development_allowed") is not False:
            fail(f"{candidate_id} grants development permission")
        if decision.get("roadmap_update_allowed") is not False:
            fail(f"{candidate_id} grants roadmap update permission")
        if decision.get("requires_separate_execution_approval") is not True:
            fail(f"{candidate_id} must require separate execution approval")
        if final_decision in {"final_approve_documentation_only", "final_approve_reference_only"}:
            approved_ids.append(candidate_id)
        if final_decision in {"final_hold", "final_reject_boundary_risk", "final_reject_low_relevance"}:
            held_ids.append(candidate_id)

    approved_text = (RUN_DIR / "APPROVED_BUT_NOT_EXECUTED.md").read_text(encoding="utf-8")
    missing_approved = [candidate_id for candidate_id in approved_ids if candidate_id not in approved_text]
    if missing_approved:
        fail("approved candidates missing from APPROVED_BUT_NOT_EXECUTED.md: " + ", ".join(missing_approved))
    if "execution_status: not_executed" not in approved_text:
        fail("APPROVED_BUT_NOT_EXECUTED.md must state execution_status: not_executed")

    held_text = (RUN_DIR / "HELD_CANDIDATES.md").read_text(encoding="utf-8")
    missing_held = [candidate_id for candidate_id in held_ids if candidate_id not in held_text]
    if missing_held:
        fail("held candidates missing from HELD_CANDIDATES.md: " + ", ".join(missing_held))

    boundary = (RUN_DIR / "FINAL_REVIEW_BOUNDARY_AUDIT.md").read_text(encoding="utf-8")
    required_boundary = [
        "No runtime modified",
        "No backend modified",
        "No kernel modified",
        "No API schema modified",
        "No landing page modified",
        "No private core exposed",
        "No product launched",
        "No customer contacted",
        "No public SDK released",
        "No external AI assistant tested",
        "No external model API called",
        "No task candidate executed",
        "No development permission granted",
    ]
    missing_boundary = [phrase for phrase in required_boundary if phrase not in boundary]
    if missing_boundary:
        fail("boundary audit missing: " + ", ".join(missing_boundary))

    print("SAEE_PUBLIC_SIGNAL_FINAL_REVIEW_SMOKE: PASS")


if __name__ == "__main__":
    main()
