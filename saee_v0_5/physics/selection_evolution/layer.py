"""Generate, mutate, and apply selection mechanisms."""

from __future__ import annotations

import copy
import hashlib
from typing import Any


def _digest(parts: list[str], size: int = 10) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:size]


class SelectionMechanismEvolutionLayer:
    """Treat selection mechanisms as generated evolving entities."""

    def __init__(self) -> None:
        self.current: dict[str, Any] | None = None
        self.mechanisms: list[dict[str, Any]] = []

    def evolve(
        self,
        law: dict[str, Any],
        generated_fitness: dict[str, Any],
        observation: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        parents = [self.current["mechanism_id"]] if self.current else []
        mutation_basis = [
            law["law_id"],
            generated_fitness["fitness_function_id"],
            observation["phase_signal"]["signature"],
            str(generation_index),
        ]
        digest = _digest(mutation_basis)
        novelty = observation["novelty"]["novelty_score"]
        collapse = observation["phase_signal"]["collapse_pressure"]
        spread = observation["population_metrics"]["score_spread_hint"]
        mechanism = {
            "mechanism_id": f"selection_g{generation_index:03d}_{digest}",
            "generation_index": generation_index,
            "parents": parents,
            "origin_law": law["law_id"],
            "origin_fitness_function": generated_fitness["fitness_function_id"],
            "mutation_record": {
                "basis": mutation_basis,
                "mutation_signature": digest,
                "is_reproduction": bool(parents),
            },
            "pressure_expression": {
                "survival_quantile": round(max(0.35, min(0.72, 0.50 + novelty * 0.12 - collapse * 0.10)), 6),
                "dormancy_band": round(max(0.08, min(0.25, 0.12 + spread * 0.20)), 6),
                "novelty_bias": round(novelty * 0.18, 6),
                "collapse_bias": round(collapse * 0.20, 6),
            },
        }
        self.current = mechanism
        self.mechanisms.append(mechanism)
        return mechanism

    def resolve(
        self,
        scored_population: list[dict[str, Any]],
        mechanism: dict[str, Any],
        observation: dict[str, Any],
    ) -> dict[str, Any]:
        annotated = [self._annotate(item, mechanism) for item in scored_population]
        ranked = sorted(annotated, key=lambda item: (item["selection_score"], item["genome"]["id"]), reverse=True)
        survival_count = max(3, int(len(ranked) * mechanism["pressure_expression"]["survival_quantile"]))
        dormant_count = min(3, max(1, int(len(ranked) * mechanism["pressure_expression"]["dormancy_band"])))
        survivors = ranked[:survival_count]
        dormant = ranked[survival_count : survival_count + dormant_count]
        extinct = ranked[survival_count + dormant_count :]
        decision = {
            "mechanism_id": mechanism["mechanism_id"],
            "survival_set": [self._mark(item, "survival", "active", observation, mechanism) for item in survivors],
            "dormant_set": [self._mark(item, "dormancy", "dormant", observation, mechanism) for item in dormant],
            "extinction_set": [self._mark(item, "extinction", "extinct", observation, mechanism) for item in extinct],
            "revival_set": [],
        }
        return decision

    def export(self) -> list[dict[str, Any]]:
        return list(self.mechanisms)

    def _annotate(self, item: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
        annotated = copy.deepcopy(item)
        score = float(annotated["generated_fitness"]["score"])
        novelty_bonus = mechanism["pressure_expression"]["novelty_bias"] * self._generated_trait_count(annotated["genome"])
        collapse_penalty = mechanism["pressure_expression"]["collapse_bias"] * self._unsafe_penalty(annotated["genome"])
        annotated["selection_score"] = round(max(0.0, min(1.0, score + novelty_bonus - collapse_penalty)), 6)
        return annotated

    def _mark(
        self,
        item: dict[str, Any],
        event: str,
        status: str,
        observation: dict[str, Any],
        mechanism: dict[str, Any],
    ) -> dict[str, Any]:
        genome = copy.deepcopy(item["genome"])
        genome["status"] = status
        genome["fitness"] = item["generated_fitness"]
        genome["selection_score"] = item["selection_score"]
        genome.setdefault("selection_events", [])
        genome["selection_events"].append(
            {
                "generation_index": observation["generation_index"],
                "event": event,
                "observation_id": observation["observation_id"],
                "mechanism_id": mechanism["mechanism_id"],
                "selection_score": item["selection_score"],
            }
        )
        return genome

    def _generated_trait_count(self, genome: dict[str, Any]) -> float:
        return min(1.0, len(genome.get("traits", {}).get("generated_traits", [])) * 0.12)

    def _unsafe_penalty(self, genome: dict[str, Any]) -> float:
        constraints = set(genome.get("traits", {}).get("constraints", []))
        return 0.0 if {"no_permission_escalation", "no_external_code_execution"}.issubset(constraints) else 1.0
