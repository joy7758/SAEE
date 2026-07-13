"""SAEE v0.7 reflexive evolution kernel.

Agent-readable loop:
Meaning feedback -> Reflexive Mutation Engine -> Epistemic Fitness Layer
-> Semantic Selection Engine -> Observer-in-the-Loop System
-> Self-model update -> Explanation-influenced lineage.

v0.7 makes explanation causal input to evolution. It remains local-only and
uses v0.5 generated physics components without external execution.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from saee_v0_5.runtime.physics_loop import OpenEndedPhysicsLoop
from saee_v0_7.cognition.interpretation_pressure_engine import InterpretationPressureEngine
from saee_v0_7.cognition.meaning_feedback_loop import MeaningFeedbackLoop
from saee_v0_7.lineage.explanation_influenced_dag import ExplanationInfluencedDAG
from saee_v0_7.reflexive_core.epistemic_fitness import EpistemicFitnessLayer
from saee_v0_7.reflexive_core.observer_loop import ObserverInTheLoopSystem
from saee_v0_7.reflexive_core.reflexive_mutation_engine import ReflexiveMutationEngine
from saee_v0_7.reflexive_core.semantic_selection import SemanticSelectionEngine
from saee_v0_7.self_model.evolution_self_model import EvolutionSelfModel
from saee_v0_7.self_model.recursive_understanding_graph import RecursiveUnderstandingGraph


class ReflexiveEvolutionKernel:
    """Run explanation-influenced evolution."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.physics = OpenEndedPhysicsLoop(seed_genome, initial_population_size)
        self.reflexive_mutation = ReflexiveMutationEngine()
        self.epistemic_fitness = EpistemicFitnessLayer()
        self.semantic_selection = SemanticSelectionEngine()
        self.observer_loop = ObserverInTheLoopSystem(seed_genome, initial_population_size)
        self.meaning_feedback = MeaningFeedbackLoop()
        self.interpretation_pressure = InterpretationPressureEngine()
        self.self_model = EvolutionSelfModel()
        self.understanding_graph = RecursiveUnderstandingGraph()
        self.lineage = ExplanationInfluencedDAG()
        self.feedback = self.meaning_feedback.seed()
        self.cycles: list[dict[str, Any]] = []
        self.reflexive_mutation_events: list[dict[str, Any]] = []
        self.semantic_selection_records: list[dict[str, Any]] = []
        self.epistemic_records: list[dict[str, Any]] = []

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            self.step()
        return self.record()

    def step(self) -> dict[str, Any]:
        self.physics.generation_index += 1
        generation_index = self.physics.generation_index
        previous_self_model = self.self_model.snapshot()
        pressure = self.interpretation_pressure.compute(self.feedback, previous_self_model, generation_index)

        environment = self.physics._abstract_environment(generation_index)
        novelty = self.physics.novelty.detect(self.physics.population, environment, generation_index)
        observation = self.physics._observe(environment, novelty)
        dimension_state = self.physics.dimensions.update(observation, generation_index)
        law = self.physics.law_generator.generate(observation, dimension_state["dimensions"], generation_index)
        phase = self.physics.phase_engine.detect(observation, dimension_state["dimensions"], generation_index)
        regime = self.physics.regime_constructor.construct(
            law,
            dimension_state["dimensions"],
            phase,
            observation,
            generation_index,
        )
        generated_fitness = self.physics.fitness_engine.generate(
            law,
            dimension_state["dimensions"],
            observation,
            generation_index,
        )

        candidates, mutation_events = self.reflexive_mutation.generate(
            self.physics.population,
            law,
            dimension_state["dimensions"],
            regime,
            self.feedback,
            previous_self_model,
            generation_index,
        )
        base_scored = self.physics.fitness_engine.score(candidates, generated_fitness)
        epistemic_scored = self.epistemic_fitness.score(base_scored, self.feedback, previous_self_model)
        decision = self.semantic_selection.resolve(
            epistemic_scored,
            self.feedback,
            previous_self_model,
            generation_index,
        )
        self.physics.population = self._reconfigure_population(decision)

        selection_mechanism = {
            "mechanism_id": decision["mechanism_id"],
            "generation_index": generation_index,
            "parents": [self.semantic_selection_records[-1]["mechanism_id"]] if self.semantic_selection_records else [],
            "origin_law": law["law_id"],
            "origin_fitness_function": generated_fitness["fitness_function_id"],
            "mutation_record": {
                "feedback_input_id": self.feedback["feedback_id"],
                "self_model_id": previous_self_model["self_model_id"],
                "semantic_selection": True,
            },
            "pressure_expression": decision["semantic_selection_pressure"],
        }
        cycle = {
            "generation_id": f"v07-generation-{generation_index:03d}",
            "generation_index": generation_index,
            "environment_state": environment,
            "observation": observation,
            "dimension_state": dimension_state,
            "generated_evolution_law": law,
            "phase_emergence": phase,
            "constructed_regime": regime,
            "generated_fitness_function": generated_fitness,
            "selection_mechanism": selection_mechanism,
            "reflexive_feedback_input": copy.deepcopy(self.feedback),
            "interpretation_pressure": pressure,
            "self_model_input": previous_self_model,
            "variation_events": [event for event in mutation_events if "child" in event],
            "reflexive_mutation_events": mutation_events,
            "epistemic_fitness": [
                {
                    "genome_id": item["genome"]["id"],
                    "epistemic_fitness": item["epistemic_fitness"],
                }
                for item in epistemic_scored
            ],
            "selection_decision": {
                "mechanism_id": decision["mechanism_id"],
                "survival_set": [genome["id"] for genome in decision["survival_set"]],
                "dormant_set": [genome["id"] for genome in decision["dormant_set"]],
                "extinction_set": [genome["id"] for genome in decision["extinction_set"]],
                "revival_set": [genome["id"] for genome in decision["revival_set"]],
                "epistemic_changed_outcome": decision["epistemic_changed_outcome"],
            },
            "population": self.physics.population,
        }
        self.physics.cycles.append(cycle)
        self.physics.hypergraph.record_cycle(cycle)
        observer_result = self.observer_loop.observe_reflexive_cycle(cycle)
        next_feedback = self.meaning_feedback.update(
            generation_index,
            observer_result["observed"]["self_description"],
            observer_result["observed"]["fitness_explanations"],
            observer_result["semantic_graph"],
        )
        next_self_model = self.self_model.update(generation_index, next_feedback, observer_result, pressure)
        self.understanding_graph.record(previous_self_model, next_self_model, next_feedback, generation_index)
        self.lineage.record_cycle(
            self.physics.population,
            mutation_events,
            decision,
            self.feedback,
            previous_self_model,
            generation_index,
        )
        cycle["observer_in_loop"] = observer_result["observer_event"]
        cycle["meaning_feedback_output"] = next_feedback
        cycle["self_model_output"] = next_self_model
        self.feedback = next_feedback
        self.cycles.append(cycle)
        self.reflexive_mutation_events.extend(mutation_events)
        self.semantic_selection_records.append(selection_mechanism)
        self.epistemic_records.extend(cycle["epistemic_fitness"])
        return cycle

    def record(self) -> dict[str, Any]:
        observer_export = self.observer_loop.export()
        explanation_dag = self.lineage.export()
        recursive_graph = self.understanding_graph.export()
        changed_outcomes = sum(1 for cycle in self.cycles if cycle["selection_decision"]["epistemic_changed_outcome"])
        return {
            "kernel": "SAEE v0.7 Reflexive Evolution Kernel",
            "version": "0.7.0",
            "status": "local_v0_7_reflexive_evolution",
            "generation_id": f"v07-generation-{self.physics.generation_index:03d}",
            "cycles": self.cycles,
            "population": self.physics.population,
            "reflexive_mutation_events": self.reflexive_mutation_events,
            "epistemic_fitness_records": self.epistemic_records,
            "semantic_selection_records": self.semantic_selection_records,
            "meaning_feedback": self.meaning_feedback.export(),
            "interpretation_pressure": self.interpretation_pressure.export(),
            "self_model": self.self_model.snapshot(),
            "recursive_understanding_graph": recursive_graph,
            "explanation_influenced_dag": explanation_dag,
            "observer_in_loop": observer_export,
            "v0_5_generated_physics": self.physics.record(),
            "reflexive_summary": {
                "generation_count": len(self.cycles),
                "explanation_driven_mutation_count": sum(1 for event in self.reflexive_mutation_events if event["event_type"] == "explanation_driven_mutation"),
                "semantic_stabilization_count": sum(1 for event in self.reflexive_mutation_events if event["event_type"] == "semantic_stabilization"),
                "feedback_input_count": len([cycle for cycle in self.cycles if cycle["reflexive_feedback_input"]["feedback_id"] != "meaning_feedback_seed"]),
                "semantic_selection_count": len(self.semantic_selection_records),
                "epistemic_fitness_record_count": len(self.epistemic_records),
                "epistemic_changed_outcome_count": changed_outcomes,
                "self_model_update_count": len(recursive_graph["edges"]),
                "interpretation_influenced_edge_count": sum(1 for edge in explanation_dag["edges"] if edge["edge_type"] in {"explanation_influence", "semantic_selection_influence"}),
                "observer_embedded_count": len(observer_export["events"]),
            },
            "boundaries": [
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_external_code_as_genome",
                "no_publication_claim",
                "not_production_runtime",
                "not_self_aware_system",
                "not_verified_semantic_causality",
                "local_reproducible_simulation_only",
            ],
        }

    def _reconfigure_population(self, decision: dict[str, Any]) -> list[dict[str, Any]]:
        retained: dict[str, dict[str, Any]] = {}
        for key in ("survival_set", "dormant_set", "revival_set"):
            for genome in decision.get(key, []):
                retained[genome["id"]] = copy.deepcopy(genome)
        active = sorted(
            [genome for genome in retained.values() if genome.get("status") == "active"],
            key=lambda genome: (float(genome.get("selection_score", 0.0)), genome["id"]),
            reverse=True,
        )[:14]
        dormant = sorted(
            [genome for genome in retained.values() if genome.get("status") == "dormant"],
            key=lambda genome: genome["id"],
        )[:5]
        return sorted(active + dormant, key=lambda genome: genome["id"])


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "run_record.json": record,
        "reflexive_cycles.json": record["cycles"],
        "reflexive_mutations.json": record["reflexive_mutation_events"],
        "epistemic_fitness.json": record["epistemic_fitness_records"],
        "semantic_selection.json": record["semantic_selection_records"],
        "meaning_feedback.json": record["meaning_feedback"],
        "interpretation_pressure.json": record["interpretation_pressure"],
        "self_model.json": record["self_model"],
        "recursive_understanding_graph.json": record["recursive_understanding_graph"],
        "explanation_influenced_dag.json": record["explanation_influenced_dag"],
        "observer_in_loop.json": record["observer_in_loop"],
        "reflexive_summary.json": record["reflexive_summary"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
