"""SAEE v0.6 observable evolution kernel.

Agent-readable loop:
Run v0.5 generated physics -> Evolution Observation Engine
-> Rule Genesis Tracker -> Fitness Interpretability Layer
-> Semantic Lineage Graph -> Self-Description Generator
-> Causal Reconstruction -> Counter-Observer Loop.

v0.6 observes and explains v0.5 outputs; it does not change v0.5 mechanics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_v0_5.runtime.physics_loop import OpenEndedPhysicsLoop
from saee_v0_6.cognition.causal_reconstruction import CausalReconstructionEngine
from saee_v0_6.cognition.self_description_engine import SelfDescriptionGenerator
from saee_v0_6.observability.evolution_observer import EvolutionObservationEngine
from saee_v0_6.observability.fitness_interpreter import FitnessInterpretabilityLayer
from saee_v0_6.observability.rule_genesis_tracker import RuleGenesisTracker
from saee_v0_6.observability.semantic_lineage import SemanticLineageBuilder
from saee_v0_6.runtime.observer_loop import CounterObserverLoop


class ObservableEvolutionKernel:
    """Wrap v0.5 physics with self-observation and self-explanation."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.physics = OpenEndedPhysicsLoop(seed_genome, initial_population_size)
        self.observer = EvolutionObservationEngine()
        self.rule_tracker = RuleGenesisTracker()
        self.fitness_interpreter = FitnessInterpretabilityLayer()
        self.semantic_lineage = SemanticLineageBuilder()
        self.self_description = SelfDescriptionGenerator()
        self.causal_reconstructor = CausalReconstructionEngine()
        self.counter_observer = CounterObserverLoop()
        self.observed_cycles: list[dict[str, Any]] = []

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            cycle = self.physics.step()
            self._observe_cycle(cycle)
        return self.record()

    def _observe_cycle(self, cycle: dict[str, Any]) -> dict[str, Any]:
        feedback_input = self.counter_observer.before_cycle()
        observation_event = self.observer.observe_cycle(cycle, feedback_input)
        rule_record = self.rule_tracker.track(cycle, observation_event)
        fitness_explanations = self.fitness_interpreter.explain_cycle(cycle)
        self.semantic_lineage.add_cycle(cycle, observation_event, rule_record, fitness_explanations)
        self_description = self.self_description.describe(
            cycle,
            observation_event,
            rule_record,
            fitness_explanations,
        )
        causal_traces = self.causal_reconstructor.reconstruct(
            cycle,
            observation_event,
            fitness_explanations,
        )
        feedback_output = self.counter_observer.after_cycle(cycle, observation_event, self_description)
        observed = {
            "generation_id": cycle["generation_id"],
            "generation_index": cycle["generation_index"],
            "observation_event": observation_event,
            "rule_genesis": rule_record,
            "fitness_explanations": fitness_explanations,
            "self_description": self_description,
            "causal_traces": causal_traces,
            "counter_observer": {
                "input": feedback_input,
                "output": feedback_output,
            },
        }
        self.observed_cycles.append(observed)
        return observed

    def record(self) -> dict[str, Any]:
        physics_record = self.physics.record()
        observation_events = self.observer.export()
        rule_graph = self.rule_tracker.export()
        fitness_explanations = self.fitness_interpreter.export()
        semantic_graph = self.semantic_lineage.export()
        self_descriptions = self.self_description.export()
        causal_traces = self.causal_reconstructor.export()
        observer_events = self.counter_observer.export()
        return {
            "kernel": "SAEE v0.6 Evolution Observability Kernel",
            "version": "0.6.0",
            "status": "local_v0_6_evolution_observability",
            "generation_id": physics_record["generation_id"],
            "v0_5_physics_record": physics_record,
            "observed_cycles": self.observed_cycles,
            "observation_events": observation_events,
            "rule_ancestry_graph": rule_graph,
            "fitness_explanations": fitness_explanations,
            "semantic_lineage_graph": semantic_graph,
            "self_descriptions": self_descriptions,
            "causal_reconstructions": causal_traces,
            "observer_loop": observer_events,
            "observability_summary": {
                "observed_generation_count": len(self.observed_cycles),
                "observation_event_count": len(observation_events),
                "rule_genesis_count": len(rule_graph["nodes"]),
                "fitness_explanation_count": len(fitness_explanations),
                "semantic_node_count": len(semantic_graph["nodes"]),
                "semantic_edge_count": len(semantic_graph["edges"]),
                "causal_reconstruction_count": len(causal_traces),
                "self_description_count": len(self_descriptions),
                "observer_feedback_count": len(observer_events),
                "second_order_feedback_count": sum(1 for event in observer_events if event["second_order_feedback"]),
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
                "not_verified_scientific_explanation",
                "does_not_change_v0_5_evolution_mechanics",
                "local_reproducible_simulation_only",
            ],
        }


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "run_record.json": record,
        "v0_5_physics_record.json": record["v0_5_physics_record"],
        "observation_events.json": record["observation_events"],
        "rule_ancestry_graph.json": record["rule_ancestry_graph"],
        "fitness_explanations.json": record["fitness_explanations"],
        "semantic_lineage_graph.json": record["semantic_lineage_graph"],
        "self_descriptions.json": record["self_descriptions"],
        "causal_reconstructions.json": record["causal_reconstructions"],
        "observer_loop.json": record["observer_loop"],
        "observability_summary.json": record["observability_summary"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
