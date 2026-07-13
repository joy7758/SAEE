#!/usr/bin/env python3
"""Smoke test for SAEE v0.5 open-ended evolution physics."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_5.runtime.physics_loop import OpenEndedPhysicsLoop


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V0_5_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    runtime = OpenEndedPhysicsLoop(seed, initial_population_size=5)
    record = runtime.run(6)
    summary = record["open_ended_physics_summary"]
    boundaries = set(record["boundaries"])

    if record["status"] != "local_v0_5_open_ended_physics":
        fail("unexpected status")
    if len(record["population"]) < 5:
        fail("population collapsed")
    if summary["generated_law_count"] < 6:
        fail("laws were not generated each generation")
    if summary["generated_fitness_function_count"] < 6:
        fail("fitness functions were not generated each generation")
    if summary["selection_mechanism_count"] < 6:
        fail("selection mechanisms were not generated each generation")
    if summary["dimension_birth_count"] < 2:
        fail("runtime dimension birth missing")
    if summary["dimension_merge_count"] < 1:
        fail("runtime dimension merge missing")
    if summary["dimension_collapse_count"] < 1:
        fail("runtime dimension collapse missing")
    if summary["regime_regeneration_count"] < 1 or summary["regime_collapse_count"] < 1:
        fail("regime collapse/regeneration missing")
    if summary["irreversible_phase_count"] < 1:
        fail("irreversible phase transition missing")

    if not all(law.get("clauses") and law.get("origin_observation") for law in record["generated_evolution_laws"]):
        fail("generated laws missing clauses or observation origin")
    if not all(function.get("expression_terms") for function in record["generated_fitness_functions"]):
        fail("generated fitness functions missing expression terms")
    if not any(mechanism.get("parents") for mechanism in record["selection_mechanisms"][1:]):
        fail("selection mechanisms did not reproduce or mutate")
    if not record["hyper_graph"]["hyperedges"]:
        fail("hypergraph has no hyperedges")

    required_boundaries = {
        "abstract_signal_objects_only",
        "no_real_api_calls",
        "no_external_repo_execution",
        "no_permission_expansion",
        "no_external_code_as_genome",
        "local_reproducible_simulation_only",
    }
    if not required_boundaries.issubset(boundaries):
        fail("required safety boundaries missing")

    print(
        "SAEE_V0_5_SMOKE: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])} "
        f"laws={summary['generated_law_count']} "
        f"dimensions={summary['dimension_birth_count']} "
        f"regenerations={summary['regime_regeneration_count']}"
    )


if __name__ == "__main__":
    main()
