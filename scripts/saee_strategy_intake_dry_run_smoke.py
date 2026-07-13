#!/usr/bin/env python3
"""Smoke-check SAEE Strategy Intake dry-run outputs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "strategy_intake/dry_runs/run_001"

REQUIRED_FILES = [
    RUN_DIR / "DRY_RUN_SUMMARY.json",
    RUN_DIR / "DRY_RUN_REPORT.md",
    RUN_DIR / "SIGNAL_QUALITY_SCORECARD.md",
    RUN_DIR / "TASK_CANDIDATE_REVIEW.md",
    RUN_DIR / "BOUNDARY_AUDIT.md",
    RUN_DIR / "REVIEW_GATE_QUEUE.md",
    RUN_DIR / "NEXT_ACTIONS.md",
    ROOT / "docs/strategy/SAEE_STRATEGY_INTAKE_DRY_RUN_GATE.md",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_STRATEGY_INTAKE_DRY_RUN_SMOKE: FAIL {message}")


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    summary = json.loads((RUN_DIR / "DRY_RUN_SUMMARY.json").read_text(encoding="utf-8"))
    expected = {
        "dry_run_only": True,
        "external_calls_made": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "task_candidates_executed": False,
        "human_approval_required": True,
    }
    bad = [key for key, value in expected.items() if summary.get(key) is not value]
    if bad:
        fail("summary boundary flags drifted: " + ", ".join(bad))

    if summary.get("dry_run_status") not in {"pass", "hold", "stop"}:
        fail("dry_run_status must be pass, hold, or stop")

    scores = summary.get("scores", {})
    for key in ["signal_quality", "task_candidate_quality", "duplicate_rate_score", "boundary_safety", "commercial_relevance"]:
        value = scores.get(key)
        if not isinstance(value, int) or not 0 <= value <= 5:
            fail(f"score {key} must be an integer between 0 and 5")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED_FILES if path.suffix in {".md", ".json"})
    required_phrases = [
        "No candidate task was executed.",
        "No product, backend, runtime, or private core was modified.",
        "Human review of `REVIEW_GATE_QUEUE.md` only.",
    ]
    missing_phrases = [phrase for phrase in required_phrases if phrase not in combined]
    if missing_phrases:
        fail("missing dry-run boundary phrases: " + ", ".join(missing_phrases))

    forbidden = [
        "external_calls_made: true",
        "runtime_modified: true",
        "backend_modified: true",
        "kernel_modified: true",
        "private_core_exposed: true",
        "product_launched: true",
        "customer_contacted: true",
        "task_candidates_executed: true",
        "\"external_calls_made\": true",
        "\"runtime_modified\": true",
        "\"backend_modified\": true",
        "\"kernel_modified\": true",
        "\"private_core_exposed\": true",
        "\"product_launched\": true",
        "\"customer_contacted\": true",
        "\"task_candidates_executed\": true",
    ]
    hits = [token for token in forbidden if token in combined]
    if hits:
        fail("forbidden status tokens found: " + ", ".join(hits))

    print("SAEE_STRATEGY_INTAKE_DRY_RUN_SMOKE: PASS")


if __name__ == "__main__":
    main()
