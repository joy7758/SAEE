#!/usr/bin/env python3
"""Run the public-safe SAEE toy abstraction demo.

This demo is intentionally simplified. It does not import or reproduce SAEE
private kernel, fitness, selection, lineage, mutation, or runtime logic.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis_layer.attractor_mapper_stub import map_toy_attractor
from analysis_layer.regime_classifier_stub import summarize_regimes
from experiment_layer.experiment_runner_stub import ToyExperimentConfig, run_toy_experiment
from experiment_layer.logging_tools import write_jsonl


def main() -> None:
    config = ToyExperimentConfig(generations=12, population_size=6)
    rows = run_toy_experiment(config)
    regime_counts = summarize_regimes(rows)
    attractor = map_toy_attractor(regime_counts)

    output_dir = ROOT / "demo" / "output"
    write_jsonl(output_dir / "toy_trace.jsonl", rows)

    print("SAEE_TOY_DEMO: PASS")
    print(f"rows={len(rows)}")
    print(f"regimes={regime_counts}")
    print(f"attractor={attractor}")


if __name__ == "__main__":
    main()

