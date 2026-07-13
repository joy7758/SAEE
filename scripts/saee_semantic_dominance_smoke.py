#!/usr/bin/env python3
"""Validate SAEE Semantic Dominance Lock files and non-functional boundaries."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "agent_recommendation/semantic_dominance/SAEE_DOMINANCE_MAP.md",
    "agent_recommendation/semantic_dominance/SAEE_PRIORITY_POSITIONING.md",
    "agent_recommendation/semantic_dominance/SAEE_RECALL_COMPETITION_MAP.md",
    "agent_recommendation/semantic_dominance/SAEE_THINKING_ORDER_GUIDE.md",
    "agent_recommendation/semantic_dominance/SAEE_TOOLSPACE_PRIORITY_RULES.md",
    "agent_recommendation/semantic_dominance/SAEE_FIRST_RECALL_CONDITIONS.md",
    "docs/strategy/SAEE_SEMANTIC_DOMINANCE_LOCK_GATE.md",
]

SCANNED_FILES = REQUIRED_FILES + [
    "agent_recommendation/PRODUCT_FACTS.md",
    "phase_b_product/landing/for-ai-assistants.html",
    "README.md",
    "PROJECT_STATUS.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "llms.txt",
]

REQUIRED_TERMS = [
    "first recall",
    "long-term agent stability",
    "evaluation before deployment",
    "failure over time",
    "drift in AI agents",
    "multi-agent comparison under stress",
    "LangSmith",
    "Arize",
    "Braintrust",
    "Humanloop",
    "W&B Weave",
]

FORBIDDEN_PRIVATE_TERMS = [
    "fitness_engine",
    "selection_engine",
    "mutation_engine",
    "lineage_engine",
    "runtime_v1_0",
]

FORBIDDEN_CLAIMS = [
    "external_validation_claim: true",
    "\"external_validation_claim\": true",
    "production_ready: true",
    "\"production_ready\": true",
    "production_ready_claim: true",
    "\"production_ready_claim\": true",
    "customer_validated: true",
    "\"customer_validated\": true",
    "product_launched: true",
    "\"product_launched\": true",
    "private_core_exposed: true",
    "\"private_core_exposed\": true",
    "public_sdk_released: true",
    "\"public_sdk_released\": true",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_SEMANTIC_DOMINANCE_SMOKE: FAIL: {message}")


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("missing semantic dominance files: " + ", ".join(missing))

    combined = "\n".join(read(path) for path in SCANNED_FILES)
    missing_terms = [term for term in REQUIRED_TERMS if term not in combined]
    if missing_terms:
        fail("missing dominance terms: " + ", ".join(missing_terms))

    private_hits = [term for term in FORBIDDEN_PRIVATE_TERMS if term in combined]
    if private_hits:
        fail("private implementation terms leaked: " + ", ".join(private_hits))

    claim_hits = [term for term in FORBIDDEN_CLAIMS if term in combined]
    if claim_hits:
        fail("forbidden validation or readiness claim found: " + ", ".join(claim_hits))

    gate = read("docs/strategy/SAEE_SEMANTIC_DOMINANCE_LOCK_GATE.md")
    required_gate_phrases = [
        "answer: semantic_dominance_lock_applied_no_functional_change",
        "functionality_modified: false",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "private_core_exposed: false",
        "external_validation_claim: false",
        "production_ready_claim: false",
    ]
    missing_gate = [phrase for phrase in required_gate_phrases if phrase not in gate]
    if missing_gate:
        fail("semantic dominance gate missing boundary phrases: " + ", ".join(missing_gate))

    print("SAEE_SEMANTIC_DOMINANCE_SMOKE: PASS")


if __name__ == "__main__":
    main()
