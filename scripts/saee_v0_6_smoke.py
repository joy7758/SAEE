#!/usr/bin/env python3
"""Smoke test for SAEE v0.6 evolution observability."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_6.runtime.observable_kernel import ObservableEvolutionKernel


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V0_6_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    runtime = ObservableEvolutionKernel(seed, initial_population_size=5)
    record = runtime.run(6)
    summary = record["observability_summary"]
    boundaries = set(record["boundaries"])

    if record["status"] != "local_v0_6_evolution_observability":
        fail("unexpected status")
    if summary["observed_generation_count"] < 6:
        fail("missing observed generations")
    if summary["observation_event_count"] < 6:
        fail("missing observation events")
    if summary["rule_genesis_count"] < 6:
        fail("missing rule genesis records")
    if summary["fitness_explanation_count"] < 1:
        fail("missing fitness explanations")
    if summary["causal_reconstruction_count"] < 1:
        fail("missing causal reconstructions")
    if summary["semantic_node_count"] < 1 or summary["semantic_edge_count"] < 1:
        fail("missing semantic lineage graph")
    if summary["second_order_feedback_count"] < 6:
        fail("observer loop inactive")

    if not all(event.get("cause_chain") and event.get("semantic_claim") for event in record["observation_events"]):
        fail("observation event lacks cause chain or semantic claim")
    if not all(node.get("origin_observation") for node in record["rule_ancestry_graph"]["nodes"]):
        fail("rule origin history missing")
    if not any(edge["edge_type"] == "meaning_transition" for edge in record["semantic_lineage_graph"]["edges"]):
        fail("semantic meaning transitions missing")
    if not any("why_this_rule_emerged" in item for item in record["self_descriptions"]):
        fail("self-description missing rule explanation")
    if not all(event["second_order_feedback"] for event in record["observer_loop"]):
        fail("observer loop feedback not second-order")

    required_boundaries = {
        "abstract_signal_objects_only",
        "no_real_api_calls",
        "no_external_repo_execution",
        "no_permission_expansion",
        "does_not_change_v0_5_evolution_mechanics",
        "local_reproducible_simulation_only",
    }
    if not required_boundaries.issubset(boundaries):
        fail("required safety boundaries missing")

    print(
        "SAEE_V0_6_SMOKE: PASS "
        f"generation={record['generation_id']} "
        f"observed={summary['observed_generation_count']} "
        f"rules={summary['rule_genesis_count']} "
        f"explanations={summary['fitness_explanation_count']} "
        f"feedback={summary['second_order_feedback_count']}"
    )


if __name__ == "__main__":
    main()
