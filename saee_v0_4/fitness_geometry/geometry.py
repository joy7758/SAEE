"""Dynamic fitness geometry for SAEE v0.4."""

from __future__ import annotations

from collections import Counter
from typing import Any


class FitnessGeometry:
    """Evaluate population positions in mutable fitness geometry."""

    def project(
        self,
        population: list[dict[str, Any]],
        environment: dict[str, Any],
        evolution_space: dict[str, Any],
    ) -> list[dict[str, Any]]:
        active_dimensions = [
            name
            for name, spec in evolution_space["dimensions"].items()
            if spec.get("active", True)
        ]
        mutation_counts = Counter(
            mutation
            for genome in population
            for mutation in genome["traits"].get("mutation_scope", [])
        )
        parent_counts = Counter(
            genome.get("parents", ["founder"])[0] if genome.get("parents") else "founder"
            for genome in population
        )
        projections = []
        for genome in population:
            coordinates = self._coordinates(genome, environment, active_dimensions, mutation_counts)
            lineage_competition = parent_counts[genome.get("parents", ["founder"])[0] if genome.get("parents") else "founder"] / max(1, len(population))
            geometry_score = self._geometry_score(coordinates, evolution_space, lineage_competition)
            niche = self._niche(coordinates, genome)
            projections.append(
                {
                    "genome": genome,
                    "fitness_geometry": {
                        "geometry_type": evolution_space["geometry_type"],
                        "active_dimensions": active_dimensions,
                        "coordinates": coordinates,
                        "niche": niche,
                        "lineage_competition": round(lineage_competition, 4),
                        "geometry_score": round(geometry_score, 6),
                    },
                }
            )
        return projections

    def _coordinates(
        self,
        genome: dict[str, Any],
        environment: dict[str, Any],
        dimensions: list[str],
        mutation_counts: Counter[str],
    ) -> dict[str, float]:
        vector = environment["pressure_vector"]
        scope = set(genome["traits"].get("mutation_scope", []))
        constraints = set(genome["traits"].get("constraints", []))
        safe = {"no_permission_escalation", "no_external_code_execution"}.issubset(constraints)
        base = {
            "technical": 0.30 + vector.get("technical", 0.0) * 0.35 + ("workflow_reorder" in " ".join(scope)) * 0.08,
            "market": 0.28 + vector.get("market", 0.0) * 0.35 + ("niche" in " ".join(scope)) * 0.10,
            "safety": 0.25 + vector.get("safety", 0.0) * 0.30 + safe * 0.25,
            "cost": 0.95 - len(scope) * 0.025,
            "novelty": 0.25 + vector.get("novelty", 0.0) * 0.35 + self._rarity(scope, mutation_counts) * 0.25,
            "evolvability": 0.25 + vector.get("evolvability", 0.0) * 0.35 + min(0.25, len(genome.get("mutation_history", [])) * 0.025),
            "niche_diversity": 0.20 + len(set(genome["traits"].get("mutation_scope", []))) * 0.04,
            "coordination": 0.25 + vector.get("coordination", 0.0) * 0.35 + ("coordination" in " ".join(scope)) * 0.12,
        }
        return {dimension: round(max(0.0, min(1.0, base.get(dimension, 0.3))), 6) for dimension in dimensions}

    def _geometry_score(
        self,
        coordinates: dict[str, float],
        evolution_space: dict[str, Any],
        lineage_competition: float,
    ) -> float:
        weights = {
            name: spec["weight"]
            for name, spec in evolution_space["dimensions"].items()
            if spec.get("active", True) and name in coordinates
        }
        total_weight = sum(weights.values()) or 1.0
        weighted = sum(coordinates[name] * weights[name] for name in coordinates) / total_weight
        geometry = evolution_space["geometry_type"]
        if geometry == "expanding_simplex":
            return min(1.0, weighted + coordinates.get("novelty", 0.0) * 0.08)
        if geometry == "multi_niche_manifold":
            return min(1.0, weighted + coordinates.get("niche_diversity", 0.0) * 0.06)
        if geometry == "stability_basin":
            return max(0.0, weighted + coordinates.get("safety", 0.0) * 0.08 - lineage_competition * 0.08)
        return max(0.0, weighted - lineage_competition * 0.06)

    def _niche(self, coordinates: dict[str, float], genome: dict[str, Any]) -> str:
        if not coordinates:
            return "undefined"
        scope_blob = " ".join(genome["traits"].get("mutation_scope", []))
        anchor = None
        if "niche_split" in scope_blob or "cross_niche_bridge" in scope_blob:
            anchor = "niche_diversity"
        elif "coordination" in scope_blob:
            anchor = "coordination"
        elif "safety" in scope_blob or "threshold" in scope_blob or "stability" in scope_blob:
            anchor = "safety"
        elif "workflow" in scope_blob or "technical" in scope_blob:
            anchor = "technical"
        elif "novel_operator" in scope_blob or "evolvability_probe" in scope_blob:
            anchor = "novelty"
        top = sorted(coordinates.items(), key=lambda item: (item[1], item[0]), reverse=True)[:2]
        if anchor and anchor in coordinates:
            secondary = next((name for name, _value in top if name != anchor), top[0][0])
            return f"{anchor}+{secondary}"
        return "+".join(name for name, _value in top)

    def _rarity(self, scope: set[str], counts: Counter[str]) -> float:
        if not scope:
            return 0.0
        return sum(1.0 / max(1, counts[item]) for item in scope) / len(scope)
