#!/usr/bin/env python3
"""Smoke-check Public Signal Run 001 documentation-only execution."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = ROOT / "strategy_intake/public_signal_runs/run_001/documentation_execution"
SUMMARY_PATH = EXEC_DIR / "DOCUMENTATION_EXECUTION_SUMMARY.json"

REQUIRED_FILES = [
    EXEC_DIR / "DOCUMENTATION_EXECUTION_PLAN.md",
    EXEC_DIR / "DOCUMENTATION_EXECUTION_REPORT.md",
    SUMMARY_PATH,
    EXEC_DIR / "UPDATED_FILES.md",
    EXEC_DIR / "REFERENCE_ONLY_ARCHIVE.md",
    EXEC_DIR / "HELD_ITEMS_UNCHANGED.md",
    EXEC_DIR / "DOCUMENTATION_BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_PUBLIC_SIGNAL_RUN_001_DOCUMENTATION_EXECUTION_GATE.md",
]

ALLOWED_UPDATED_FILES = {
    "agent_recommendation/PRODUCT_FACTS.md",
    "agent_recommendation/PRODUCT_FACTS.json",
    "agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/SAEE_VS_EXISTING_TOOLS.md",
    "agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md",
    "agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
    "agent_recommendation/EVIDENCE_SUMMARY.md",
    "agent_recommendation/AGENT_RECOMMENDATION_FIT.md",
    "phase_b_product/landing/for-ai-assistants.html",
    "README.md",
    "PROJECT_STATUS.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "agent-readable.md",
    "llms.txt",
    "agent-index.json",
    "Makefile",
    "scripts/mainline_guard.py",
}


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_PUBLIC_SIGNAL_DOCUMENTATION_EXECUTION_SMOKE: FAIL {message}")


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    expected_true = {
        "human_execution_authorized": True,
        "task_candidates_executed": True,
        "validation_required": True,
    }
    for key, expected in expected_true.items():
        if summary.get(key) is not expected:
            fail(f"{key} must be {expected}")

    expected_false = [
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "landing_page_interaction_modified",
        "private_core_exposed",
        "product_launched",
        "customer_contacted",
        "public_sdk_released",
        "external_ai_assistant_tested",
        "external_model_api_called",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    bad_false = [key for key in expected_false if summary.get(key) is not False]
    if bad_false:
        fail("boundary flags drifted: " + ", ".join(bad_false))

    if summary.get("execution_type") != "documentation_only":
        fail("execution_type must be documentation_only")
    if summary.get("executed_candidates") != ["PSR-001", "PSR-002"]:
        fail("executed_candidates must be exactly PSR-001 and PSR-002")
    if "PSR-004" not in summary.get("reference_only_candidates", []):
        fail("PSR-004 must remain reference-only")
    held = set(summary.get("held_candidates", []))
    if not {"PSR-003", "PSR-005"}.issubset(held):
        fail("PSR-003 and PSR-005 must remain held")

    updated_files = set(summary.get("updated_files", []))
    if not updated_files:
        fail("updated_files must not be empty")
    disallowed = sorted(updated_files - ALLOWED_UPDATED_FILES)
    if disallowed:
        fail("updated_files contains disallowed paths: " + ", ".join(disallowed))

    product_facts = json.loads((ROOT / "agent_recommendation/PRODUCT_FACTS.json").read_text(encoding="utf-8"))
    current_status = product_facts.get("current_status", {})
    for key in [
        "production_ready",
        "customer_validated",
        "public_sdk_released",
        "private_core_exposed",
    ]:
        if current_status.get(key) is not False:
            fail(f"PRODUCT_FACTS.json current_status.{key} must remain false")

    boundary = (EXEC_DIR / "DOCUMENTATION_BOUNDARY_AUDIT.md").read_text(encoding="utf-8")
    required_boundary = [
        "Only documentation / recommendation materials were modified",
        "No runtime modified",
        "No backend modified",
        "No kernel modified",
        "No API schema modified",
        "No landing page interaction modified",
        "No private core exposed",
        "No product launched",
        "No customer contacted",
        "No public SDK released",
        "No external AI assistant tested",
        "No external model API called",
        "No production-ready claim added",
        "No customer-validation claim added",
    ]
    missing_boundary = [phrase for phrase in required_boundary if phrase not in boundary]
    if missing_boundary:
        fail("boundary audit missing: " + ", ".join(missing_boundary))

    reference = (EXEC_DIR / "REFERENCE_ONLY_ARCHIVE.md").read_text(encoding="utf-8")
    if "PSR-004" not in reference or "not converted into roadmap work" not in reference:
        fail("REFERENCE_ONLY_ARCHIVE.md must preserve PSR-004 as reference-only")

    held_text = (EXEC_DIR / "HELD_ITEMS_UNCHANGED.md").read_text(encoding="utf-8")
    for candidate_id in ["PSR-003", "PSR-005"]:
        if candidate_id not in held_text or "final_hold" not in held_text:
            fail(f"{candidate_id} must be recorded as held")

    print("SAEE_PUBLIC_SIGNAL_DOCUMENTATION_EXECUTION_SMOKE: PASS")


if __name__ == "__main__":
    main()
