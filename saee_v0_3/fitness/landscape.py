"""Dynamic multi-objective fitness landscape for SAEE v0.3."""

from __future__ import annotations

from collections import Counter
from typing import Any


class V03FitnessLandscape:
    """Score genomes with rule-aware dynamic fitness."""

    def score(
        self,
        population: list[dict[str, Any]],
        environment: dict[str, Any],
        rule_genome: dict[str, Any],
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
        pressure = len(population) / max(1, environment["carrying_capacity"])
        return [
            {
                "genome": genome,
                "fitness": self._score_genome(genome, environment, rule_genome, mutation_counts, parent_counts, pressure, len(population)),
            }
            for genome in population
        ]

    def _score_genome(
        self,
        genome: dict[str, Any],
        environment: dict[str, Any],
        rule_genome: dict[str, Any],
        mutation_counts: Counter[str],
        parent_counts: Counter[str],
        population_pressure: float,
        population_size: int,
    ) -> dict[str, Any]:
        vector = environment["pressure_vector"]
        scope = set(genome["traits"].get("mutation_scope", []))
        constraints = set(genome["traits"].get("constraints", []))
        parent_key = genome.get("parents", ["founder"])[0] if genome.get("parents") else "founder"
        lineage_competition = parent_counts[parent_key] / max(1, population_size)
        rarity = self._rarity(scope, mutation_counts)
        safe = {"no_permission_escalation", "no_external_code_execution"}.issubset(constraints)
        components = {
            "technical": self._bounded(0.30 + vector["technical"] * 0.35 + ("workflow_reorder" in " ".join(scope)) * 0.08),
            "market": self._bounded(0.28 + vector["market"] * 0.42 + ("niche_shift" in " ".join(scope)) * 0.10),
            "safety": self._bounded(0.20 + vector["safety"] * 0.32 + safe * 0.25 + ("rollback_bias" in " ".join(scope)) * 0.05),
            "cost": self._bounded(1.0 - len(scope) * 0.03 - max(0.0, population_pressure - 1.0) * 0.08),
            "novelty": self._bounded(0.22 + vector["novelty"] * 0.32 + rarity * 0.25),
            "evolvability": self._bounded(0.26 + vector["evolvability"] * 0.35 + min(0.2, len(genome.get("mutation_history", [])) * 0.02)),
        }
        weights = rule_genome["fitness_weights"]
        total_weight = sum(weights[key] for key in components)
        weighted = sum(components[key] * weights[key] for key in components) / total_weight
        total = self._bounded(weighted - min(0.12, lineage_competition * 0.1))
        return {
            "generation_index": environment["generation_index"],
            "environment_id": environment["environment_id"],
            "rule_genome_id": rule_genome["id"],
            "population_pressure": round(population_pressure, 4),
            "lineage_competition": round(lineage_competition, 4),
            "components": {key: round(value, 6) for key, value in components.items()},
            "weights": dict(weights),
            "total": round(total, 6),
        }

    def _rarity(self, scope: set[str], counts: Counter[str]) -> float:
        if not scope:
            return 0.0
        return sum(1.0 / max(1, counts[mutation]) for mutation in scope) / len(scope)

    def _bounded(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

