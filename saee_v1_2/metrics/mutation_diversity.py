"""Mutation diversity metrics."""

from __future__ import annotations

from typing import Any


def mutation_diversity_index(trace: list[dict[str, Any]]) -> list[dict[str, float]]:
    """Measure diversity of mutation influence values per generation."""
    series = []
    for state in trace:
        generation = state["generation"]
        influences = [
            round(float(edge["mutation_influence"]), 4)
            for edge in state.get("lineage", [])
            if edge["generation"] == generation
        ]
        unique = len(set(influences))
        total = len(influences)
        diversity = unique / total if total else 0.0
        series.append(
            {
                "generation": generation,
                "mutation_event_count": total,
                "mutation_diversity_index": round(diversity, 6),
            }
        )
    return series

