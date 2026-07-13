#!/usr/bin/env python3
"""Bootstrap SAEE v0.7 reflexive evolution locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from saee_v0_7.runtime.reflexive_kernel import ReflexiveEvolutionKernel, load_seed, write_outputs


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_v0_7" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v0.7 reflexive evolution bootstrap")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--initial-population-size", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    runtime = ReflexiveEvolutionKernel(seed, initial_population_size=args.initial_population_size)
    record = runtime.run(args.generations)
    write_outputs(record, args.output_dir)
    summary = record["reflexive_summary"]
    if summary["explanation_driven_mutation_count"] < 1:
        raise SystemExit("SAEE_V0_7_BOOTSTRAP: FAIL explanation-driven mutation missing")
    if summary["feedback_input_count"] < args.generations - 1:
        raise SystemExit("SAEE_V0_7_BOOTSTRAP: FAIL feedback did not enter loop")
    if summary["epistemic_changed_outcome_count"] < 1:
        raise SystemExit("SAEE_V0_7_BOOTSTRAP: FAIL epistemic fitness did not change outcome")
    print(
        "SAEE_V0_7_BOOTSTRAP: PASS "
        f"generation={record['generation_id']} "
        f"mutations={summary['explanation_driven_mutation_count']} "
        f"feedback={summary['feedback_input_count']} "
        f"semantic_selection={summary['semantic_selection_count']} "
        f"changed={summary['epistemic_changed_outcome_count']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
