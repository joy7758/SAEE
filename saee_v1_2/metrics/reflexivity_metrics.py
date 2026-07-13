"""Reflexive coupling metrics."""

from __future__ import annotations

from typing import Any


def reflexive_feedback_strength(trace: list[dict[str, Any]]) -> list[dict[str, float]]:
    series = []
    for index, state in enumerate(trace):
        pressure = float(state["observer"]["reflexive_pressure"])
        if index == 0:
            delta = 0.0
        else:
            delta = pressure - float(trace[index - 1]["observer"]["reflexive_pressure"])
        mutation_influence = [
            float(edge["mutation_influence"])
            for edge in state.get("lineage", [])
            if edge["generation"] == state["generation"]
        ]
        mean_mutation = sum(mutation_influence) / max(1, len(mutation_influence))
        series.append(
            {
                "generation": state["generation"],
                "reflexive_pressure": round(pressure, 6),
                "pressure_delta": round(delta, 6),
                "mean_mutation_influence": round(mean_mutation, 6),
                "feedback_strength": round(abs(delta) + mean_mutation, 6),
            }
        )
    return series


def coupling_strength_coefficient(series: list[dict[str, float]]) -> float:
    if not series:
        return 0.0
    return round(sum(item["feedback_strength"] for item in series) / len(series), 6)

