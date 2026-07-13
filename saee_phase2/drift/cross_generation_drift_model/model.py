"""Measure structural, semantic, and behavioral drift across generations."""

from __future__ import annotations

from typing import Any


class CrossGenerationDriftModel:
    """Measure drift without changing evolution state."""

    def measure(self, behavior: dict[str, Any], regimes: dict[str, Any], topology: dict[str, Any]) -> dict[str, Any]:
        trajectory = behavior["trajectory"]
        structural_series = []
        semantic_series = []
        behavioral_series = []
        previous_point = None
        previous_regime = None
        regimes_by_generation = {
            item["generation_index"]: item["regime"]
            for item in regimes["classifications"]
        }
        for point in trajectory:
            generation = point["generation_index"]
            structural_delta = 0 if previous_point is None else point["population_count"] - previous_point["population_count"]
            semantic_delta = 0.0 if previous_point is None else round(point["semantic_drift_after"] - previous_point["semantic_drift_after"], 6)
            regime = regimes_by_generation[generation]
            behavioral_delta = 0 if previous_regime in (None, regime) else 1
            structural_series.append(
                {
                    "generation_index": generation,
                    "population_count": point["population_count"],
                    "structural_delta": structural_delta,
                }
            )
            semantic_series.append(
                {
                    "generation_index": generation,
                    "semantic_drift_after": point["semantic_drift_after"],
                    "semantic_delta": semantic_delta,
                }
            )
            behavioral_series.append(
                {
                    "generation_index": generation,
                    "regime": regime,
                    "regime_change": behavioral_delta,
                }
            )
            previous_point = point
            previous_regime = regime
        max_semantic = max((item["semantic_drift_after"] for item in semantic_series), default=0.0)
        return {
            "analysis_type": "cross_generation_drift_model",
            "structural_drift": structural_series,
            "semantic_drift": semantic_series,
            "behavioral_drift": behavioral_series,
            "drift_summary": {
                "structural_drift_total": sum(abs(item["structural_delta"]) for item in structural_series),
                "semantic_drift_max": max_semantic,
                "semantic_drift_state": "bounded" if max_semantic <= 0.32 else "unbounded",
                "behavioral_regime_changes": sum(item["regime_change"] for item in behavioral_series),
                "topology_diversity_change": topology["diversity_change"],
            },
        }

