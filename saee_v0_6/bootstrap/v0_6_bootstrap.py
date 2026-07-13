#!/usr/bin/env python3
"""Bootstrap SAEE v0.6 evolution observability locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from saee_v0_6.runtime.observable_kernel import ObservableEvolutionKernel, load_seed, write_outputs


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_v0_6" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v0.6 observability bootstrap")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--initial-population-size", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    runtime = ObservableEvolutionKernel(seed, initial_population_size=args.initial_population_size)
    record = runtime.run(args.generations)
    write_outputs(record, args.output_dir)
    summary = record["observability_summary"]
    if summary["observed_generation_count"] < args.generations:
        raise SystemExit("SAEE_V0_6_BOOTSTRAP: FAIL missing observed generations")
    if summary["rule_genesis_count"] < args.generations:
        raise SystemExit("SAEE_V0_6_BOOTSTRAP: FAIL missing rule genesis")
    if summary["second_order_feedback_count"] < args.generations:
        raise SystemExit("SAEE_V0_6_BOOTSTRAP: FAIL observer loop inactive")
    print(
        "SAEE_V0_6_BOOTSTRAP: PASS "
        f"generation={record['generation_id']} "
        f"observed={summary['observed_generation_count']} "
        f"rules={summary['rule_genesis_count']} "
        f"explanations={summary['fitness_explanation_count']} "
        f"feedback={summary['second_order_feedback_count']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
