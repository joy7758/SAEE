"""Explanation-driven mutation engine for SAEE v0.7."""

from __future__ import annotations

import copy
import hashlib
from typing import Any


def stable_digest(parts: list[str], size: int = 8) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:size]


class ReflexiveMutationEngine:
    """Make explanation quality a causal input to mutation probability."""

    def generate(
        self,
        population: list[dict[str, Any]],
        law: dict[str, Any],
        dimensions: dict[str, Any],
        regime: dict[str, Any],
        feedback: dict[str, Any],
        self_model: dict[str, Any],
        generation_index: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        candidates = [copy.deepcopy(genome) for genome in population if genome.get("status") != "extinct"]
        active = [genome for genome in population if genome.get("status") == "active"]
        active_dimensions = [dimension for dimension in dimensions.values() if dimension.get("state") == "active"]
        clauses = law.get("clauses", []) or [{"clause_id": "seed_clause", "expression": "seed_expression"}]
        events: list[dict[str, Any]] = []
        feedback_id = feedback["feedback_id"]

        for index, parent in enumerate(active):
            explanation_quality = feedback["genome_explanation_quality"].get(parent["id"], feedback["global_explanation_quality"])
            mutation_probability = self._mutation_probability(explanation_quality, feedback, self_model, index)
            stable_by_understanding = (
                explanation_quality >= 0.70
                and feedback["semantic_coherence"] >= 0.90
                and index % 4 == 1
            )
            if (mutation_probability < 0.30 and index % 2 == 1) or stable_by_understanding:
                events.append(
                    {
                        "event_type": "semantic_stabilization",
                        "generation_index": generation_index,
                        "parent": parent["id"],
                        "feedback_input_id": feedback_id,
                        "explanation_quality": explanation_quality,
                        "mutation_probability": mutation_probability,
                    }
                )
                continue
            clause = clauses[index % len(clauses)]
            dimension = active_dimensions[index % len(active_dimensions)] if active_dimensions else {"dimension_id": "generated_seed_dimension", "source_token": "seed"}
            child = copy.deepcopy(parent)
            reflexive_trait = f"reflexive::{feedback_id}::{clause['clause_id']}::{dimension['source_token']}"
            child["id"] = f"{parent['id']}_v07_g{generation_index}_{stable_digest([reflexive_trait, str(index)])}"
            child["parents"] = [parent["id"]]
            child["version"] = int(parent.get("version", 0)) + 1
            child["status"] = "active"
            child["selection_events"] = []
            child.setdefault("mutation_history", [])
            child["mutation_history"].append(
                {
                    "generation_index": generation_index,
                    "event": "explanation_driven_mutation",
                    "source_law": law["law_id"],
                    "source_clause": clause["clause_id"],
                    "source_dimension": dimension["dimension_id"],
                    "source_regime": regime["regime_id"],
                    "feedback_input_id": feedback_id,
                    "explanation_quality": explanation_quality,
                    "mutation_probability": mutation_probability,
                    "self_model_id": self_model["self_model_id"],
                }
            )
            child["traits"].setdefault("generated_traits", [])
            child["traits"]["generated_traits"].append(reflexive_trait)
            child.setdefault("interpretation_history", [])
            child["interpretation_history"].append(
                {
                    "generation_index": generation_index,
                    "feedback_input_id": feedback_id,
                    "self_model_id": self_model["self_model_id"],
                    "semantic_coherence": feedback["semantic_coherence"],
                }
            )
            candidates.append(child)
            events.append(
                {
                    "event_type": "explanation_driven_mutation",
                    "generation_index": generation_index,
                    "parent": parent["id"],
                    "child": child["id"],
                    "source_law": law["law_id"],
                    "source_clause": clause["clause_id"],
                    "source_dimension": dimension["dimension_id"],
                    "feedback_input_id": feedback_id,
                    "explanation_quality": explanation_quality,
                    "semantic_coherence": feedback["semantic_coherence"],
                    "mutation_probability": mutation_probability,
                    "self_model_id": self_model["self_model_id"],
                }
            )
        return candidates, events

    def _mutation_probability(
        self,
        explanation_quality: float,
        feedback: dict[str, Any],
        self_model: dict[str, Any],
        index: int,
    ) -> float:
        poor_explanation_pressure = 1.0 - explanation_quality
        semantic_instability = 1.0 - feedback["semantic_coherence"]
        model_uncertainty = 1.0 - self_model["understanding_quality"]
        probability = 0.16 + poor_explanation_pressure * 0.42 + semantic_instability * 0.22 + model_uncertainty * 0.14
        probability += (index % 3) * 0.015
        return round(max(0.05, min(0.95, probability)), 6)
