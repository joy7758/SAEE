"""Epistemic fitness makes explainability a survival pressure."""

from __future__ import annotations

import copy
from typing import Any


class EpistemicFitnessLayer:
    """Combine generated fitness with explanation quality and self-model alignment."""

    def score(
        self,
        scored_population: list[dict[str, Any]],
        feedback: dict[str, Any],
        self_model: dict[str, Any],
    ) -> list[dict[str, Any]]:
        scored = []
        for item in scored_population:
            genome = copy.deepcopy(item["genome"])
            base_score = float(item["generated_fitness"]["score"])
            explanation_quality = feedback["genome_explanation_quality"].get(genome["id"], feedback["global_explanation_quality"])
            semantic_coherence = feedback["semantic_coherence"]
            self_model_alignment = self._self_model_alignment(genome, self_model)
            epistemic_score = round(
                max(
                    0.0,
                    min(
                        1.0,
                        base_score * 0.58
                        + explanation_quality * 0.20
                        + semantic_coherence * 0.13
                        + self_model_alignment * 0.09,
                    ),
                ),
                6,
            )
            epistemic_fitness = {
                "base_generated_score": base_score,
                "explanation_quality": explanation_quality,
                "semantic_coherence": semantic_coherence,
                "self_model_alignment": self_model_alignment,
                "epistemic_score": epistemic_score,
                "feedback_input_id": feedback["feedback_id"],
                "self_model_id": self_model["self_model_id"],
            }
            genome["fitness"] = item["generated_fitness"]
            genome["epistemic_fitness"] = epistemic_fitness
            scored.append(
                {
                    "genome": genome,
                    "generated_fitness": item["generated_fitness"],
                    "epistemic_fitness": epistemic_fitness,
                }
            )
        return scored

    def _self_model_alignment(self, genome: dict[str, Any], self_model: dict[str, Any]) -> float:
        generated_traits = " ".join(genome.get("traits", {}).get("generated_traits", [])).lower()
        model_terms = self_model.get("dominant_meaning_terms", [])
        if not model_terms:
            return 0.45
        matches = sum(1 for term in model_terms if term in generated_traits)
        return round(max(0.20, min(1.0, 0.34 + matches * 0.18 + self_model["understanding_quality"] * 0.24)), 6)
