#!/usr/bin/env python3
"""Smoke test for SAEE v0.7 reflexive evolution."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_7.runtime.reflexive_kernel import ReflexiveEvolutionKernel


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V0_7_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    runtime = ReflexiveEvolutionKernel(seed, initial_population_size=5)
    record = runtime.run(6)
    summary = record["reflexive_summary"]
    boundaries = set(record["boundaries"])

    if record["status"] != "local_v0_7_reflexive_evolution":
        fail("unexpected status")
    if summary["explanation_driven_mutation_count"] < 1:
        fail("explanation-driven mutation missing")
    if summary["semantic_stabilization_count"] < 1:
        fail("semantic stabilization missing")
    if summary["feedback_input_count"] < 5:
        fail("meaning feedback did not enter later generations")
    if summary["observer_embedded_count"] < 6:
        fail("observer is not embedded in loop")
    if summary["semantic_selection_count"] < 6:
        fail("semantic selection missing")
    if summary["epistemic_fitness_record_count"] < 1:
        fail("epistemic fitness missing")
    if summary["epistemic_changed_outcome_count"] < 1:
        fail("epistemic fitness did not change survival outcome")
    if summary["self_model_update_count"] < 6:
        fail("self-model did not update")
    if summary["interpretation_influenced_edge_count"] < 1:
        fail("lineage lacks interpretation influence")

    if not all(event.get("feedback_input_id") for event in record["reflexive_mutation_events"]):
        fail("mutation events missing feedback input")
    if not all(item["epistemic_fitness"].get("epistemic_score") is not None for item in record["epistemic_fitness_records"]):
        fail("epistemic scores missing")
    if not any(edge["edge_type"] == "recursive_self_model_update" for edge in record["recursive_understanding_graph"]["edges"]):
        fail("recursive self-model graph missing")
    if not any(edge["edge_type"] == "explanation_influence" for edge in record["explanation_influenced_dag"]["edges"]):
        fail("explanation influence edges missing")
    if not all(cycle["observer_in_loop"]["observer_embedded"] for cycle in record["cycles"]):
        fail("observer is not in loop for every generation")

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
        "SAEE_V0_7_SMOKE: PASS "
        f"generation={record['generation_id']} "
        f"mutations={summary['explanation_driven_mutation_count']} "
        f"stabilized={summary['semantic_stabilization_count']} "
        f"changed={summary['epistemic_changed_outcome_count']}"
    )


if __name__ == "__main__":
    main()
