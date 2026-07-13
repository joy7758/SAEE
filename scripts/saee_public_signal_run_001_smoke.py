#!/usr/bin/env python3
"""Smoke-check SAEE public signal collection run 001 outputs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "strategy_intake/public_signal_runs/run_001"

REQUIRED_FILES = [
    RUN_DIR / "SIGNAL_SUMMARY.md",
    RUN_DIR / "SIGNAL_SUMMARY.json",
    RUN_DIR / "PEER_MOVEMENT_TABLE.md",
    RUN_DIR / "COMMERCIAL_RELEVANCE_NOTES.md",
    RUN_DIR / "BOUNDARY_AUDIT.md",
    RUN_DIR / "NEXT_REVIEW_QUEUE.md",
    RUN_DIR / "SOURCES.md",
    RUN_DIR / "SEARCH_QUERIES.md",
    RUN_DIR / "RAW_NOTES.md",
    ROOT / "docs/strategy/SAEE_PUBLIC_SIGNAL_COLLECTION_RUN_001_GATE.md",
]

FORBIDDEN_CANDIDATE_TYPES = [
    "backend_change",
    "runtime_change",
    "kernel_change",
    "api_schema_change",
    "product_launch",
    "customer_contact",
    "public_sdk_release",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_PUBLIC_SIGNAL_RUN_001_SMOKE: FAIL {message}")


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    summary = json.loads((RUN_DIR / "SIGNAL_SUMMARY.json").read_text(encoding="utf-8"))
    if summary.get("run_type") != "one_time_read_only_public_signal_collection":
        fail("run_type must be one_time_read_only_public_signal_collection")

    expected = {
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "task_candidates_executed": False,
        "human_review_required": True,
    }
    bad = [key for key, value in expected.items() if summary.get(key) is not value]
    if bad:
        fail("summary boundary flags drifted: " + ", ".join(bad))

    if summary.get("run_status") not in {"pass", "hold", "stop"}:
        fail("run_status must be pass, hold, or stop")
    if summary.get("network_available") is True and summary.get("source_count", 0) < 8:
        fail("network_available=true requires at least 8 sources for this run")

    scores = summary.get("scores", {})
    if scores.get("boundary_safety") != 5:
        fail("boundary_safety must be 5")

    queue = (RUN_DIR / "NEXT_REVIEW_QUEUE.md").read_text(encoding="utf-8")
    forbidden = [token for token in FORBIDDEN_CANDIDATE_TYPES if token in queue]
    if forbidden:
        fail("forbidden candidate types found: " + ", ".join(forbidden))
    if "default_decision\": \"hold\"" not in queue:
        fail("review queue must keep default_decision hold")

    audit = (RUN_DIR / "BOUNDARY_AUDIT.md").read_text(encoding="utf-8")
    required_audit = [
        "No runtime modified",
        "No backend modified",
        "No kernel modified",
        "No API schema modified",
        "No private core exposed",
        "No external model API called",
        "No external AI assistant tested",
        "No product launched",
        "No customer contacted",
        "No candidate executed",
    ]
    missing_audit = [phrase for phrase in required_audit if phrase not in audit]
    if missing_audit:
        fail("BOUNDARY_AUDIT.md missing: " + ", ".join(missing_audit))

    print("SAEE_PUBLIC_SIGNAL_RUN_001_SMOKE: PASS")


if __name__ == "__main__":
    main()
