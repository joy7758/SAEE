"""Classify observed evolutionary regimes."""

from __future__ import annotations

from typing import Any


class RegimeClassificationSystem:
    """Classify behavior into stable, exploratory, chaotic, or collapse regimes."""

    def classify(self, behavior: dict[str, Any], attractors: dict[str, Any]) -> dict[str, Any]:
        classifications = []
        previous = None
        transitions = []
        attractor_generations = {
            generation
            for attractor in attractors["attractors"]
            for generation in attractor["support_generations"]
        }
        for point in behavior["trajectory"]:
            regime = self._classify_point(point, point["generation_index"] in attractor_generations)
            item = {
                "generation_index": point["generation_index"],
                "regime": regime,
                "evidence": {
                    "semantic_drift_after": point["semantic_drift_after"],
                    "identity_break_count": point["identity_break_count"],
                    "population_count": point["population_count"],
                    "mutation_event_count": point["mutation_event_count"],
                },
            }
            classifications.append(item)
            if previous and previous["regime"] != regime:
                transitions.append(
                    {
                        "from_generation": previous["generation_index"],
                        "to_generation": point["generation_index"],
                        "from_regime": previous["regime"],
                        "to_regime": regime,
                    }
                )
            previous = item
        regime_counts: dict[str, int] = {}
        for item in classifications:
            regime_counts[item["regime"]] = regime_counts.get(item["regime"], 0) + 1
        return {
            "analysis_type": "regime_classification",
            "classifications": classifications,
            "regime_counts": regime_counts,
            "transitions": transitions,
            "dominant_regime": max(regime_counts, key=regime_counts.get) if regime_counts else "unknown",
        }

    def _classify_point(self, point: dict[str, Any], in_attractor: bool) -> str:
        if point["identity_break_count"] > 0 or point["semantic_drift_after"] > 0.55:
            return "chaotic_regime"
        if point["population_count"] <= 2:
            return "collapse_regime"
        if in_attractor and point["semantic_drift_after"] <= 0.32:
            return "stable_regime"
        if point["mutation_event_count"] >= 4:
            return "exploratory_regime"
        return "stable_regime"

