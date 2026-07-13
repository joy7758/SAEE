#!/usr/bin/env python3
"""Smoke test for the SAEE v1.0 long-horizon experiment layer."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "saee_experiments" / "output" / "smoke-run"
REPORTS = ROOT / "saee_experiments" / "reports"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_EXPERIMENT_SMOKE: FAIL: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path} is invalid JSON: {exc}")


def main() -> None:
    command = [
        sys.executable,
        "saee_experiments/bootstrap/experiment_bootstrap.py",
        "--generation-count",
        "100",
        "--output-dir",
        "saee_experiments/output/smoke-run",
    ]
    result = subprocess.run(command, cwd=ROOT, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        fail(result.stderr.strip() or result.stdout.strip() or "bootstrap failed")

    experiment = load_json(OUTPUT / "experiment_record.json")
    stability = load_json(REPORTS / "stability_report.json")
    lineage = load_json(REPORTS / "lineage_statistics.json")
    drift = load_json(OUTPUT / "drift_report.json")
    emergence = load_json(OUTPUT / "emergence_report.json")

    constitution = experiment["constitution"]
    if constitution["kernel_modified"]:
        fail("experiment claims kernel modification")
    if constitution["new_evolution_mechanics"]:
        fail("experiment introduced new evolution mechanics")
    if constitution["observer_feedback_into_kernel"]:
        fail("observer feedback entered kernel")
    for key in (
        "single_loop_only",
        "single_fitness_function_only",
        "single_population_pool_only",
        "single_lineage_dag_only",
    ):
        if not constitution[key]:
            fail(f"constitution check failed: {key}")

    kernel = experiment["kernel_record"]
    if kernel["generation_count"] != 100:
        fail("generation count is not 100")
    if len(kernel["population"]) != int(experiment["config"]["population_size"]):
        fail("population size changed outside v1.0 runtime")
    if kernel["loop_count"] != 1:
        fail("more than one evolution loop detected")
    if kernel["fitness_model"] != "single_unified_fitness":
        fail("fitness model is not unified")
    if kernel["population_model"] != "single_population_pool":
        fail("population model is not a single pool")
    if kernel["lineage_model"] != "single_lineage_dag":
        fail("lineage model is not a single DAG")

    trace_lines = (OUTPUT / "evolution_trace.jsonl").read_text(encoding="utf-8").splitlines()
    if len(trace_lines) != 100:
        fail("trace line count does not match generation count")
    if not all(json.loads(line).get("observation_only") is True for line in trace_lines):
        fail("trace contains non-observational generation entry")

    if stability["kernel_modified"] or not stability["observation_only"]:
        fail("stability analyzer is not passive")
    if drift["analysis_type"] != "drift_monitor" or not drift["observation_only"]:
        fail("drift monitor is not passive")
    if emergence["kernel_influence"] or not emergence["observation_only"]:
        fail("emergence observer influenced kernel")
    if not lineage["lineage_integrity_preserved"] or not lineage["single_lineage_dag"]:
        fail("lineage DAG integrity is not preserved")

    print(
        "SAEE_EXPERIMENT_SMOKE: PASS "
        "generations=100 "
        f"population={len(kernel['population'])} "
        f"collapse_events={stability['collapse_event_count']} "
        "observation_only=True"
    )


if __name__ == "__main__":
    main()
