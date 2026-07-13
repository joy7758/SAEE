#!/usr/bin/env python3
"""Bootstrap SAEE v1.0 stable evolutionary runtime locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from saee_v1_0.runtime.saee_runtime import load_seed, run_runtime, write_outputs


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_v1_0" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v1.0 stable runtime")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=12)
    parser.add_argument("--population-size", type=int, default=8)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    record = run_runtime(seed, args.generations, args.population_size)
    write_outputs(record, args.output_dir)
    summary = record["stability_summary"]
    if record["loop_count"] != 1:
        raise SystemExit("SAEE_V1_0_BOOTSTRAP: FAIL loop_count is not 1")
    if not summary["single_population_pool"]:
        raise SystemExit("SAEE_V1_0_BOOTSTRAP: FAIL population is not single pool")
    if not summary["single_unified_fitness"]:
        raise SystemExit("SAEE_V1_0_BOOTSTRAP: FAIL fitness is not unified")
    if not summary["single_lineage_graph"]:
        raise SystemExit("SAEE_V1_0_BOOTSTRAP: FAIL lineage is not single graph")
    if summary["forbidden_runtime_layers"]:
        raise SystemExit("SAEE_V1_0_BOOTSTRAP: FAIL forbidden runtime layers present")
    print(
        "SAEE_V1_0_BOOTSTRAP: PASS "
        f"generations={record['generation_count']} "
        f"population={len(record['population'])} "
        f"loop_count={record['loop_count']} "
        f"fitness={record['fitness_model']} "
        f"lineage={record['lineage_model']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

