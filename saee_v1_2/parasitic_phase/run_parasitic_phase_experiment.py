#!/usr/bin/env python3
"""Run the SAEE v1.2 local parasitic phase experiment set."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.parasitic_phase.model import (
    STATISTICAL_SEED_MINIMUM,
    run_experiment_set,
    write_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=160)
    parser.add_argument(
        "--output-dir",
        default="saee_v1_2/parasitic_phase/results/scientific-closure-demo",
        help="Local output directory for Phi, entropy, dominance, and SAEE trace outputs.",
    )
    parser.add_argument(
        "--statistical-seeds",
        type=int,
        default=STATISTICAL_SEED_MINIMUM,
        help="Stochastic seeds per A/B/C experiment for statistical_summary.json.",
    )
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    results = run_experiment_set(steps=args.steps)
    write_outputs(results, output_dir, statistical_seed_count=args.statistical_seeds)
    for result in results:
        summary = result.summary()
        print(
            "SAEE_PARASITIC_PHASE_EXPERIMENT: "
            f"{summary['experiment_id']} "
            f"governance={summary['governance']} "
            f"phase_transition_step={summary['phase_transition_step']} "
            f"final_phi={summary['final_phi']} "
            f"final_entropy={summary['final_entropy']} "
            f"final_dominance={summary['final_agent_dominance']}"
        )
    print(f"SAEE_PARASITIC_PHASE_EXPERIMENT: output={output_dir}")
    print(
        "SAEE_PARASITIC_PHASE_EXPERIMENT: "
        f"statistical_seeds_per_experiment={args.statistical_seeds}"
    )


if __name__ == "__main__":
    main()
