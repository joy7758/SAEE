#!/usr/bin/env python3
"""Bootstrap SAEE v0.8 identity-stable reflexive evolution locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from saee_v0_8.runtime.identity_stable_kernel import IdentityStableKernel, load_seed, write_outputs


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_v0_8" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v0.8 identity-stable reflexive evolution bootstrap")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--initial-population-size", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    runtime = IdentityStableKernel(seed, initial_population_size=args.initial_population_size)
    record = runtime.run(args.generations)
    write_outputs(record, args.output_dir)
    summary = record["stability_summary"]
    if not summary["identity_kernel_stable"]:
        raise SystemExit("SAEE_V0_8_BOOTSTRAP: FAIL identity kernel is unstable")
    if summary["max_semantic_drift_after"] > summary["semantic_drift_threshold"]:
        raise SystemExit("SAEE_V0_8_BOOTSTRAP: FAIL semantic drift exceeds threshold")
    if summary["continuity_break_count"]:
        raise SystemExit("SAEE_V0_8_BOOTSTRAP: FAIL identity continuity break detected")
    if summary["observer_boundary_count"] < args.generations:
        raise SystemExit("SAEE_V0_8_BOOTSTRAP: FAIL observer boundary missing")
    print(
        "SAEE_V0_8_BOOTSTRAP: PASS "
        f"generation={record['generation_id']} "
        f"identity_stable={summary['identity_kernel_stable']} "
        f"max_drift={summary['max_semantic_drift_after']} "
        f"bounded={summary['bounded_drift_intervention_count']} "
        f"continuity_breaks={summary['continuity_break_count']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

