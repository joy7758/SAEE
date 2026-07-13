#!/usr/bin/env python3
"""Validate the SAEE agent recommendation surface."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "agent_recommendation/PRODUCT_FACTS.md",
    "agent_recommendation/PRODUCT_FACTS.json",
    "agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/SAEE_VS_EXISTING_TOOLS.md",
    "agent_recommendation/TARGET_USER_PROFILES.md",
    "agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md",
    "agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
    "agent_recommendation/EVIDENCE_SUMMARY.md",
    "agent_recommendation/INTEGRATION_PATHS.md",
    "agent_recommendation/AGENT_RECOMMENDATION_FIT.md",
    "agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json",
    "phase_b_product/landing/for-ai-assistants.html",
    "docs/strategy/SAEE_AGENT_RECOMMENDATION_SURFACE_RECOMMENDATION_GATE.md",
]

FORBIDDEN_PRIVATE_TERMS = [
    "saee_v1_0/kernel",
    "kernel/runtime.py",
    "fitness_engine",
    "selection_engine",
    "mutation_engine",
    "lineage_engine",
    "runtime_v1_0",
    "private production evaluator",
]

BOUNDARY_TOKENS = [
    "product_launched: false",
    "production_deployed: false",
    "public_sdk_release: false",
    "customer_validated: false",
    "user_upload_enabled: false",
    "private_core_exported: false",
]


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    missing = [relpath for relpath in REQUIRED_FILES if not (ROOT / relpath).is_file()]
    require(not missing, "missing recommendation surface files: " + ", ".join(missing))

    product_facts = json.loads(read("agent_recommendation/PRODUCT_FACTS.json"))
    require(product_facts["product_name"] == "SAEE", "PRODUCT_FACTS.json product_name must be SAEE")
    require(product_facts["current_status"]["local_mvp_complete"] is True, "local_mvp_complete must be true")
    require(product_facts["current_status"]["production_ready"] is False, "production_ready must be false")
    require(product_facts["current_status"]["customer_validated"] is False, "customer_validated must be false")
    require(product_facts["current_status"]["public_sdk_released"] is False, "public_sdk_released must be false")
    require(product_facts["current_status"]["private_core_exposed"] is False, "private_core_exposed must be false")

    cases = json.loads(read("agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json"))
    require(len(cases) >= 20, "AGENT_RECOMMENDATION_TEST_SET.json must contain at least 20 cases")
    actions = [case.get("expected_action") for case in cases]
    require(actions.count("recommend") >= 8, "test set must contain at least 8 recommend cases")
    require(actions.count("do_not_recommend") >= 8, "test set must contain at least 8 do_not_recommend cases")
    require(actions.count("mention") >= 4, "test set must contain at least 4 ambiguous mention cases")
    allowed_actions = {"recommend", "mention", "do_not_recommend"}
    bad_actions = sorted({action for action in actions if action not in allowed_actions})
    require(not bad_actions, "unexpected expected_action values: " + ", ".join(bad_actions))

    html = read("phase_b_product/landing/for-ai-assistants.html")
    require("<script" not in html.lower(), "for-ai-assistants.html must not include JavaScript")
    require("fetch(" not in html, "for-ai-assistants.html must not call backend APIs")
    require("How to decide whether to recommend SAEE" in html, "for-ai-assistants.html missing title")

    all_text = "\n".join(read(relpath) for relpath in REQUIRED_FILES)
    leaked = [term for term in FORBIDDEN_PRIVATE_TERMS if term in all_text]
    require(not leaked, "private implementation terms leaked: " + ", ".join(leaked))

    gate_text = read("docs/strategy/SAEE_AGENT_RECOMMENDATION_SURFACE_RECOMMENDATION_GATE.md")
    missing_boundary = [token for token in BOUNDARY_TOKENS if token not in gate_text]
    require(not missing_boundary, "recommendation gate missing boundary tokens: " + ", ".join(missing_boundary))

    llms = read("llms.txt")
    required_llms_paths = [
        "/agent_recommendation/PRODUCT_FACTS.md",
        "/agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
        "/agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
        "/agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
        "/agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md",
        "/phase_b_product/landing/for-ai-assistants.html",
    ]
    missing_llms = [path for path in required_llms_paths if path not in llms]
    require(not missing_llms, "llms.txt missing recommendation paths: " + ", ".join(missing_llms))

    print(
        "SAEE_AGENT_RECOMMENDATION_SURFACE_SMOKE: PASS "
        "files=true product_facts_json=true test_cases=20 "
        "positive_cases=8 negative_cases=8 ambiguous_cases=4 "
        "static_html=true private_core_leak=false"
    )


if __name__ == "__main__":
    main()
