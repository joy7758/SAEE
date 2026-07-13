"""Drift monitoring for SAEE v1.0 long-horizon experiments."""

from __future__ import annotations

from statistics import mean
from typing import Any


class DriftMonitor:
    """Measure mutation accumulation and structural lineage drift."""

    def monitor(self, experiment_record: dict[str, Any], trace: list[dict[str, Any]]) -> dict[str, Any]:
        mutation_accumulation = []
        population_divergence = []
        previous_ids: set[str] | None = None
        for item in trace:
            genomes = item["population_state"]
            mutation_lengths = [len(genome.get("mutation_history", [])) for genome in genomes]
            current_ids = {genome["id"] for genome in genomes}
            if previous_ids is None:
                turnover = 0.0
            else:
                turnover = 1.0 - len(previous_ids & current_ids) / max(1, len(previous_ids | current_ids))
            previous_ids = current_ids
            mutation_accumulation.append(
                {
                    "generation_index": item["generation_index"],
                    "mean_mutation_history_length": round(mean(mutation_lengths), 6) if mutation_lengths else 0.0,
                    "max_mutation_history_length": max(mutation_lengths) if mutation_lengths else 0,
                }
            )
            population_divergence.append(
                {
                    "generation_index": item["generation_index"],
                    "population_turnover": round(turnover, 6),
                    "unique_population_ids": len(current_ids),
                }
            )
        lineage = experiment_record["kernel_record"]["lineage_dag"]
        structural_drift = {
            "node_count": len(lineage["nodes"]),
            "edge_count": len(lineage["edges"]),
            "edge_to_node_ratio": round(len(lineage["edges"]) / max(1, len(lineage["nodes"])), 6),
        }
        return {
            "analysis_type": "drift_monitor",
            "mutation_accumulation": mutation_accumulation,
            "population_divergence": population_divergence,
            "structural_drift": structural_drift,
            "mean_population_turnover": round(mean(item["population_turnover"] for item in population_divergence), 6)
            if population_divergence
            else 0.0,
            "observation_only": True,
        }

