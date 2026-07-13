"""Reflexive coupling quantification."""

from __future__ import annotations

import math
from typing import Any

from saee_v1_2.metrics.reflexivity_metrics import (
    coupling_strength_coefficient,
    reflexive_feedback_strength,
)


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return 0.0
    return round(numerator / (denom_x * denom_y), 6)


class ReflexiveCouplingQuantifier:
    """Measure impact of observer state on transformation and selection."""

    def quantify(self, trace: list[dict[str, Any]]) -> dict[str, Any]:
        feedback = reflexive_feedback_strength(trace)
        pressures = [item["reflexive_pressure"] for item in feedback]
        mutation_influence = [item["mean_mutation_influence"] for item in feedback]
        selection_concentration = []
        for state in trace:
            masses = [item["mass"] for item in state["population"].values()]
            selection_concentration.append(max(masses) if masses else 0.0)
        impact_on_t = abs(_pearson(pressures, mutation_influence))
        impact_on_s = abs(_pearson(pressures, selection_concentration))
        coefficient = coupling_strength_coefficient(feedback)
        return {
            "analysis_type": "reflexive_coupling_quantification",
            "feedback_series": feedback,
            "impact_on_transformation": impact_on_t,
            "impact_on_selection": impact_on_s,
            "coupling_strength_coefficient": coefficient,
            "coupling_summary": {
                "observer_influences_transformation": impact_on_t > 0.05,
                "observer_influences_selection": impact_on_s > 0.05,
                "combined_observed_coupling": round((impact_on_t + impact_on_s + coefficient) / 3.0, 6),
            },
        }

