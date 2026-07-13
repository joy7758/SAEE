"""Recursive self-model of the evolution process."""

from __future__ import annotations

import hashlib
from typing import Any


class EvolutionSelfModel:
    """Maintain a model of how the system understands its own evolution."""

    def __init__(self) -> None:
        self.state = {
            "self_model_id": "self_model_seed",
            "generation_index": 0,
            "understanding_quality": 0.42,
            "dominant_meaning_terms": ["seed", "explainability"],
            "model_history": [],
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "self_model_id": self.state["self_model_id"],
            "generation_index": self.state["generation_index"],
            "understanding_quality": self.state["understanding_quality"],
            "dominant_meaning_terms": list(self.state["dominant_meaning_terms"]),
            "model_history": list(self.state["model_history"]),
        }

    def update(
        self,
        generation_index: int,
        feedback: dict[str, Any],
        observer_result: dict[str, Any],
        interpretation_pressure: dict[str, Any],
    ) -> dict[str, Any]:
        quality = round(
            max(
                0.05,
                min(
                    1.0,
                    self.state["understanding_quality"] * 0.52
                    + feedback["global_explanation_quality"] * 0.25
                    + feedback["semantic_coherence"] * 0.18
                    + (1.0 - interpretation_pressure["interpretation_pressure"]) * 0.05,
                ),
            ),
            6,
        )
        terms = list(dict.fromkeys(feedback["dominant_terms"] + self.state["dominant_meaning_terms"]))[:8]
        digest = hashlib.sha256("|".join([feedback["feedback_id"], *terms]).encode("utf-8")).hexdigest()[:10]
        event = {
            "generation_index": generation_index,
            "previous_self_model_id": self.state["self_model_id"],
            "feedback_id": feedback["feedback_id"],
            "observer_event_id": observer_result["observer_event"]["observation_event_id"],
            "interpretation_pressure": interpretation_pressure["interpretation_pressure"],
            "understanding_quality": quality,
        }
        self.state["self_model_id"] = f"self_model_g{generation_index:03d}_{digest}"
        self.state["generation_index"] = generation_index
        self.state["understanding_quality"] = quality
        self.state["dominant_meaning_terms"] = terms
        self.state["model_history"].append(event)
        return self.snapshot()
