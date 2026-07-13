#!/usr/bin/env python3
"""Smoke test for SAEE v0.3 meta-evolution bootstrap."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_3.kernel.runtime import SAEEV03Runtime


SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_V0_3_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    runtime = SAEEV03Runtime(seed, initial_population_size=4)
    record = runtime.run(3)

    if record["status"] != "local_v0_3_meta_evolution":
        fail("unexpected status")
    if len(record["population"]) < 3:
        fail("population collapsed")
    if not record["lineage_graph"]["edges"]:
        fail("lineage DAG has no edges")
    if not record["lineage_graph"]["rule_graph"]["nodes"]:
        fail("rule graph has no nodes")
    if not any(cycle["meta_evolution"]["candidate_rule_id"] for cycle in record["cycles"]):
        fail("meta-evolution candidate missing")
    if not record["drift_guard"]["passed"]:
        fail("drift guard failed")
    if not all(cycle["environment_state"]["signal_mode"] == "abstract_local" for cycle in record["cycles"]):
        fail("non-abstract sensing detected")

    print(
        "SAEE_V0_3_SMOKE: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])} "
        f"rule={record['rule_genome']['id']}"
    )


if __name__ == "__main__":
    main()

