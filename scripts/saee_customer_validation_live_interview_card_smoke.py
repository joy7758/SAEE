#!/usr/bin/env python3
"""Smoke test the customer-validation live interview card."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_customer_validation_live_interview_card.py"
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_live_interview_card"
SUMMARY = OUT / "customer_validation_live_interview_card.local.json"
REPORT = OUT / "customer_validation_live_interview_card.md"
HTML = OUT / "customer_validation_live_interview_card.html"
ANSWER_BLOCK = OUT / "customer_validation_live_interview_answer_block.md"
BOUNDARY = OUT / "customer_validation_live_interview_card_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    require("SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD: PASS" in result.stdout, "runner did not print PASS")
    for path in [SUMMARY, REPORT, HTML, ANSWER_BLOCK, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_live_interview_card_v0_1": True,
        "status": "ready_for_real_customer_interview",
        "current_goal_blocker": "customer_validated",
        "customer_question_count": 13,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "blockers_closed_by_card": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    questions = payload.get("interview_questions")
    require(isinstance(questions, list), "interview_questions must be a list")
    require(len(questions) == 13, "interview_questions must contain 13 records")
    require(
        all(item.get("category") == "customer_answer_required" for item in questions),
        "all interview questions must require customer answers",
    )
    require(
        all(item.get("source_required") == "real_customer_or_target_user" for item in questions),
        "all interview questions must require real target-user source",
    )

    answer_block = ANSWER_BLOCK.read_text(encoding="utf-8")
    for token in [
        "participant_role:",
        "current_evaluation_method:",
        "candidate_count:",
        "understanding_score:",
        "trust_score:",
        "decision_influence_score:",
        "willing_to_test_own_candidates:",
    ]:
        require(token in answer_block, f"answer block missing {token}")

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [REPORT, HTML, BOUNDARY, GATE]
    )
    for token in [
        "customer_validation_live_interview_card_v0_1: true",
        "customer_validated: false",
        "production_ready: false",
        "private_core_exposed: false",
        "answer: ready_for_real_customer_interview_no_validation_claim",
        "真实客户 13 问访谈卡",
    ]:
        require(token in combined_docs, f"docs missing token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_answer_block.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD_GATE.md",
        "/scripts/saee_customer_validation_live_interview_card.py",
        "/scripts/saee_customer_validation_live_interview_card_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    entry = read_json(ROOT / "agent-index.json").get("customer_validation_live_interview_card_v0_1")
    require(isinstance(entry, dict), "agent-index missing interview card entry")
    for key in [
        "status",
        "current_goal_blocker",
        "customer_question_count",
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
        "blockers_closed_by_card",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} mismatch")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Customer Validation Live Interview Card v0.1",
        "customer_validation_live_interview_card_v0_1",
        "Current blocker: `customer_validated`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print("SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD_SMOKE: PASS questions=13 customer_validated=false")


if __name__ == "__main__":
    main()
