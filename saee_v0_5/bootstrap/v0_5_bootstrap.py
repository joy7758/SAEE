#!/usr/bin/env python3
"""Bootstrap SAEE v0.5 open-ended evolution physics locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from saee_v0_5.runtime.physics_loop import OpenEndedPhysicsLoop, load_seed, write_outputs


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_v0_5" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v0.5 open-ended physics bootstrap")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--initial-population-size", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    runtime = OpenEndedPhysicsLoop(seed, initial_population_size=args.initial_population_size)
    record = runtime.run(args.generations)
    write_outputs(record, args.output_dir)
    summary = record["open_ended_physics_summary"]
    if summary["generated_law_count"] < args.generations:
        raise SystemExit("SAEE_V0_5_BOOTSTRAP: FAIL law generation incomplete")
    if summary["dimension_birth_count"] < 2:
        raise SystemExit("SAEE_V0_5_BOOTSTRAP: FAIL dimension birth missing")
    if summary["regime_regeneration_count"] < 1:
        raise SystemExit("SAEE_V0_5_BOOTSTRAP: FAIL regime regeneration missing")
    print(
        "SAEE_V0_5_BOOTSTRAP: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])} "
        f"laws={summary['generated_law_count']} "
        f"dimensions={summary['dimension_birth_count']} "
        f"regenerations={summary['regime_regeneration_count']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
