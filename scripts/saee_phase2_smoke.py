#!/usr/bin/env python3
"""Smoke test for SAEE Phase II behavior science."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_phase2.runtime.phase2_behavior_runtime import Phase2BehaviorRuntime, generate_v08_observation


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_PHASE2_SMOKE: FAIL: {message}")


def main() -> None:
    source = generate_v08_observation(SEED, generations=6, initial_population_size=5)
    record = Phase2BehaviorRuntime().analyze_record(source)
    summary = record["phase2_summary"]
    boundaries = set(record["boundaries"])

    if record["status"] != "local_phase2_behavior_science_analysis":
        fail("unexpected status")
    if summary["evolution_modified"]:
        fail("phase II modified evolution")
    if not summary["analysis_only"]:
        fail("analysis_only flag missing")
    if summary["generation_count"] < 6:
        fail("insufficient generations observed")
    if summary["attractor_count"] < 1:
        fail("attractor states not identifiable")
    if summary["dominant_regime"] not in {"stable_regime", "exploratory_regime", "chaotic_regime", "collapse_regime"}:
        fail("regime classification invalid")
    if summary["lineage_node_count"] < 1 or summary["lineage_edge_count"] < 1:
        fail("lineage topology not analyzable")
    if summary["law_count"] < 1:
        fail("evolution laws not extracted")
    if record["cross_generation_drift"]["drift_summary"]["semantic_drift_state"] not in {"bounded", "unbounded"}:
        fail("semantic drift not measured")
    if not record["behavior_analysis"]["behavioral_motifs"]:
        fail("behavioral motifs missing")
    if not record["invariants"]["invariants"]:
        fail("invariants missing")

    required_boundaries = {
        "analysis_only",
        "no_evolution_kernel_modification",
        "no_new_mutation_mechanics",
        "no_new_selection_mechanics",
        "no_external_repo_execution",
        "local_reproducible_analysis_only",
    }
    if not required_boundaries.issubset(boundaries):
        fail("required analysis boundaries missing")

    print(
        "SAEE_PHASE2_SMOKE: PASS "
        f"generations={summary['generation_count']} "
        f"attractors={summary['attractor_count']} "
        f"regime={summary['dominant_regime']} "
        f"laws={summary['law_count']} "
        f"analysis_only={summary['analysis_only']}"
    )


if __name__ == "__main__":
    main()

