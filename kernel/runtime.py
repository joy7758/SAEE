"""SAEE Evolution Kernel v0.1 runtime loop.

Loop: Sense -> Branch -> Evaluate -> Select -> Lineage -> Update.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kernel.config import KERNEL_VERSION
from kernel.fitness.evaluator import FitnessEvaluator
from kernel.genome.brancher import GenomeBrancher
from kernel.lineage.tracker import LineageTracker
from kernel.selection.selector import Selector
from kernel.sense.sense_engine import SenseEngine


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT_DIR = ROOT / "kernel" / "output" / "latest"


class SAEEKernel:
    """Minimal local evolution loop: sense, branch, evaluate, select, record."""

    def __init__(self, seed_genome: dict[str, Any]) -> None:
        self.genome = seed_genome
        self.generation = int(seed_genome.get("version", 0))
        self.sense_engine = SenseEngine([])
        self.brancher = GenomeBrancher()
        self.evaluator = FitnessEvaluator()
        self.selector = Selector()
        self.lineage = LineageTracker()

    def step(self) -> dict[str, Any]:
        signals = self.sense_engine.sense()
        parent = self.genome
        offspring = self.brancher.branch(parent, signals)
        scored = [
            {
                "genome": genome,
                "fitness": self.evaluator.evaluate(genome, signals),
            }
            for genome in offspring
        ]
        selected_record = self.selector.select(scored)
        selected = selected_record["genome"]

        self.lineage.record(parent, offspring, selected, scored, signals)
        self.genome = selected
        self.generation = int(selected.get("version", self.generation + 1))
        return selected

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")

        for _ in range(generations):
            self.step()

        return {
            "kernel": "SAEE Evolution Kernel",
            "version": KERNEL_VERSION,
            "status": "local_v0_1_runnable",
            "generations": generations,
            "current_genome": self.genome,
            "lineage": self.lineage.history,
            "boundaries": [
                "mock_sensing_only",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_publication_claim",
            ],
        }


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_run_record(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "selected_genome.json").write_text(
        json.dumps(record["current_genome"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "lineage.json").write_text(
        json.dumps(record["lineage"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "run_record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE Evolution Kernel v0.1")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    kernel = SAEEKernel(seed)
    record = kernel.run(args.generations)
    write_run_record(record, args.output_dir)
    print(
        "SAEE_KERNEL_V0_1: PASS "
        f"generations={args.generations} "
        f"selected={record['current_genome']['id']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
