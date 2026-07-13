#!/usr/bin/env python3
"""Smoke test for SAEE v1.0 stable evolutionary runtime."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v1_0.runtime.saee_runtime import run_runtime


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V1_0_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    record = run_runtime(seed, generations=12, population_size=8)
    summary = record["stability_summary"]
    boundaries = set(record["boundaries"])

    if record["status"] != "local_v1_0_stable_evolutionary_runtime":
        fail("unexpected status")
    if record["loop_count"] != 1 or record["core_loop"] != ["Sense", "Mutate", "Evaluate", "Select", "Lineage", "Update"]:
        fail("single core loop missing")
    if record["population_model"] != "single_population_pool" or not summary["single_population_pool"]:
        fail("population is not single pool")
    if record["fitness_model"] != "single_unified_fitness" or not summary["single_unified_fitness"]:
        fail("fitness is not unified")
    if record["lineage_model"] != "single_lineage_dag" or not summary["single_lineage_graph"]:
        fail("lineage is not single DAG")
    if summary["forbidden_runtime_layers"]:
        fail("forbidden runtime layers present")
    if summary["phase_theory_in_runtime"] or summary["physics_abstraction_in_runtime"]:
        fail("phase/physics layer leaked into runtime")
    if summary["observer_epistemic_semantic_core"]:
        fail("observer/epistemic/semantic core leaked into runtime")
    if len(record["population"]) != 8:
        fail("population size changed unexpectedly")
    if not record["lineage_dag"]["nodes"] or not record["lineage_dag"]["edges"]:
        fail("lineage DAG missing nodes or edges")

    required_boundaries = {
        "single_core_loop_only",
        "population_based_evolution",
        "single_population_pool",
        "single_unified_fitness",
        "single_lineage_dag",
        "no_phase_theory_runtime",
        "no_physics_abstraction_runtime",
        "no_external_repo_execution",
        "local_reproducible_runtime_only",
    }
    if not required_boundaries.issubset(boundaries):
        fail("required stability boundaries missing")

    print(
        "SAEE_V1_0_SMOKE: PASS "
        f"generations={record['generation_count']} "
        f"population={len(record['population'])} "
        f"loop_count={record['loop_count']} "
        f"fitness={record['fitness_model']} "
        f"lineage={record['lineage_model']}"
    )


if __name__ == "__main__":
    main()

