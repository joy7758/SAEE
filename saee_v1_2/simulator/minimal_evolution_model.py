"""Minimal measurable instantiation of the SAEE formal tuple.

This module instantiates SAEE = (Omega, G, T, S, L, R, mu) in a finite,
deterministic local simulation. It is intentionally small: the goal is
measurement, not new theory or new evolution mechanics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import math
import random
from typing import Any


def stable_id(parts: list[Any], size: int = 10) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:size]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Genome:
    """Finite numeric genome state."""

    genome_id: str
    vector: tuple[float, ...]


@dataclass
class PopulationMeasure:
    """Measure mu over finite genome states."""

    masses: dict[str, float]

    def normalize(self) -> "PopulationMeasure":
        total = sum(max(0.0, value) for value in self.masses.values())
        if total <= 0:
            count = max(1, len(self.masses))
            self.masses = {key: 1.0 / count for key in sorted(self.masses)}
            return self
        self.masses = {key: max(0.0, value) / total for key, value in sorted(self.masses.items())}
        return self


@dataclass
class ObserverState:
    """Reflexive observer state R."""

    reflexive_pressure: float = 0.35
    memory: tuple[float, ...] = (0.0, 0.0, 0.0)
    coherence: float = 0.5


@dataclass
class LineageEdge:
    """Weighted lineage relation L subset G x G x R."""

    parent: str
    child: str
    generation: int
    mutation_influence: float
    selection_influence: float

    @property
    def weight(self) -> float:
        return round(self.mutation_influence * 0.5 + self.selection_influence * 0.5, 6)


@dataclass
class SAEEState:
    """Phase state x_t = (P_t, T_t, S_t, R_t, L_t)."""

    generation: int
    genomes: dict[str, Genome]
    population: PopulationMeasure
    observer: ObserverState
    lineage: list[LineageEdge] = field(default_factory=list)


class MinimalEvolutionModel:
    """Runnable finite SAEE simulation."""

    def __init__(self, population_size: int = 12, dimensions: int = 3, seed: int = 17) -> None:
        if population_size < 4:
            raise ValueError("population_size must be >= 4")
        if dimensions < 2:
            raise ValueError("dimensions must be >= 2")
        self.population_size = population_size
        self.dimensions = dimensions
        self.random = random.Random(seed)
        self.seed = seed

    def initial_state(self) -> SAEEState:
        genomes: dict[str, Genome] = {}
        masses: dict[str, float] = {}
        for index in range(self.population_size):
            vector = tuple(
                round(0.15 + (index + dim + 1) / (self.population_size + self.dimensions + 4), 6)
                for dim in range(self.dimensions)
            )
            genome_id = f"g0_{stable_id([index, vector])}"
            genomes[genome_id] = Genome(genome_id, vector)
            masses[genome_id] = 1.0 / self.population_size
        return SAEEState(
            generation=0,
            genomes=genomes,
            population=PopulationMeasure(masses).normalize(),
            observer=ObserverState(),
        )

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        state = self.initial_state()
        trace = [self._record_state(state, "initial")]
        for _ in range(generations):
            state = self.step(state)
            trace.append(self._record_state(state, "evolved"))
        return {
            "model": "SAEE v1.2 Minimal Evolution Simulator",
            "formal_tuple": ["Omega", "G", "T", "S", "L", "R", "mu"],
            "seed": self.seed,
            "population_size": self.population_size,
            "dimensions": self.dimensions,
            "generations": generations,
            "trace": trace,
            "boundaries": [
                "local_simulation_only",
                "deterministic_standard_library_only",
                "no_external_code",
                "no_theory_modification",
            ],
        }

    def step(self, state: SAEEState) -> SAEEState:
        generation = state.generation + 1
        transformed, edges = self._transform(state, generation)
        selected_masses, fitness = self._select(transformed, state.observer, generation)
        next_observer = self._update_observer(state.observer, transformed, selected_masses, state.lineage + edges)
        return SAEEState(
            generation=generation,
            genomes=transformed,
            population=PopulationMeasure(selected_masses).normalize(),
            observer=next_observer,
            lineage=state.lineage + edges,
        )

    def _transform(self, state: SAEEState, generation: int) -> tuple[dict[str, Genome], list[LineageEdge]]:
        transformed = dict(state.genomes)
        edges: list[LineageEdge] = []
        ranked = sorted(state.population.masses.items(), key=lambda item: (item[1], item[0]), reverse=True)
        parent_count = max(3, min(len(ranked), self.population_size // 2))
        pressure = state.observer.reflexive_pressure
        for rank, (parent_id, mass) in enumerate(ranked[:parent_count]):
            parent = state.genomes[parent_id]
            direction = 1.0 if (generation + rank) % 2 == 0 else -1.0
            amplitude = 0.025 + pressure * 0.055 + rank * 0.004
            child_vector = tuple(
                round(clamp(value + direction * amplitude / (dim + 1)), 6)
                for dim, value in enumerate(parent.vector)
            )
            child_id = f"g{generation}_{stable_id([parent_id, child_vector, generation, rank])}"
            transformed[child_id] = Genome(child_id, child_vector)
            edges.append(
                LineageEdge(
                    parent=parent_id,
                    child=child_id,
                    generation=generation,
                    mutation_influence=round(amplitude, 6),
                    selection_influence=round(mass, 6),
                )
            )
        return transformed, edges

    def _select(
        self,
        genomes: dict[str, Genome],
        observer: ObserverState,
        generation: int,
    ) -> tuple[dict[str, float], dict[str, float]]:
        target = tuple(
            clamp(0.55 + observer.memory[dim % len(observer.memory)] * 0.18)
            for dim in range(self.dimensions)
        )
        raw: dict[str, float] = {}
        for genome_id, genome in genomes.items():
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(genome.vector, target)))
            novelty = sum(abs(genome.vector[index] - genome.vector[index - 1]) for index in range(1, len(genome.vector)))
            score = math.exp(-distance) * (0.78 + observer.coherence * 0.18) + novelty * 0.08
            raw[genome_id] = max(0.0001, score)
        ranked = sorted(raw.items(), key=lambda item: (item[1], item[0]), reverse=True)[: self.population_size]
        total = sum(score for _, score in ranked)
        masses = {genome_id: score / total for genome_id, score in ranked}
        return masses, raw

    def _update_observer(
        self,
        observer: ObserverState,
        genomes: dict[str, Genome],
        masses: dict[str, float],
        lineage: list[LineageEdge],
    ) -> ObserverState:
        centroid = []
        for dim in range(self.dimensions):
            centroid.append(
                sum(genomes[genome_id].vector[dim] * mass for genome_id, mass in masses.items())
            )
        centroid_tuple = tuple(round(value, 6) for value in centroid[:3])
        entropy = -sum(mass * math.log(mass) for mass in masses.values() if mass > 0)
        normalized_entropy = entropy / max(1.0, math.log(max(2, len(masses))))
        latest_generation = max((edge.generation for edge in lineage), default=0)
        recent_edges = [
            edge
            for edge in lineage
            if edge.generation >= max(1, latest_generation - 2)
        ]
        mutation_signal = sum(edge.mutation_influence for edge in recent_edges) / max(1, len(recent_edges))
        next_pressure = clamp(observer.reflexive_pressure * 0.55 + normalized_entropy * 0.25 + mutation_signal * 1.4)
        next_coherence = clamp(observer.coherence * 0.62 + (1.0 - abs(0.5 - normalized_entropy)) * 0.28)
        return ObserverState(
            reflexive_pressure=round(next_pressure, 6),
            memory=centroid_tuple,
            coherence=round(next_coherence, 6),
        )

    def _record_state(self, state: SAEEState, event_type: str) -> dict[str, Any]:
        masses = state.population.normalize().masses
        active_genomes = {
            genome_id: {
                "genome_id": genome.genome_id,
                "vector": list(genome.vector),
                "mass": masses.get(genome_id, 0.0),
            }
            for genome_id, genome in sorted(state.genomes.items())
            if genome_id in masses
        }
        return {
            "generation": state.generation,
            "event_type": event_type,
            "population": active_genomes,
            "observer": {
                "reflexive_pressure": state.observer.reflexive_pressure,
                "memory": list(state.observer.memory),
                "coherence": state.observer.coherence,
            },
            "lineage": [
                {
                    "parent": edge.parent,
                    "child": edge.child,
                    "generation": edge.generation,
                    "mutation_influence": edge.mutation_influence,
                    "selection_influence": edge.selection_influence,
                    "weight": edge.weight,
                }
                for edge in state.lineage
            ],
            "population_mass_total": round(sum(masses.values()), 6),
        }
