#!/usr/bin/env python3
"""Smoke test for SAEE v0.4 phase-transition bootstrap."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_4.kernel.runtime import SAEEV04Runtime


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V0_4_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    runtime = SAEEV04Runtime(seed, initial_population_size=5)
    record = runtime.run(5)
    summary = record["phase_transition_summary"]
    boundaries = set(record["boundaries"])

    if record["status"] != "local_v0_4_phase_transition":
        fail("unexpected status")
    if len(record["population"]) < 4:
        fail("population collapsed")
    if len(summary["regime_counts"]) < 2:
        fail("fewer than two ecological regimes")
    if len(summary["selection_topology_counts"]) < 2:
        fail("selection topology did not restructure")
    if "single_niche_to_multi_niche_emergence" not in summary["phase_counts"]:
        fail("niche emergence phase missing")
    if "collapse_pressure" not in summary["phase_counts"]:
        fail("collapse/reset phase missing")
    if len(summary["mutation_operator_mode_counts"]) < 2:
        fail("mutation operator modes did not change")
    if not record["lineage_graph"]["evolution_space_graph"]["edges"]:
        fail("evolution-space graph has no mutation edges")

    for cycle in record["cycles"]:
        space = cycle["evolution_space"]
        if not space["active_dimensions"]:
            fail("active dimensions missing")
        if not cycle["mutation_space"]["active_operators"]:
            fail("runtime mutation operators missing")
        if cycle["environment_state"]["signal_model"] != "abstract_signal_objects_only":
            fail("non-abstract signal model detected")

    required_boundaries = {
        "abstract_signal_objects_only",
        "no_real_api_calls",
        "no_external_repo_execution",
        "no_permission_expansion",
        "local_reproducible_simulation_only",
    }
    if not required_boundaries.issubset(boundaries):
        fail("required safety boundaries missing")

    print(
        "SAEE_V0_4_SMOKE: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])} "
        f"regimes={','.join(sorted(summary['regime_counts']))} "
        f"topologies={','.join(sorted(summary['selection_topology_counts']))}"
    )


if __name__ == "__main__":
    main()
