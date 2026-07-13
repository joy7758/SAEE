#!/usr/bin/env python3
"""Smoke test for the local external customer-validation session launcher."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_local_session_launcher"
)
SUMMARY = BASE / "external_customer_validation_local_session_launcher.local.json"
HTML = BASE / "external_customer_validation_local_session_launcher.html"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    HTML,
    BASE / "README.md",
    BASE / "external_customer_validation_local_session_launcher.md",
    BASE / "BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LOCAL_SESSION_LAUNCHER_GATE.md",
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    for path in REQUIRED:
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    require(
        summary.get("external_customer_validation_local_session_launcher_v0_1") is True,
        "launcher flag must be true",
    )
    require(
        summary.get("status") == "local_session_launcher_ready_human_external_session_required",
        "unexpected launcher status",
    )
    require(summary.get("current_goal_blocker") == "customer_validated", "wrong blocker")
    require(summary.get("recommended_path_locked") is True, "recommended path must be locked")
    require(summary.get("recommended_path_id") == "minimum_session_packet", "wrong recommended path")
    require(summary.get("human_external_session_required") is True, "human session required")
    require(summary.get("blockers_closed_by_launcher") == 0, "blockers must remain open")
    require(
        summary.get("local_static_launcher")
        == (
            "phase_b_product/commercial_readiness/customer_validation_evidence/"
            "external_customer_validation_local_session_launcher/"
            "external_customer_validation_local_session_launcher.html"
        ),
        "launcher path mismatch",
    )
    require(
        summary.get("online_experience_preview") == "phase_b_product/landing/online-experience.html",
        "online experience path mismatch",
    )
    require(
        summary.get("minimum_session_form")
        == (
            "phase_b_product/commercial_readiness/customer_validation_evidence/"
            "external_customer_validation_minimum_session_packet/minimum_session_form.html"
        ),
        "minimum session form path mismatch",
    )
    require(
        summary.get("minimum_session_questions")
        == (
            "phase_b_product/commercial_readiness/customer_validation_evidence/"
            "external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md"
        ),
        "minimum session questions path mismatch",
    )
    require(
        summary.get("facilitator_role") == "reference_only_boundary_support",
        "facilitator must be reference-only",
    )
    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")

    html = HTML.read_text(encoding="utf-8")
    for token in [
        "SAEE 客户验证会话启动器",
        "把一次真实客户验证会话跑顺",
        "../../../landing/online-experience.html",
        "../external_customer_validation_minimum_session_packet/minimum_session_form.html",
        "../external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
        "../external_customer_validation_facilitator/external_customer_validation_facilitator.html",
        "锁定的推荐路径",
        "facilitator 只用于提醒边界",
        "customer_validated",
        "production_ready",
        "false",
    ]:
        require(token in html, "launcher HTML missing token: " + token)

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("external_customer_validation_local_session_launcher_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    require(entry.get("status") == summary["status"], "agent-index status mismatch")
    require(entry.get("current_goal_blocker") == "customer_validated", "agent-index blocker mismatch")
    require(entry.get("recommended_path_locked") is True, "agent-index recommended path must be locked")
    require(entry.get("recommended_path_id") == "minimum_session_packet", "agent-index recommended path mismatch")
    require(entry.get("minimum_session_form") == summary["minimum_session_form"], "agent-index form mismatch")
    require(entry.get("minimum_session_questions") == summary["minimum_session_questions"], "agent-index questions mismatch")
    require(entry.get("facilitator_role") == "reference_only_boundary_support", "agent-index facilitator role mismatch")
    require(entry.get("blockers_closed_by_launcher") == 0, "agent-index blockers must remain open")
    for key in FALSE_KEYS:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/README.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/BOUNDARY_AUDIT.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LOCAL_SESSION_LAUNCHER_GATE.md",
    ]:
        require(item in llms, f"llms.txt missing {item}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED)
    for required in [
        "recommended path is locked",
        "12-question minimum session form",
        "reference-only boundary support",
        "MINIMUM_SESSION_QUESTIONS.md",
    ]:
        require(required in combined, f"required locked-path text missing: {required}")
    for forbidden in [
        "customer_validated=true",
        "production_ready=true",
        "product_launched=true",
        "private_core_exposed=true",
        "customer validation is complete",
        "production readiness is complete",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_LOCAL_SESSION_LAUNCHER_SMOKE: PASS")


if __name__ == "__main__":
    main()
