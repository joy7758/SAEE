#!/usr/bin/env python3
"""Smoke check for SAEE v1.2 empirical alignment."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.experiments.run_saee_experiment import run_experiment


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V1_2_SMOKE: FAIL: {message}")


def main() -> None:
    record = run_experiment(generations=18, population_size=10, dimensions=3, seed=23)
    summary = record["summary"]
    validation = summary["validation"]
    for key, passed in validation.items():
        if passed is not True:
            fail(key)
    if summary["metric_count"] < 3:
        fail("expected at least three empirical metrics")
    if summary["attractor_count"] < 1:
        fail("expected at least one detected attractor")
    if summary["baseline_count"] < 3:
        fail("expected GA, ES, and ALife baselines")
    if not record["metric_report"]["lineage_entropy"]:
        fail("missing lineage entropy series")
    if "coupling_strength_coefficient" not in record["coupling_report"]:
        fail("missing reflexive coupling coefficient")
    print(
        "SAEE_V1_2_SMOKE: PASS "
        f"generations={summary['generations']} "
        f"metrics={summary['metric_count']} "
        f"attractors={summary['attractor_count']} "
        f"coupling={summary['coupling_strength_coefficient']} "
        f"baselines={summary['baseline_count']}"
    )


if __name__ == "__main__":
    main()
