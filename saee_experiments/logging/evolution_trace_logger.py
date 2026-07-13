"""Immutable trace logging for long-horizon experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvolutionTraceLogger:
    """Write per-generation observation traces without kernel feedback."""

    def build_trace(self, experiment_record: dict[str, Any]) -> list[dict[str, Any]]:
        kernel_record = experiment_record["kernel_record"]
        fitness_by_generation: dict[int, list[dict[str, Any]]] = {}
        for score in kernel_record["fitness_scores"]:
            fitness_by_generation.setdefault(int(score["generation_index"]), []).append(score)
        trace = []
        for generation in kernel_record["generation_log"]:
            generation_index = int(generation["generation_index"])
            selected_ids = {genome["id"] for genome in generation["population"]}
            fitness_values = fitness_by_generation.get(generation_index, [])
            rejected_ids = sorted(
                score["genome_id"]
                for score in fitness_values
                if score["genome_id"] not in selected_ids
            )
            trace.append(
                {
                    "generation_index": generation_index,
                    "generation_id": generation["generation_id"],
                    "signals": generation["signals"],
                    "population_state": generation["population"],
                    "fitness_values": fitness_values,
                    "selection_result": {
                        "selected_ids": sorted(selected_ids),
                        "rejected_ids": rejected_ids,
                        "survivor_count": generation["survivor_count"],
                        "rejected_count": generation["rejected_count"],
                    },
                    "lineage_update": {
                        "lineage_model": kernel_record["lineage_model"],
                        "graph_type": kernel_record["lineage_dag"]["graph_type"],
                    },
                    "observation_only": True,
                }
            )
        return trace

    def write_jsonl(self, trace: list[dict[str, Any]], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for item in trace:
                handle.write(json.dumps(item, sort_keys=True) + "\n")

