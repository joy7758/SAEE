#!/usr/bin/env python3
"""Smoke test for SAEE Kernel v0.2."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kernel_v0_2.runtime_v0_2 import SAEEKernelV02


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"KERNEL_V0_2_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    kernel = SAEEKernelV02(seed, initial_population_size=3)
    record = kernel.run(4)

    if record["status"] != "local_v0_2_evolutionary_ecology":
        fail("unexpected run status")
    if len(record["population"]) < 2:
        fail("population collapsed below two genomes")
    if not record["lineage_graph"]["edges"]:
        fail("lineage graph has no edges")
    if not any(cycle["selection_pressure"]["extinction_set"] for cycle in record["cycles"]):
        fail("expected at least one extinction event")
    if not any(cycle["selection_pressure"]["dormant_set"] for cycle in record["cycles"]):
        fail("expected at least one dormancy event")
    if record["cycles"][-1]["environment_state"]["signal_mode"] != "abstract_local":
        fail("expected abstract local signals")
    last_fitness = record["cycles"][-1]["fitness_scores"][0]["fitness"]
    for key in ["generation_id", "environment_id", "population_pressure", "lineage_competition", "total"]:
        if key not in last_fitness:
            fail(f"fitness missing {key}")

    print(
        "KERNEL_V0_2_SMOKE: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])}"
    )


if __name__ == "__main__":
    main()

