"""Dynamic fitness landscape for population ecology scoring."""

from __future__ import annotations

from collections import Counter
from typing import Any


class DynamicFitnessLandscape:
    """Score genomes against time, environment, population pressure, and lineage competition."""

    def score_population(
        self,
        population: list[dict[str, Any]],
        generation_id: int,
        environment_state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        mutation_counts = Counter(
            mutation
            for genome in population
            for mutation in genome["traits"].get("mutation_scope", [])
        )
        parent_counts = Counter(
            genome.get("parents", ["founder"])[0] if genome.get("parents") else "founder"
            for genome in population
        )
        population_pressure = round(len(population) / environment_state["carrying_capacity"], 4)

        return [
            {
                "genome": genome,
                "fitness": self.score_genome(
                    genome,
                    generation_id,
                    environment_state,
                    population_pressure,
                    mutation_counts,
                    parent_counts,
                    len(population),
                ),
            }
            for genome in population
        ]

    def score_genome(
        self,
        genome: dict[str, Any],
        generation_id: int,
        environment_state: dict[str, Any],
        population_pressure: float,
        mutation_counts: Counter[str],
        parent_counts: Counter[str],
        population_size: int,
    ) -> dict[str, Any]:
        pressure = environment_state["pressure_vector"]
        scope = set(genome["traits"].get("mutation_scope", []))
        constraints = set(genome["traits"].get("constraints", []))
        parent_key = genome.get("parents", ["founder"])[0] if genome.get("parents") else "founder"
        lineage_competition = parent_counts[parent_key] / max(1, population_size)
        novelty_rarity = self._rarity(scope, mutation_counts)

        components = {
            "technical": self._bounded(0.35 + pressure["technical"] * 0.35 + ("workflow_reorder" in scope) * 0.10),
            "market": self._bounded(0.30 + pressure["market"] * 0.45 + ("niche_shift" in scope) * 0.10),
            "safety": self._bounded(
                0.25
                + pressure["safety"] * 0.25
                + ("safety_constraint_tuning" in scope) * 0.15
                + ({
                    "no_permission_escalation",
                    "no_external_code_execution",
                }.issubset(constraints))
                * 0.25
            ),
            "cost": self._bounded(1.0 - (len(scope) * 0.035) - max(0.0, population_pressure - 1.0) * 0.08),
            "novelty": self._bounded(0.25 + pressure["novelty"] * 0.35 + novelty_rarity * 0.25),
            "evolvability": self._bounded(
                0.30
                + pressure["evolvability"] * 0.35
                + min(0.20, len(genome.get("mutation_history", [])) * 0.025)
                + ("cross_lineage_recombination" in scope) * 0.10
            ),
        }

        weights = {
            "technical": 0.25,
            "market": 0.20,
            "safety": 0.20,
            "cost": 0.10,
            "novelty": 0.10,
            "evolvability": 0.15,
        }
        weights.update({key: float(value) for key, value in genome["traits"].get("fitness_weights", {}).items()})
        total_weight = sum(weights.get(key, 0.0) for key in components)
        weighted_total = sum(components[key] * weights.get(key, 0.0) for key in components) / total_weight
        competition_penalty = min(0.12, lineage_competition * 0.10)
        time_shift = 0.01 * (generation_id % 5)
        total = self._bounded(weighted_total - competition_penalty + time_shift)

        return {
            "generation_id": generation_id,
            "environment_id": environment_state["environment_id"],
            "population_pressure": population_pressure,
            "lineage_competition": round(lineage_competition, 4),
            "components": {key: round(value, 6) for key, value in components.items()},
            "total": round(total, 6),
        }

    def _rarity(self, scope: set[str], mutation_counts: Counter[str]) -> float:
        if not scope:
            return 0.0
        return sum(1.0 / max(1, mutation_counts[mutation]) for mutation in scope) / len(scope)

    def _bounded(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

