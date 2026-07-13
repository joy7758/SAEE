"""Selection driven by semantic coherence and epistemic fitness."""

from __future__ import annotations

import copy
import hashlib
from typing import Any


def stable_digest(parts: list[str], size: int = 10) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:size]


class SemanticSelectionEngine:
    """Resolve survival with semantic coherence as selection pressure."""

    def resolve(
        self,
        epistemic_scored: list[dict[str, Any]],
        feedback: dict[str, Any],
        self_model: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        mechanism_id = f"semantic_selection_g{generation_index:03d}_{stable_digest([feedback['feedback_id'], self_model['self_model_id']])}"
        annotated = [self._annotate(item, feedback, self_model) for item in epistemic_scored]
        base_ranked = sorted(annotated, key=lambda item: (item["generated_fitness"]["score"], item["genome"]["id"]), reverse=True)
        semantic_ranked = sorted(annotated, key=lambda item: (item["semantic_selection_score"], item["genome"]["id"]), reverse=True)
        survival_count = max(4, int(len(semantic_ranked) * (0.46 + feedback["semantic_coherence"] * 0.10)))
        dormant_count = min(4, max(1, int(len(semantic_ranked) * 0.16)))
        survivors = semantic_ranked[:survival_count]
        dormant = semantic_ranked[survival_count : survival_count + dormant_count]
        extinct = semantic_ranked[survival_count + dormant_count :]
        changed = {item["genome"]["id"] for item in semantic_ranked[:survival_count]} != {item["genome"]["id"] for item in base_ranked[:survival_count]}
        return {
            "mechanism_id": mechanism_id,
            "semantic_selection_pressure": {
                "feedback_input_id": feedback["feedback_id"],
                "semantic_coherence": feedback["semantic_coherence"],
                "self_model_id": self_model["self_model_id"],
                "meaning_coherence_weight": 0.28,
                "epistemic_weight": 0.36,
            },
            "epistemic_changed_outcome": changed,
            "survival_set": [self._mark(item, "survival", "active", mechanism_id, feedback) for item in survivors],
            "dormant_set": [self._mark(item, "dormancy", "dormant", mechanism_id, feedback) for item in dormant],
            "extinction_set": [self._mark(item, "extinction", "extinct", mechanism_id, feedback) for item in extinct],
            "revival_set": [],
        }

    def _annotate(self, item: dict[str, Any], feedback: dict[str, Any], self_model: dict[str, Any]) -> dict[str, Any]:
        annotated = copy.deepcopy(item)
        epistemic = item["epistemic_fitness"]
        semantic_bonus = feedback["semantic_coherence"] * 0.18 + epistemic["self_model_alignment"] * 0.16
        inconsistency_penalty = (1.0 - epistemic["explanation_quality"]) * feedback["interpretation_pressure"] * 0.20
        score = epistemic["epistemic_score"] + semantic_bonus - inconsistency_penalty
        annotated["semantic_selection_score"] = round(max(0.0, min(1.0, score)), 6)
        return annotated

    def _mark(
        self,
        item: dict[str, Any],
        event: str,
        status: str,
        mechanism_id: str,
        feedback: dict[str, Any],
    ) -> dict[str, Any]:
        genome = copy.deepcopy(item["genome"])
        genome["status"] = status
        genome["selection_score"] = item["semantic_selection_score"]
        genome.setdefault("selection_events", [])
        genome["selection_events"].append(
            {
                "event": event,
                "mechanism_id": mechanism_id,
                "feedback_input_id": feedback["feedback_id"],
                "semantic_selection_score": item["semantic_selection_score"],
                "semantic_coherence": feedback["semantic_coherence"],
                "epistemic_score": item["epistemic_fitness"]["epistemic_score"],
            }
        )
        genome.setdefault("interpretation_history", [])
        genome["interpretation_history"].append(
            {
                "feedback_input_id": feedback["feedback_id"],
                "selection_meaning": event,
                "semantic_selection_score": item["semantic_selection_score"],
            }
        )
        return genome
