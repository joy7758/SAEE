#!/usr/bin/env python3
"""Bootstrap SAEE v0.4 phase-transition evolution space locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_4.kernel.runtime import SAEEV04Runtime, load_seed, write_outputs


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_v0_4" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v0.4 phase-transition bootstrap")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=5)
    parser.add_argument("--initial-population-size", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    runtime = SAEEV04Runtime(seed, initial_population_size=args.initial_population_size)
    record = runtime.run(args.generations)
    write_outputs(record, args.output_dir)
    summary = record["phase_transition_summary"]
    if len(summary["regime_counts"]) < 2:
        raise SystemExit("SAEE_V0_4_BOOTSTRAP: FAIL fewer than two regimes")
    if len(summary["selection_topology_counts"]) < 2:
        raise SystemExit("SAEE_V0_4_BOOTSTRAP: FAIL fewer than two selection topologies")
    print(
        "SAEE_V0_4_BOOTSTRAP: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])} "
        f"regimes={','.join(sorted(summary['regime_counts']))} "
        f"topologies={','.join(sorted(summary['selection_topology_counts']))} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
