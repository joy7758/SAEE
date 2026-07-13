"""SAEE v1.0 stable runtime entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_v1_0.kernel.evolution_loop import EvolutionLoopKernel


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_runtime(seed_genome: dict[str, Any], generations: int, population_size: int) -> dict[str, Any]:
    return EvolutionLoopKernel(seed_genome, population_size=population_size).run(generations)


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "run_record.json": record,
        "population.json": record["population"],
        "lineage_dag.json": record["lineage_dag"],
        "fitness_scores.json": record["fitness_scores"],
        "generation_log.json": record["generation_log"],
        "stability_summary.json": record["stability_summary"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

