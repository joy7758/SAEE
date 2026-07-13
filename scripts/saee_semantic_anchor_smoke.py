#!/usr/bin/env python3
"""Validate SAEE Semantic Anchor Layer files and boundaries."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "agent_recommendation/semantic_anchor/SAEE_SEMANTIC_ANCHOR_MAP.md",
    "agent_recommendation/semantic_anchor/SAEE_RETRIEVAL_TRIGGERS.md",
    "agent_recommendation/semantic_anchor/SAEE_QUERY_PATTERNS.md",
    "agent_recommendation/semantic_anchor/SAEE_TOOLSPACE_POSITIONING.md",
    "agent_recommendation/semantic_anchor/SAEE_VS_LANGSMITH_ARIZE_MAP.md",
    "agent_recommendation/semantic_anchor/SAEE_EMBEDDING_LIKELIHOOD_GUIDE.md",
    "docs/strategy/SAEE_SEMANTIC_ANCHOR_LAYER_RECOMMENDATION_GATE.md",
]

SCANNED_FILES = REQUIRED_FILES + [
    "agent_recommendation/PRODUCT_FACTS.md",
    "agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/SAEE_VS_EXISTING_TOOLS.md",
    "agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
    "agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md",
    "agent_recommendation/EVIDENCE_SUMMARY.md",
    "agent_recommendation/AGENT_RECOMMENDATION_FIT.md",
    "phase_b_product/landing/for-ai-assistants.html",
]

REQUIRED_TERMS = [
    "long-term stability",
    "agent drift",
    "pre-deployment",
    "multi-agent comparison",
    "policy stress testing",
]

FORBIDDEN_PRIVATE_TERMS = [
    "fitness_engine",
    "selection_engine",
    "mutation_engine",
    "lineage_engine",
    "runtime_v1_0",
    "private production evaluator",
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
    raise SystemExit(f"SAEE_SEMANTIC_ANCHOR_SMOKE: FAIL: {message}")


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("missing semantic anchor files: " + ", ".join(missing))

    combined = "\n".join(read(path) for path in SCANNED_FILES)
    missing_terms = [term for term in REQUIRED_TERMS if term not in combined]
    if missing_terms:
        fail("missing semantic anchor terms: " + ", ".join(missing_terms))

    private_hits = [term for term in FORBIDDEN_PRIVATE_TERMS if term in combined]
    if private_hits:
        fail("private implementation terms leaked: " + ", ".join(private_hits))

    claim_hits = [term for term in FORBIDDEN_CLAIMS if term in combined]
    if claim_hits:
        fail("forbidden validation or readiness claim found: " + ", ".join(claim_hits))

    gate = read("docs/strategy/SAEE_SEMANTIC_ANCHOR_LAYER_RECOMMENDATION_GATE.md")
    required_gate_phrases = [
        "answer: semantic_anchor_layer_applied_no_functional_change",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "private_core_exposed: false",
        "external_validation_claim: false",
    ]
    missing_gate = [phrase for phrase in required_gate_phrases if phrase not in gate]
    if missing_gate:
        fail("semantic anchor gate missing boundary phrases: " + ", ".join(missing_gate))

    print("SAEE_SEMANTIC_ANCHOR_SMOKE: PASS")


if __name__ == "__main__":
    main()
