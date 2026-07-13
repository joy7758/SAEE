"""SAEE v0.4 phase-transition runtime.

Closed local loop:
abstract sensing -> phase detection -> regime switch -> evolution-space mutation
-> mutation/recombination -> fitness geometry projection -> selection topology
-> lineage update -> population reconfiguration.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from saee_v0_4.ecological_regimes import MetaRegimeSwitchSystem
from saee_v0_4.evolution_space import EvolutionSpace
from saee_v0_4.fitness_geometry import FitnessGeometry
from saee_v0_4.lineage_graph import V04LineageGraph
from saee_v0_4.mutation_space import MutationOperatorRegistry
from saee_v0_4.phase_transition import EcologicalPhaseTransitionDetector
from saee_v0_4.population import PopulationPoolV04
from saee_v0_4.selection_topology import SelectionTopologyEngine


class SAEEV04Runtime:
    """Local reproducible phase-transition evolution-space kernel."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.population_pool = PopulationPoolV04()
        self.evolution_space = EvolutionSpace()
        self.mutation_space = MutationOperatorRegistry()
        self.fitness_geometry = FitnessGeometry()
        self.selection_topology = SelectionTopologyEngine()
        self.phase_detector = EcologicalPhaseTransitionDetector()
        self.regime_switch = MetaRegimeSwitchSystem()
        self.lineage = V04LineageGraph()
        self.population = self.population_pool.initialize(seed_genome, size=initial_population_size)
        self.cycles: list[dict[str, Any]] = []
        self.generation_index = 0

        seed_phase = {
            "generation_index": 0,
            "phase_type": "seed_stability",
            "metrics": {
                "population_count": len(self.population),
                "niche_count": 1,
                "score_average": 0.0,
                "score_dispersion": 0.0,
                "dominant_dimension": "seed",
            },
            "previous_phase_type": None,
            "is_phase_shift": False,
        }
        seed_regime = {
            "generation_index": 0,
            "phase_type": "seed_stability",
            "regime": "optimization",
            "reason": "seed_evolution_space",
        }
        self.lineage.record_population(self.population, self.generation_index)
        self.lineage.record_space(
            self.evolution_space.snapshot(),
            {"generation_index": 0, "phase_type": "seed_stability", "regime": "optimization", "changes": ["seed_space"]},
            seed_phase,
            seed_regime,
        )

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            self.step()
        return self._record()

    def step(self) -> dict[str, Any]:
        self.generation_index += 1
        environment = self._abstract_environment(self.generation_index)
        current_space = self.evolution_space.snapshot()
        current_projection = self.fitness_geometry.project(self.population, environment, current_space)
        phase = self.phase_detector.detect(current_projection, environment, self.generation_index)
        regime_event = self.regime_switch.resolve(phase, self.generation_index)
        space_mutation = self.evolution_space.mutate(phase, regime_event["regime"], self.generation_index)
        mutated_space = self.evolution_space.snapshot()

        candidates, mutation_events = self.mutation_space.mutate_population(
            self.population,
            mutated_space,
            self.generation_index,
        )
        active_operators = self.mutation_space.active_operators(mutated_space)
        candidate_projection = self.fitness_geometry.project(candidates, environment, mutated_space)
        decision = self.selection_topology.resolve(
            candidate_projection,
            environment,
            mutated_space,
            self.population,
        )

        self.lineage.record_mutations(mutation_events)
        self.lineage.record_selection(decision, self.generation_index)
        self.population = self.population_pool.reconfigure(decision)
        self.lineage.record_population(self.population, self.generation_index)
        self.lineage.record_space(mutated_space, space_mutation, phase, regime_event)

        cycle = {
            "generation_id": f"v04-generation-{self.generation_index:03d}",
            "environment_state": environment,
            "phase_transition": phase,
            "regime_switch": regime_event,
            "evolution_space_mutation": space_mutation,
            "evolution_space": {
                "space_id": mutated_space["space_id"],
                "geometry_type": mutated_space["geometry_type"],
                "selection_topology": mutated_space["selection_topology"],
                "mutation_operator_mode": mutated_space["mutation_operator_mode"],
                "active_dimensions": [
                    name
                    for name, spec in mutated_space["dimensions"].items()
                    if spec.get("active", True)
                ],
            },
            "mutation_space": {
                "active_operators": active_operators,
                "events": mutation_events,
            },
            "fitness_geometry": {
                "geometry_type": mutated_space["geometry_type"],
                "sample": [
                    {
                        "genome_id": item["genome"]["id"],
                        "niche": item["fitness_geometry"]["niche"],
                        "geometry_score": item["fitness_geometry"]["geometry_score"],
                        "active_dimensions": item["fitness_geometry"]["active_dimensions"],
                    }
                    for item in candidate_projection[:8]
                ],
            },
            "selection_topology": {
                "topology_type": decision["topology_type"],
                "survival_set": [genome["id"] for genome in decision["survival_set"]],
                "dormant_set": [genome["id"] for genome in decision["dormant_set"]],
                "extinction_set": [genome["id"] for genome in decision["extinction_set"]],
                "revival_set": [genome["id"] for genome in decision["revival_set"]],
                "niche_count": len(decision["niche_map"]),
            },
            "population_size": len(self.population),
        }
        self.cycles.append(cycle)
        return cycle

    def _abstract_environment(self, generation_index: int) -> dict[str, Any]:
        pattern = generation_index % 4
        if pattern == 1:
            vector = {
                "technical": 0.45,
                "market": 0.68,
                "safety": 0.40,
                "cost": 0.22,
                "novelty": 0.76,
                "evolvability": 0.72,
                "coordination": 0.50,
            }
            signals = [
                {"source": "github", "signal": "repo_growth", "intensity": 0.58},
                {"source": "paper", "signal": "framework_trend", "intensity": 0.74},
                {"source": "news", "signal": "new_niche_pressure", "intensity": 0.69},
            ]
        elif pattern == 2:
            vector = {
                "technical": 0.80,
                "market": 0.32,
                "safety": 0.62,
                "cost": 0.35,
                "novelty": 0.25,
                "evolvability": 0.42,
                "coordination": 0.46,
            }
            signals = [
                {"source": "github", "signal": "pr_pattern", "intensity": 0.70},
                {"source": "history", "signal": "past_architecture_success", "intensity": 0.57},
            ]
        elif pattern == 3:
            vector = {
                "technical": 0.54,
                "market": 0.74,
                "safety": 0.48,
                "cost": 0.28,
                "novelty": 0.66,
                "evolvability": 0.63,
                "coordination": 0.58,
            }
            signals = [
                {"source": "news", "signal": "market_shift", "intensity": 0.76},
                {"source": "paper", "signal": "research_branching", "intensity": 0.65},
            ]
        else:
            vector = {
                "technical": 0.42,
                "market": 0.30,
                "safety": 0.84,
                "cost": 0.64,
                "novelty": 0.20,
                "evolvability": 0.34,
                "coordination": 0.52,
            }
            signals = [
                {"source": "news", "signal": "regulation_shift", "intensity": 0.82},
                {"source": "history", "signal": "failed_system_pattern", "intensity": 0.78},
            ]
        dominant_dimension = max(vector, key=lambda name: vector[name])
        return {
            "environment_id": f"abstract_environment_v04_g{generation_index:03d}",
            "generation_index": generation_index,
            "signal_model": "abstract_signal_objects_only",
            "signal_objects": signals,
            "pressure_vector": vector,
            "dominant_dimension": dominant_dimension,
            "carrying_capacity": 6 + (generation_index % 2),
            "dormancy_limit": 3,
            "dormancy_threshold": 0.35,
            "revival_pressure": pattern == 0,
        }

    def _record(self) -> dict[str, Any]:
        phase_counts = Counter(cycle["phase_transition"]["phase_type"] for cycle in self.cycles)
        regime_counts = Counter(cycle["regime_switch"]["regime"] for cycle in self.cycles)
        topology_counts = Counter(cycle["selection_topology"]["topology_type"] for cycle in self.cycles)
        operator_modes = Counter(cycle["evolution_space"]["mutation_operator_mode"] for cycle in self.cycles)
        return {
            "kernel": "SAEE v0.4 Phase Transition Evolution Space Kernel",
            "version": "0.4.0",
            "status": "local_v0_4_phase_transition",
            "generation_id": f"v04-generation-{self.generation_index:03d}",
            "population": self.population,
            "evolution_space": self.evolution_space.snapshot(),
            "lineage_graph": self.lineage.export(),
            "cycles": self.cycles,
            "phase_transition_summary": {
                "phase_counts": dict(sorted(phase_counts.items())),
                "regime_counts": dict(sorted(regime_counts.items())),
                "selection_topology_counts": dict(sorted(topology_counts.items())),
                "mutation_operator_mode_counts": dict(sorted(operator_modes.items())),
                "phase_shift_count": sum(1 for cycle in self.cycles if cycle["phase_transition"]["is_phase_shift"]),
            },
            "regime_history": self.regime_switch.export(),
            "boundaries": [
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_external_code_as_genome",
                "no_publication_claim",
                "not_production_runtime",
                "not_unbounded_self_modification",
                "local_reproducible_simulation_only",
            ],
        }


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "run_record.json": record,
        "population.json": record["population"],
        "lineage_graph.json": record["lineage_graph"],
        "evolution_space.json": record["evolution_space"],
        "phase_transition_summary.json": record["phase_transition_summary"],
        "regime_switch_log.json": record["regime_history"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
