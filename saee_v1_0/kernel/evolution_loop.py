"""Single stable evolution loop for SAEE v1.0."""

from __future__ import annotations

import copy
from typing import Any

from saee_v1_0.kernel.fitness import evaluate_population
from saee_v1_0.kernel.genome import mutate_population, seed_population
from saee_v1_0.kernel.lineage import LineageDAG
from saee_v1_0.kernel.selection import select_population


class EvolutionLoopKernel:
    """Run Sense -> Mutate -> Evaluate -> Select -> Lineage -> Update."""

    LOOP = ["Sense", "Mutate", "Evaluate", "Select", "Lineage", "Update"]

    def __init__(self, seed_genome: dict[str, Any], population_size: int = 8) -> None:
        if population_size < 2:
            raise ValueError("population_size must be >= 2")
        self.population_size = population_size
        self.population = seed_population(seed_genome, population_size)
        self.lineage = LineageDAG()
        self.generation_index = 0
        self.generation_log: list[dict[str, Any]] = []
        self.fitness_scores: list[dict[str, Any]] = []
        self.lineage.record_population(self.population, self.generation_index)

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            self.step()
        return self.record()

    def step(self) -> dict[str, Any]:
        self.generation_index += 1
        signals = self._sense(self.generation_index)
        children = mutate_population(self.population, signals, self.generation_index)
        candidates = copy.deepcopy(self.population) + children
        evaluated = evaluate_population(candidates, signals)
        selected = select_population(evaluated, self.population_size, self.generation_index)
        self.population = selected["survivors"]
        self.lineage.record_population(self.population + selected["rejected"], self.generation_index)
        scores = [
            {
                "generation_index": self.generation_index,
                "genome_id": item["genome"]["id"],
                "score": item["score"],
                "fitness_model": item["fitness_model"],
                "signal_id": item["signal_id"],
            }
            for item in evaluated
        ]
        self.fitness_scores.extend(scores)
        generation_record = {
            "generation_id": f"v1-generation-{self.generation_index:04d}",
            "generation_index": self.generation_index,
            "loop": list(self.LOOP),
            "signals": signals,
            "candidate_count": len(candidates),
            "survivor_count": len(selected["survivors"]),
            "rejected_count": len(selected["rejected"]),
            "population": self.population,
            "selection_model": selected["selection_model"],
        }
        self.generation_log.append(generation_record)
        return generation_record

    def record(self) -> dict[str, Any]:
        lineage_graph = self.lineage.export()
        return {
            "kernel": "SAEE v1.0 Stable Evolutionary Runtime",
            "version": "1.0.0",
            "status": "local_v1_0_stable_evolutionary_runtime",
            "core_loop": list(self.LOOP),
            "loop_count": 1,
            "population_model": "single_population_pool",
            "fitness_model": "single_unified_fitness",
            "lineage_model": "single_lineage_dag",
            "generation_count": self.generation_index,
            "population": self.population,
            "generation_log": self.generation_log,
            "fitness_scores": self.fitness_scores,
            "lineage_dag": lineage_graph,
            "stability_summary": {
                "one_loop": True,
                "population_size": len(self.population),
                "single_population_pool": True,
                "single_unified_fitness": True,
                "single_lineage_graph": lineage_graph["graph_type"] == "lineage_dag",
                "runtime_layer_count": 1,
                "forbidden_runtime_layers": [],
                "phase_theory_in_runtime": False,
                "physics_abstraction_in_runtime": False,
                "observer_epistemic_semantic_core": False,
            },
            "boundaries": [
                "single_core_loop_only",
                "population_based_evolution",
                "single_population_pool",
                "single_unified_fitness",
                "single_lineage_dag",
                "no_phase_theory_runtime",
                "no_physics_abstraction_runtime",
                "no_observer_epistemic_semantic_core",
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_external_code_as_genome",
                "local_reproducible_runtime_only",
            ],
        }

    def _sense(self, generation_index: int) -> dict[str, Any]:
        return {
            "signal_id": f"v1_signal_{generation_index:04d}",
            "generation_index": generation_index,
            "signal_model": "local_deterministic_abstract_signals",
            "technical": round(0.52 + (generation_index % 5) * 0.035, 6),
            "market": round(0.48 + (generation_index % 4) * 0.03, 6),
            "safety": round(0.70 - (generation_index % 3) * 0.025, 6),
            "evolvability": round(0.50 + (generation_index % 6) * 0.025, 6),
        }

