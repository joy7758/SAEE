#!/usr/bin/env python3
"""Smoke-check SAEE public signal review draft outputs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "strategy_intake/public_signal_runs/run_001"

REQUIRED_FILES = [
    RUN_DIR / "HUMAN_REVIEW_DECISION_DRAFT.md",
    RUN_DIR / "HUMAN_REVIEW_DECISION_DRAFT.json",
    RUN_DIR / "REVIEW_DECISION_SUMMARY.md",
    RUN_DIR / "REVIEW_DECISION_BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_PUBLIC_SIGNAL_RUN_001_REVIEW_DRAFT_GATE.md",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_PUBLIC_SIGNAL_REVIEW_DRAFT_SMOKE: FAIL {message}")


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    draft = json.loads((RUN_DIR / "HUMAN_REVIEW_DECISION_DRAFT.json").read_text(encoding="utf-8"))
    expected = {
        "final_human_decision_made": False,
        "task_candidates_executed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_model_api_called": False,
    }
    bad = [key for key, value in expected.items() if draft.get(key) is not value]
    if bad:
        fail("draft boundary flags drifted: " + ", ".join(bad))

    decisions = draft.get("decisions", [])
    if len(decisions) != draft.get("summary", {}).get("total_candidates"):
        fail("decision count must match summary total_candidates")
    if not decisions:
        fail("at least one decision is required")

    allowed_decisions = {
        "proposed_approve_documentation_only",
        "proposed_approve_reference_only",
        "proposed_hold",
        "proposed_reject_boundary_risk",
        "proposed_reject_low_relevance",
    }
    for decision in decisions:
        if decision.get("proposed_decision") not in allowed_decisions:
            fail(f"invalid proposed_decision for {decision.get('candidate_id')}")
        if decision.get("execution_allowed") is not False:
            fail(f"{decision.get('candidate_id')} grants execution permission")
        if decision.get("development_allowed") is not False:
            fail(f"{decision.get('candidate_id')} grants development permission")
        if decision.get("roadmap_update_allowed") is not False:
            fail(f"{decision.get('candidate_id')} grants roadmap update permission")
        if decision.get("requires_human_final_approval") is not True:
            fail(f"{decision.get('candidate_id')} must require human final approval")

    boundary = (RUN_DIR / "REVIEW_DECISION_BOUNDARY_AUDIT.md").read_text(encoding="utf-8")
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
    ]
    missing_boundary = [phrase for phrase in required_boundary if phrase not in boundary]
    if missing_boundary:
        fail("boundary audit missing: " + ", ".join(missing_boundary))

    print("SAEE_PUBLIC_SIGNAL_REVIEW_DRAFT_SMOKE: PASS")


if __name__ == "__main__":
    main()
