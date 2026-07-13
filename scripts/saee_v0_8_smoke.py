#!/usr/bin/env python3
"""Smoke test for SAEE v0.8 identity-stable reflexive evolution."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_8.runtime.identity_stable_kernel import IdentityStableKernel


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V0_8_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    runtime = IdentityStableKernel(seed, initial_population_size=5)
    record = runtime.run(6)
    summary = record["stability_summary"]
    boundaries = set(record["boundaries"])

    if record["status"] != "local_v0_8_identity_stable_reflexive_evolution":
        fail("unexpected status")
    if not summary["identity_kernel_stable"]:
        fail("identity kernel changed across generations")
    if summary["identity_anchor_hash_count"] != 1:
        fail("more than one identity anchor hash observed")
    if summary["max_semantic_drift_after"] > summary["semantic_drift_threshold"]:
        fail("semantic drift exceeded threshold")
    if summary["bounded_drift_intervention_count"] < 1:
        fail("semantic drift controller never intervened")
    if summary["observer_boundary_count"] < 6:
        fail("observer feedback was not bounded every generation")
    if summary["bounded_observer_loop_count"] < 6:
        fail("bounded observer loop missing")
    if summary["continuity_break_count"] != 0:
        fail("identity continuity break detected")
    if summary["self_model_invariant_violation_count"] != 0:
        fail("self-model violated identity invariant")
    if summary["identity_selection_count"] < 6:
        fail("identity-aware selection missing")
    if summary["reflexive_source_generation_count"] < 6:
        fail("v0.7 reflexive source loop did not run")

    if not all(cycle["bounded_feedback"].get("identity_anchor_id") for cycle in record["cycles"]):
        fail("bounded feedback lacks identity anchor")
    if not all(cycle["bounded_self_model"].get("identity_anchor_id") for cycle in record["cycles"]):
        fail("bounded self-model lacks identity anchor")
    if not all(cycle["identity_lineage"]["status"] == "identity_continuity_preserved" for cycle in record["cycles"]):
        fail("identity lineage did not preserve continuity")
    if record["identity_preserving_lineage_graph"]["identity_breaks"]:
        fail("lineage graph recorded identity breaks")

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
        "SAEE_V0_8_SMOKE: PASS "
        f"generation={record['generation_id']} "
        f"identity_stable={summary['identity_kernel_stable']} "
        f"max_drift={summary['max_semantic_drift_after']} "
        f"bounded={summary['bounded_drift_intervention_count']} "
        f"breaks={summary['continuity_break_count']}"
    )


if __name__ == "__main__":
    main()

