"""Lineage entropy metrics."""

from __future__ import annotations

import math
from typing import Any


def lineage_entropy(trace: list[dict[str, Any]]) -> list[dict[str, float]]:
    """Measure lineage edge-weight entropy by generation."""
    series = []
    for state in trace:
        generation = state["generation"]
        edges = [edge for edge in state.get("lineage", []) if edge["generation"] <= generation]
        weights = [max(0.0, float(edge["weight"])) for edge in edges]
        total = sum(weights)
        if total <= 0:
            entropy = 0.0
        else:
            probabilities = [weight / total for weight in weights if weight > 0]
            entropy = -sum(prob * math.log(prob) for prob in probabilities)
        series.append({"generation": generation, "lineage_entropy": round(entropy, 6)})
    return series


def lineage_entropy_delta(series: list[dict[str, float]]) -> float:
    if len(series) < 2:
        return 0.0
    return round(series[-1]["lineage_entropy"] - series[0]["lineage_entropy"], 6)

