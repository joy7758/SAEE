"""Observe v0.5 evolutionary processes without changing mechanics."""

from __future__ import annotations

import hashlib
from typing import Any


def stable_digest(parts: list[str], size: int = 10) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:size]


class EvolutionObservationEngine:
    """Record causal observations for generated evolution physics."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def observe_cycle(self, cycle: dict[str, Any], observer_feedback: dict[str, Any] | None) -> dict[str, Any]:
        law = cycle["generated_evolution_law"]
        fitness = cycle["generated_fitness_function"]
        selection = cycle["selection_mechanism"]
        regime = cycle["constructed_regime"]
        phase = cycle["phase_emergence"]
        observation = cycle["observation"]
        dimension_events = cycle["dimension_state"]["dimension_events"]
        cause_chain = [
            observation["observation_id"],
            law["law_id"],
            fitness["fitness_function_id"],
            selection["mechanism_id"],
            phase["phase_id"],
            regime["regime_id"],
        ]
        event_id = f"obs_event_{cycle['generation_index']:03d}_{stable_digest(cause_chain)}"
        event = {
            "event_id": event_id,
            "generation_index": cycle["generation_index"],
            "observed_process": "generated_evolution_physics_cycle",
            "cause_chain": cause_chain,
            "observer_feedback_input": observer_feedback,
            "semantic_claim": self._semantic_claim(cycle),
            "rule_birth": {
                "law_id": law["law_id"],
                "origin_observation": law["origin_observation"],
                "source_terms": law["source_terms"],
            },
            "mutation_causes": self._mutation_causes(cycle),
            "dimension_causes": self._dimension_causes(dimension_events, observation),
            "selection_causes": {
                "mechanism_id": selection["mechanism_id"],
                "origin_law": selection["origin_law"],
                "origin_fitness_function": selection["origin_fitness_function"],
            },
        }
        self.events.append(event)
        return event

    def export(self) -> list[dict[str, Any]]:
        return list(self.events)

    def _semantic_claim(self, cycle: dict[str, Any]) -> str:
        novelty = cycle["observation"]["novelty"]["novelty_score"]
        law_terms = ", ".join(cycle["generated_evolution_law"]["source_terms"][:3])
        return (
            f"Generation {cycle['generation_index']} generated rule structure from novelty "
            f"{novelty:.2f}, source terms [{law_terms}], and phase "
            f"{cycle['phase_emergence']['phase_id']}."
        )

    def _mutation_causes(self, cycle: dict[str, Any]) -> list[dict[str, Any]]:
        causes = []
        law = cycle["generated_evolution_law"]
        regime = cycle["constructed_regime"]
        for event in cycle.get("variation_events", []):
            causes.append(
                {
                    "child": event["child"],
                    "event_type": event["event_type"],
                    "cause": [
                        event.get("source_law", law["law_id"]),
                        event.get("source_clause"),
                        event.get("source_dimension"),
                        regime["regime_id"],
                    ],
                    "explanation": f"{event['child']} was produced by generated law {event.get('source_law', law['law_id'])}.",
                }
            )
        return causes

    def _dimension_causes(self, events: list[dict[str, Any]], observation: dict[str, Any]) -> list[dict[str, Any]]:
        causes = []
        for event in events:
            causes.append(
                {
                    "dimension_id": event["dimension_id"],
                    "event_type": event["event_type"],
                    "origin_observation": observation["observation_id"],
                    "cause": event.get("source_token") or event.get("parents") or observation["phase_signal"]["signature"],
                }
            )
        return causes
