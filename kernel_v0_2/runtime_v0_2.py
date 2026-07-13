"""SAEE Kernel v0.2 dynamic evolutionary ecology runtime.

Cycle:
Sense -> Signal Interpretation -> Population Expansion -> Mutation/Recombination
-> Sandbox Evaluation -> Dynamic Fitness Scoring -> Selection Pressure Resolution
-> Lineage Graph Update -> Population Reconfiguration.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kernel_v0_2.fitness.dynamic_landscape import DynamicFitnessLandscape
from kernel_v0_2.lineage_graph.graph import LineageGraph
from kernel_v0_2.population.population_pool import PopulationPool
from kernel_v0_2.selection.pressure_engine import SelectionPressureEngine
from kernel_v0_2.signals.signal_stream import AbstractSignalStream, SignalInterpreter


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT_DIR = ROOT / "kernel_v0_2" / "output" / "latest"
KERNEL_VERSION = "0.2.0"


class SAEEKernelV02:
    """Population-level local ecology runtime for SAEE."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 3) -> None:
        self.population_pool = PopulationPool()
        self.signal_stream = AbstractSignalStream()
        self.signal_interpreter = SignalInterpreter()
        self.fitness_landscape = DynamicFitnessLandscape()
        self.selection_pressure = SelectionPressureEngine()
        self.lineage_graph = LineageGraph()
        self.population = self.population_pool.from_seed(seed_genome, initial_population_size)
        self.generation_id = 0
        self.cycles: list[dict[str, Any]] = []
        self.lineage_graph.record_population(self.population, self.generation_id)

    def step(self) -> dict[str, Any]:
        self.generation_id += 1
        signal_packet = self.signal_stream.collect(self.generation_id)
        environment_state = self.signal_interpreter.interpret(signal_packet)
        candidates, branch_events = self.population_pool.expand(
            self.population,
            environment_state,
            self.generation_id,
        )
        self.lineage_graph.record_branch_events(candidates, branch_events)
        scored = self.fitness_landscape.score_population(candidates, self.generation_id, environment_state)
        decision = self.selection_pressure.resolve(scored, environment_state, self.population)
        self.lineage_graph.record_selection_decision(decision, self.generation_id)
        self.population = self.population_pool.reconfigure(decision)

        cycle = {
            "generation_id": f"generation-{self.generation_id:03d}",
            "environment_state": environment_state,
            "branch_events": branch_events,
            "fitness_scores": [
                {
                    "genome_id": item["genome"]["id"],
                    "fitness": item["fitness"],
                }
                for item in scored
            ],
            "selection_pressure": {
                "survival_set": [genome["id"] for genome in decision["survival_set"]],
                "extinction_set": [genome["id"] for genome in decision["extinction_set"]],
                "dormant_set": [genome["id"] for genome in decision["dormant_set"]],
                "revival_set": [genome["id"] for genome in decision["revival_set"]],
            },
            "population_size": len(self.population),
        }
        self.cycles.append(cycle)
        return cycle

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            self.step()

        return {
            "kernel": "SAEE Kernel v0.2",
            "version": KERNEL_VERSION,
            "status": "local_v0_2_evolutionary_ecology",
            "generation_id": f"generation-{self.generation_id:03d}",
            "population": self.population,
            "lineage_graph": self.lineage_graph.export(),
            "cycles": self.cycles,
            "boundaries": [
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_publication_claim",
                "not_production_runtime",
            ],
        }


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_run_record(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "population.json").write_text(
        json.dumps(record["population"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "lineage_graph.json").write_text(
        json.dumps(record["lineage_graph"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "run_record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE Kernel v0.2")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=4)
    parser.add_argument("--initial-population-size", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    kernel = SAEEKernelV02(seed, initial_population_size=args.initial_population_size)
    record = kernel.run(args.generations)
    write_run_record(record, args.output_dir)
    final_cycle = record["cycles"][-1]
    print(
        "SAEE_KERNEL_V0_2: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])} "
        f"extinct={len(final_cycle['selection_pressure']['extinction_set'])} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

