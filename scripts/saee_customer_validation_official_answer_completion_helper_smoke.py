#!/usr/bin/env python3
"""Smoke test the customer validation official answer completion helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper"
SUMMARY = BASE / "customer_validation_official_answer_completion_helper.local.json"
REPORT = BASE / "customer_validation_official_answer_completion_helper.md"
FIELD_CHECKLIST = BASE / "official_answer_sheet_field_checklist.md"
COPY_TEMPLATE = BASE / "official_answer_sheet_blank_copy_block.md"
HTML = BASE / "official_answer_sheet_completion.html"
BOUNDARY = BASE / "customer_validation_official_answer_completion_helper_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER_GATE.md"
OFFICIAL_ANSWER = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER_SMOKE: FAIL " + message)


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
    for path in [SUMMARY, REPORT, FIELD_CHECKLIST, COPY_TEMPLATE, HTML, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_official_answer_completion_helper_v0_1": True,
        "status": "ready_for_human_official_answer_sheet_completion",
        "current_goal_blocker": "customer_validated",
        "official_answer_sheet_exists": False,
        "codex_generated_customer_answers": False,
        "official_answer_sheet_written_by_codex": False,
        "local_static_official_answer_completion_html": True,
        "browser_only_text_generation": True,
        "html_writes_files": False,
        "html_network_calls": False,
        "target_session_entry_written": False,
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
        "blockers_closed_by_helper": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(payload.get("total_official_answer_field_count", 0) >= 40, "official answer field count too low")
    require(payload.get("customer_answer_fields_from_interview") == 13, "expected 13 interview customer fields")
    require(not OFFICIAL_ANSWER.exists(), "official answer sheet must not be written by helper")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, FIELD_CHECKLIST, HTML, BOUNDARY, GATE])
    for token in [
        "customer_validation_official_answer_completion_helper_v0_1: true",
        "answer: conditional_internal_helper_only",
        "customer_validated: false",
        "production_ready: false",
        "private_core_exposed: false",
        "codex_generated_customer_answers: false",
        "official_answer_sheet_written_by_codex: false",
        "local_static_official_answer_completion_html: true",
        "browser_only_text_generation: true",
        "html_writes_files: false",
        "html_network_calls: false",
        "session_id",
        "human_entry_confirmed",
        "no_private_core_disclosed",
        "生成可复制答案文本",
    ]:
        require(token in combined, f"docs missing token: {token}")

    html = HTML.read_text(encoding="utf-8")
    forbidden_html_tokens = ["fetch(", "XMLHttpRequest", "navigator.sendBeacon", "localStorage", "http://", "https://"]
    found = [token for token in forbidden_html_tokens if token in html]
    require(not found, "HTML must not include external/network/storage behavior: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/customer_validation_official_answer_completion_helper.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/customer_validation_official_answer_completion_helper.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/official_answer_sheet_field_checklist.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/official_answer_sheet_blank_copy_block.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/official_answer_sheet_completion.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/customer_validation_official_answer_completion_helper_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER_GATE.md",
        "/scripts/saee_customer_validation_official_answer_completion_helper.py",
        "/scripts/saee_customer_validation_official_answer_completion_helper_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("customer_validation_official_answer_completion_helper_v0_1")
    require(isinstance(entry, dict), "agent-index missing helper entry")
    for key in [
        "status",
        "current_goal_blocker",
        "target_official_answer_sheet",
        "official_answer_sheet_exists",
        "codex_generated_customer_answers",
        "official_answer_sheet_written_by_codex",
        "local_static_official_answer_completion_html",
        "browser_only_text_generation",
        "html_writes_files",
        "html_network_calls",
        "target_session_entry_written",
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
        "blockers_closed_by_helper",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match summary")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "customer-validation-official-answer-completion-helper-smoke:",
        "check-customer-validation-official-answer-completion-helper:",
        "scripts/saee_customer_validation_official_answer_completion_helper_smoke.py",
    ]:
        require(token in makefile, f"Makefile missing {token}")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Customer Validation Official Answer Completion Helper v0.1",
        "customer_validation_official_answer_completion_helper_v0_1",
        "Current blocker: `customer_validated`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER_SMOKE: PASS "
        "customer_validated=false official_answer_sheet_written_by_codex=false"
    )


if __name__ == "__main__":
    main()
