"""Shared deterministic baseline simulation helpers."""

from __future__ import annotations

import hashlib
import math
import random
from typing import Any


def _stable_id(parts: list[Any], size: int = 10) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:size]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _record(generation: int, vectors: dict[str, tuple[float, ...]], masses: dict[str, float], lineage: list[dict[str, Any]], pressure: float) -> dict[str, Any]:
    total = sum(masses.values()) or 1.0
    normalized = {key: value / total for key, value in masses.items()}
    return {
        "generation": generation,
        "population": {
            genome_id: {
                "genome_id": genome_id,
                "vector": list(vectors[genome_id]),
                "mass": normalized[genome_id],
            }
            for genome_id in sorted(normalized)
        },
        "observer": {
            "reflexive_pressure": pressure,
            "memory": [0.0, 0.0, 0.0],
            "coherence": 0.0,
        },
        "lineage": list(lineage),
    }


def run_baseline(kind: str, generations: int = 24, population_size: int = 12, dimensions: int = 3, seed: int = 29) -> dict[str, Any]:
    rng = random.Random(seed)
    vectors: dict[str, tuple[float, ...]] = {}
    masses: dict[str, float] = {}
    lineage: list[dict[str, Any]] = []
    for index in range(population_size):
        vector = tuple(round(0.2 + (index + dim) / (population_size + dimensions + 5), 6) for dim in range(dimensions))
        genome_id = f"{kind}_g0_{_stable_id([index, vector])}"
        vectors[genome_id] = vector
        masses[genome_id] = 1.0 / population_size
    trace = [_record(0, vectors, masses, lineage, pressure=0.0)]
    for generation in range(1, generations + 1):
        target = tuple(0.58 for _ in range(dimensions))
        scored = []
        for genome_id, vector in vectors.items():
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector, target)))
            if kind == "ga":
                score = math.exp(-distance)
            elif kind == "es":
                score = math.exp(-distance) + sum(vector) / (dimensions * 12.0)
            else:
                neighbor_signal = sum(abs(vector[i] - vector[i - 1]) for i in range(1, len(vector)))
                score = math.exp(-distance) * 0.8 + neighbor_signal * 0.2
            scored.append((genome_id, max(0.0001, score)))
        parents = sorted(scored, key=lambda item: (item[1], item[0]), reverse=True)[: max(3, population_size // 2)]
        next_vectors = {genome_id: vectors[genome_id] for genome_id, _ in parents}
        for rank, (parent_id, parent_score) in enumerate(parents):
            parent = vectors[parent_id]
            if kind == "ga":
                amplitude = 0.035 + rank * 0.003
            elif kind == "es":
                amplitude = 0.025 + (generation % 4) * 0.006
            else:
                amplitude = 0.03 + abs(0.5 - parent_score) * 0.02
            child = tuple(_clamp(value + ((-1) ** (rank + generation)) * amplitude / (dim + 1)) for dim, value in enumerate(parent))
            child_id = f"{kind}_g{generation}_{_stable_id([parent_id, child, generation, rank])}"
            next_vectors[child_id] = tuple(round(value, 6) for value in child)
            lineage.append(
                {
                    "parent": parent_id,
                    "child": child_id,
                    "generation": generation,
                    "mutation_influence": round(amplitude, 6),
                    "selection_influence": round(parent_score, 6),
                    "weight": round((amplitude + parent_score) / 2.0, 6),
                }
            )
        next_raw = {}
        for genome_id, vector in next_vectors.items():
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector, target)))
            if kind == "alife":
                neighbor_signal = sum(abs(vector[i] - vector[i - 1]) for i in range(1, len(vector)))
                next_raw[genome_id] = max(0.0001, math.exp(-distance) * 0.8 + neighbor_signal * 0.2)
            else:
                next_raw[genome_id] = max(0.0001, math.exp(-distance))
        selected = [
            genome_id
            for genome_id, _ in sorted(
                next_raw.items(),
                key=lambda item: (item[1], item[0]),
                reverse=True,
            )[:population_size]
        ]
        vectors = {genome_id: next_vectors[genome_id] for genome_id in selected}
        raw = {genome_id: next_raw[genome_id] for genome_id in vectors}
        total = sum(raw.values())
        masses = {genome_id: value / total for genome_id, value in raw.items()}
        trace.append(_record(generation, vectors, masses, lineage, pressure=0.0))
    return {
        "baseline": kind,
        "generations": generations,
        "population_size": population_size,
        "dimensions": dimensions,
        "trace": trace,
    }
