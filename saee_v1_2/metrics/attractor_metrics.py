"""Attractor convergence metrics."""

from __future__ import annotations

import math
from typing import Any


def population_centroid(state: dict[str, Any]) -> tuple[float, ...]:
    population = state["population"]
    if not population:
        return tuple()
    dimensions = len(next(iter(population.values()))["vector"])
    centroid = []
    for dim in range(dimensions):
        centroid.append(
            sum(item["vector"][dim] * item["mass"] for item in population.values())
        )
    return tuple(round(value, 6) for value in centroid)


def centroid_distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if not a or not b:
        return 0.0
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def attractor_convergence_rate(trace: list[dict[str, Any]]) -> list[dict[str, float]]:
    if not trace:
        return []
    final_centroid = population_centroid(trace[-1])
    distances = [
        {
            "generation": state["generation"],
            "distance_to_terminal_centroid": round(centroid_distance(population_centroid(state), final_centroid), 6),
        }
        for state in trace
    ]
    initial = distances[0]["distance_to_terminal_centroid"]
    for item in distances:
        if initial <= 0:
            item["convergence_rate"] = 1.0
        else:
            item["convergence_rate"] = round(1.0 - item["distance_to_terminal_centroid"] / initial, 6)
    return distances

