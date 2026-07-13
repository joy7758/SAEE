#!/usr/bin/env python3
"""Smoke check for commercial review packet canonical aliases."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/review_packet_canonical_aliases/review_packet_canonical_aliases.local.json"
)
SUMMARY_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/review_packet_canonical_aliases/review_packet_canonical_aliases.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_RECOMMENDATION_GATE.md"
)
COVERAGE_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        print("SAEE_COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_SMOKE: FAIL " + message)
        sys.exit(1)


def main() -> None:
    for path in [SUMMARY_JSON, SUMMARY_MD, TOP_DOC, GATE, COVERAGE_JSON]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_review_packet_canonical_aliases_v0_1": True,
        "status": "ready_for_agent_lookup_no_blocker_closure",
        "alias_scope": "root_level_agent_readable_review_packet_pointers_only",
        "alias_count": 10,
        "source_packet_count": 10,
        "source_packet_json_count": 10,
        "canonical_alias_count": 10,
        "missing_source_count": 0,
        "missing_alias_count": 0,
        "ready_for_agent_lookup": True,
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "blockers_closed_by_aliases": 0,
    }
    for key, expected_value in expected.items():
        require(payload.get(key) == expected_value, f"{key} must be {expected_value}")

    false_flags = [
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "customer_contacted",
        "customer_validated",
        "production_ready",
        "production_ready_claim",
        "customer_validation_claim",
        "external_validation_success_claim",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
    ]
    for key in false_flags:
        require(payload.get(key) is False, f"{key} must be false")

    aliases = payload.get("aliases", [])
    require(len(aliases) == 10, "expected 10 aliases")
    for alias in aliases:
        canonical = ROOT / alias["canonical_path"]
        source = ROOT / alias["source_packet_path"]
        source_json = ROOT / alias["source_packet_json"]
        require(canonical.exists(), f"missing canonical alias {alias['canonical_path']}")
        require(source.exists(), f"missing source packet {alias['source_packet_path']}")
        require(source_json.exists(), f"missing source packet JSON {alias['source_packet_json']}")
        require(alias.get("ready_for_agent_lookup") is True, "alias not ready for lookup")
        require(alias.get("blocker_closure_allowed") is False, "alias must not allow closure")
        require(alias.get("human_review_required") is True, "alias must require human review")
        text = canonical.read_text(encoding="utf-8")
        for token in [
            "canonical_review_packet_alias_v0_1: true",
            f"packet_type: {alias['packet_type']}",
            f"source_packet_path: {alias['source_packet_path']}",
            "human_review_required: true",
            "separate_execution_approval_required: true",
            "blocker_closure_allowed: false",
            "blockers_closed_by_alias: 0",
            "production_ready: false",
            "customer_validated: false",
            "product_launched: false",
            "private_core_exposed: false",
        ]:
            require(token in text, f"{alias['canonical_path']} missing {token}")

    coverage = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    residual_missing = []
    for row in coverage.get("rows", []):
        missing = row.get("missing_expected_paths", {})
        for path in missing.get("requirements_or_review", []):
            if path.endswith("_REVIEW_PACKET_V0_1.md"):
                residual_missing.append((row.get("blocker_id"), path))
    require(not residual_missing, "coverage has missing review packet aliases: " + repr(residual_missing))
    require(coverage.get("blockers_closed_by_coverage_audit") == 0, "coverage must close zero blockers")
    require(coverage.get("production_ready") is False, "coverage production_ready must be false")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [SUMMARY_MD, TOP_DOC, GATE])
    for token in [
        "commercial_review_packet_canonical_aliases_v0_1: true",
        "status: ready_for_agent_lookup_no_blocker_closure",
        "alias_scope: root_level_agent_readable_review_packet_pointers_only",
        "alias_count: 10",
        "canonical_alias_count: 10",
        "missing_alias_count: 0",
        "blockers_closed_by_aliases: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_agent_lookup: true",
        "recommend_for_blocker_closure: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        require(token in combined, "summary/gate missing " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_V0_1.md",
        "/phase_b_product/commercial_readiness/review_packet_canonical_aliases/review_packet_canonical_aliases.local.json",
        "/phase_b_product/commercial_readiness/review_packet_canonical_aliases/review_packet_canonical_aliases.md",
        "/docs/strategy/SAEE_COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_review_packet_canonical_aliases.py",
        "/scripts/saee_commercial_review_packet_canonical_aliases_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_review_packet_canonical_aliases_v0_1", {})
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")
    for key in false_flags:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    print(
        "SAEE_COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_SMOKE: PASS "
        "alias_count=10 missing_alias_count=0 blockers_closed_by_aliases=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
