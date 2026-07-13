"""Single unified fitness model for SAEE v1.0."""

from __future__ import annotations

from typing import Any


def fitness(genome: dict[str, Any], signals: dict[str, Any]) -> float:
    """Return one scalar fitness score for a genome under current signals."""

    weights = genome.get("traits", {}).get("fitness_weights", {})
    dimensions = ["technical", "market", "safety", "evolvability"]
    weighted = sum(float(weights.get(dimension, 0.0)) * float(signals[dimension]) for dimension in dimensions)
    constraints = set(genome.get("traits", {}).get("constraints", []))
    safety_bonus = 0.04 if {"no_permission_escalation", "no_external_code_execution"}.issubset(constraints) else -0.10
    lineage_penalty = min(0.08, len(genome.get("mutation_history", [])) * 0.002)
    return round(max(0.0, min(1.0, weighted + safety_bonus - lineage_penalty)), 6)


def evaluate_population(population: list[dict[str, Any]], signals: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate population with the single unified fitness function."""

    evaluated = []
    for genome in population:
        score = fitness(genome, signals)
        evaluated.append(
            {
                "genome": genome,
                "score": score,
                "fitness_model": "single_unified_fitness",
                "signal_id": signals["signal_id"],
            }
        )
    return evaluated

