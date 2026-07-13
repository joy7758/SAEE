"""Meaning feedback loop that turns explanations into evolutionary pressure."""

from __future__ import annotations

import hashlib
from typing import Any


class MeaningFeedbackLoop:
    """Produce semantic feedback from prior self-descriptions and explanations."""

    def __init__(self) -> None:
        self.feedback_events: list[dict[str, Any]] = []

    def seed(self) -> dict[str, Any]:
        feedback = {
            "feedback_id": "meaning_feedback_seed",
            "generation_index": 0,
            "global_explanation_quality": 0.50,
            "semantic_coherence": 0.50,
            "interpretation_pressure": 0.50,
            "genome_explanation_quality": {},
            "dominant_terms": ["seed", "explainability"],
            "source_description_id": None,
        }
        self.feedback_events.append(feedback)
        return feedback

    def update(
        self,
        generation_index: int,
        self_description: dict[str, Any],
        fitness_explanations: list[dict[str, Any]],
        semantic_graph: dict[str, Any],
    ) -> dict[str, Any]:
        quality_by_genome = {
            item["genome_id"]: self._quality(item)
            for item in fitness_explanations
        }
        global_quality = sum(quality_by_genome.values()) / max(1, len(quality_by_genome))
        semantic_coherence = min(1.0, 0.35 + len(semantic_graph.get("edges", [])) / max(12, len(semantic_graph.get("nodes", [])) + 1))
        interpretation_pressure = max(0.05, min(0.95, 1.0 - global_quality * 0.55 + (1.0 - semantic_coherence) * 0.35))
        terms = self._terms(self_description)
        digest = hashlib.sha256("|".join([self_description["description_id"], *terms]).encode("utf-8")).hexdigest()[:10]
        feedback = {
            "feedback_id": f"meaning_feedback_g{generation_index:03d}_{digest}",
            "generation_index": generation_index,
            "global_explanation_quality": round(global_quality, 6),
            "semantic_coherence": round(semantic_coherence, 6),
            "interpretation_pressure": round(interpretation_pressure, 6),
            "genome_explanation_quality": quality_by_genome,
            "dominant_terms": terms[:6],
            "source_description_id": self_description["description_id"],
        }
        self.feedback_events.append(feedback)
        return feedback

    def export(self) -> list[dict[str, Any]]:
        return list(self.feedback_events)

    def _quality(self, explanation: dict[str, Any]) -> float:
        top_factors = explanation.get("top_fitness_factors", [])
        has_factors = 1.0 if top_factors else 0.35
        score = float(explanation.get("selection_score", 0.0))
        return round(max(0.05, min(1.0, has_factors * 0.45 + score * 0.55)), 6)

    def _terms(self, self_description: dict[str, Any]) -> list[str]:
        text = " ".join(str(value) for value in self_description.values()).lower()
        raw = [token.strip(".,:;()[]{}") for token in text.split()]
        return [token for token in raw if len(token) > 5][:10] or ["meaning", "feedback"]
