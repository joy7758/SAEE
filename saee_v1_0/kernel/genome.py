"""Genome helpers for the SAEE v1.0 stable runtime."""

from __future__ import annotations

import copy
import hashlib
from typing import Any


def stable_digest(parts: list[str], size: int = 8) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:size]


def seed_population(seed_genome: dict[str, Any], population_size: int) -> list[dict[str, Any]]:
    """Create one simple population pool from the seed genome."""

    population = []
    for index in range(population_size):
        genome = copy.deepcopy(seed_genome)
        genome["id"] = seed_genome["id"] if index == 0 else f"{seed_genome['id']}_p{index}"
        genome["version"] = int(seed_genome.get("version", 0))
        genome["parents"] = []
        genome["status"] = "active"
        genome.setdefault("mutation_history", [])
        if index:
            genome["mutation_history"].append(
                {
                    "event": "initial_population_variant",
                    "variant_index": index,
                    "mutation_scope": genome.get("traits", {}).get("mutation_scope", []),
                }
            )
            genome["traits"]["fitness_weights"] = _shift_weights(
                genome["traits"]["fitness_weights"],
                index,
            )
        population.append(genome)
    return population


def mutate_population(
    population: list[dict[str, Any]],
    signals: dict[str, Any],
    generation_index: int,
) -> list[dict[str, Any]]:
    """Create one deterministic child per active genome."""

    children = []
    for index, parent in enumerate(population):
        child = copy.deepcopy(parent)
        digest = stable_digest([parent["id"], signals["signal_id"], str(generation_index), str(index)])
        child["id"] = f"{parent['id']}_g{generation_index}_{digest}"
        child["parents"] = [parent["id"]]
        child["version"] = int(parent.get("version", 0)) + 1
        child["status"] = "active"
        child["traits"]["fitness_weights"] = _signal_shift_weights(
            child["traits"]["fitness_weights"],
            signals,
            index,
        )
        child.setdefault("mutation_history", [])
        child["mutation_history"].append(
            {
                "event": "stable_runtime_mutation",
                "generation_index": generation_index,
                "source_signal": signals["signal_id"],
                "parent": parent["id"],
                "child": child["id"],
                "mutation_model": "deterministic_weight_shift",
            }
        )
        children.append(child)
    return children


def _shift_weights(weights: dict[str, float], index: int) -> dict[str, float]:
    shifted = dict(weights)
    keys = sorted(shifted)
    key = keys[index % len(keys)]
    shifted[key] = min(1.0, shifted[key] + 0.02)
    return _normalize(shifted)


def _signal_shift_weights(weights: dict[str, float], signals: dict[str, Any], index: int) -> dict[str, float]:
    shifted = dict(weights)
    dimensions = ["technical", "market", "safety", "evolvability"]
    strongest = max(dimensions, key=lambda item: (float(signals[item]), item))
    weakest = min(dimensions, key=lambda item: (float(signals[item]), item))
    shifted[strongest] = min(1.0, shifted.get(strongest, 0.0) + 0.03 + index * 0.002)
    shifted[weakest] = max(0.0, shifted.get(weakest, 0.0) - 0.01)
    return _normalize(shifted)


def _normalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, float(value)) for value in weights.values()) or 1.0
    return {
        key: round(max(0.0, float(value)) / total, 6)
        for key, value in sorted(weights.items())
    }

