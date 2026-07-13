"""Stability analysis for SAEE v1.0 long-horizon experiments."""

from __future__ import annotations

from statistics import mean, variance
from typing import Any


class StabilityAnalyzer:
    """Measure fitness variance, collapse events, branching, and convergence."""

    def analyze(self, experiment_record: dict[str, Any], trace: list[dict[str, Any]]) -> dict[str, Any]:
        kernel = experiment_record["kernel_record"]
        fitness_by_generation = []
        collapse_events = []
        for item in trace:
            scores = [float(score["score"]) for score in item["fitness_values"]]
            generation_variance = variance(scores) if len(scores) > 1 else 0.0
            population_count = len(item["population_state"])
            if population_count < 2 or item["selection_result"]["survivor_count"] == 0:
                collapse_events.append(
                    {
                        "generation_index": item["generation_index"],
                        "population_count": population_count,
                        "reason": "population_below_viable_threshold",
                    }
                )
            fitness_by_generation.append(
                {
                    "generation_index": item["generation_index"],
                    "mean_fitness": round(mean(scores), 6) if scores else 0.0,
                    "max_fitness": round(max(scores), 6) if scores else 0.0,
                    "min_fitness": round(min(scores), 6) if scores else 0.0,
                    "fitness_variance": round(generation_variance, 8),
                    "population_count": population_count,
                }
            )
        lineage = kernel["lineage_dag"]
        branching_density = round(len(lineage["edges"]) / max(1, len(lineage["nodes"])), 6)
        convergence = self._convergence_tendency(fitness_by_generation)
        return {
            "analysis_type": "stability_analysis",
            "generation_count": kernel["generation_count"],
            "collapse_event_count": len(collapse_events),
            "collapse_events": collapse_events,
            "fitness_over_time": fitness_by_generation,
            "fitness_variance_mean": round(mean(item["fitness_variance"] for item in fitness_by_generation), 8)
            if fitness_by_generation
            else 0.0,
            "lineage_branching_density": branching_density,
            "convergence_tendency": convergence,
            "kernel_modified": False,
            "observation_only": True,
        }

    def _convergence_tendency(self, series: list[dict[str, Any]]) -> str:
        if len(series) < 10:
            return "insufficient_horizon"
        first_window = mean(item["fitness_variance"] for item in series[:10])
        last_window = mean(item["fitness_variance"] for item in series[-10:])
        if last_window < first_window * 0.75:
            return "converging"
        if last_window > first_window * 1.25:
            return "diverging"
        return "stable_variance"

