#!/usr/bin/env python3
"""Smoke-check the SAEE strategy intake layer."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "strategy_intake/README.md",
    "strategy_intake/SIGNAL_SOURCES.md",
    "strategy_intake/STRATEGY_INTAKE_BOUNDARY.md",
    "strategy_intake/RECOMMENDATION_SIGNAL_LOG.md",
    "strategy_intake/MARKET_SIGNAL_LOG.md",
    "strategy_intake/COMPETITOR_SIGNAL_LOG.md",
    "strategy_intake/TASK_CANDIDATES.md",
    "strategy_intake/REVIEW_GATE.md",
    "strategy_intake/SCHEDULED_AUTOMATION.md",
    "docs/strategy/SAEE_STRATEGY_INTAKE_RECOMMENDATION_GATE.md",
]


FORBIDDEN_STATUS_TOKENS = [
    "runtime_modified: true",
    "backend_modified: true",
    "api_contract_modified: true",
    "private_core_exposed: true",
    "product_launched: true",
    "customer_contacted: true",
    "self_modification_allowed: true",
    "\"runtime_modified\": true",
    "\"backend_modified\": true",
    "\"api_contract_modified\": true",
    "\"private_core_exposed\": true",
    "\"product_launched\": true",
    "\"customer_contacted\": true",
    "\"self_modification_allowed\": true",
]

FORBIDDEN_IMPLEMENTATION_TOKENS = [
    "saee_backend/core/",
    "saee_v1_0/kernel/",
    "fitness_engine/",
    "selection_engine/",
    "mutation_engine/",
    "lineage_engine/",
    "runtime_v1_0/",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_STRATEGY_INTAKE_SMOKE: FAIL {message}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in REQUIRED_FILES)
    hits = [token for token in FORBIDDEN_STATUS_TOKENS + FORBIDDEN_IMPLEMENTATION_TOKENS if token in combined]
    if hits:
        fail("forbidden tokens found: " + ", ".join(hits))

    required_phrases = [
        "Strategy Intake -> Review Gate -> Human-approved Task",
        "Self-modification = forbidden",
        "External AI Assistant Test: pending human execution",
        "No new market data was collected in this change.",
        "No new competitor or peer data was collected in this change.",
        "saee-strategy-intake-and-peer-signal-collection",
    ]
    missing_phrases = [phrase for phrase in required_phrases if phrase not in combined]
    if missing_phrases:
        fail("missing boundary phrases: " + ", ".join(missing_phrases))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    strategy = index.get("strategy_intake", {})
    required_flags = {
        "status": "observation_only_layer_established",
        "scheduled_automation_status": "active",
        "runtime_modified": False,
        "backend_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "self_modification_allowed": False,
        "human_approved_evolution_allowed": True,
    }
    if strategy.get("status") != required_flags["status"]:
        fail("agent-index.json strategy_intake status is incorrect")
    for flag, expected in required_flags.items():
        if flag == "status":
            continue
        actual = strategy.get(flag)
        if actual != expected:
            fail(f"agent-index.json strategy_intake {flag} must be {expected}")

    manual_run = index.get("external_ai_manual_test_run", {})
    if manual_run:
        if manual_run.get("external_ai_tested") is not False:
            fail("external_ai_manual_test_run external_ai_tested must remain false")
        if manual_run.get("manual_test_completed") is not False:
            fail("external_ai_manual_test_run manual_test_completed must remain false")

    print("SAEE_STRATEGY_INTAKE_SMOKE: PASS")


if __name__ == "__main__":
    main()
