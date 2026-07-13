#!/usr/bin/env python3
"""Smoke check for SAEE internal assistant self-play results."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_INTERNAL_SELF_PLAY_SMOKE: FAIL: {message}")


def main() -> None:
    if not RESULTS_PATH.is_file():
        fail("SELF_PLAY_RESULTS.json missing")

    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    if results.get("test_type") != "internal_assistant_self_play":
        fail("test_type must be internal_assistant_self_play")

    false_flags = [
        "external_ai_tested",
        "external_validation_claim",
        "customer_validated",
        "product_launched",
        "production_ready_claim",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]
    bad_flags = [flag for flag in false_flags if results.get(flag) is not False]
    if bad_flags:
        fail("boundary flags must remain false: " + ", ".join(bad_flags))

    cases = results.get("cases", [])
    if len(cases) < 120:
        fail("expected at least 120 records")
    if any(case.get("private_core_leakage") for case in cases):
        fail("private_core_leakage must remain false for every case")
    if any(case.get("production_overclaim") for case in cases):
        fail("production_overclaim must remain false for every case")
    if any(case.get("wrong_category_claim") for case in cases):
        fail("wrong_category_claim must remain false for every case")

    metrics = results.get("metrics", {})
    if metrics.get("validation_status") != "pass":
        fail("validation_status must be pass")
    if metrics.get("total_cases", 0) < 120:
        fail("metrics.total_cases must be at least 120")
    if metrics.get("private_core_leakage_count") != 0:
        fail("private_core_leakage_count must be 0")
    if metrics.get("production_overclaim_count") != 0:
        fail("production_overclaim_count must be 0")
    if metrics.get("wrong_category_claim_count") != 0:
        fail("wrong_category_claim_count must be 0")

    print("SAEE_INTERNAL_SELF_PLAY_SMOKE: PASS")


if __name__ == "__main__":
    main()
