"""Embed the observer inside the evolution cycle."""

from __future__ import annotations

from typing import Any

from saee_v0_6.runtime.observable_kernel import ObservableEvolutionKernel


class ObserverInTheLoopSystem:
    """Reuse v0.6 observability components as causal runtime participants."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.observable = ObservableEvolutionKernel(seed_genome, initial_population_size)
        self.events: list[dict[str, Any]] = []

    def observe_reflexive_cycle(self, cycle: dict[str, Any]) -> dict[str, Any]:
        observed = self.observable._observe_cycle(cycle)
        event = {
            "observer_loop_id": f"observer_in_loop_g{cycle['generation_index']:03d}",
            "generation_index": cycle["generation_index"],
            "observed_cycle": cycle["generation_id"],
            "observation_event_id": observed["observation_event"]["event_id"],
            "self_description_id": observed["self_description"]["description_id"],
            "observer_embedded": True,
        }
        self.events.append(event)
        return {
            "observed": observed,
            "observer_event": event,
            "semantic_graph": self.observable.semantic_lineage.export(),
        }

    def export(self) -> dict[str, Any]:
        return {
            "events": list(self.events),
            "observation_events": self.observable.observer.export(),
            "rule_ancestry_graph": self.observable.rule_tracker.export(),
            "fitness_explanations": self.observable.fitness_interpreter.export(),
            "semantic_lineage_graph": self.observable.semantic_lineage.export(),
            "self_descriptions": self.observable.self_description.export(),
            "causal_reconstructions": self.observable.causal_reconstructor.export(),
            "counter_observer": self.observable.counter_observer.export(),
        }
