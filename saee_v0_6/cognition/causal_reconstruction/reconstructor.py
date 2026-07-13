"""Reconstruct outcome-to-cause paths from observed events."""

from __future__ import annotations

from typing import Any


class CausalReconstructionEngine:
    """Reverse-map outcomes to causes."""

    def __init__(self) -> None:
        self.reconstructions: list[dict[str, Any]] = []

    def reconstruct(
        self,
        cycle: dict[str, Any],
        observation_event: dict[str, Any],
        fitness_explanations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        records = []
        for explanation in fitness_explanations:
            records.append(
                {
                    "reconstruction_id": f"cause_{explanation['explanation_id']}",
                    "generation_index": cycle["generation_index"],
                    "outcome": {
                        "genome_id": explanation["genome_id"],
                        "status": explanation["status"],
                    },
                    "cause_path": [
                        observation_event["event_id"],
                        cycle["generated_evolution_law"]["law_id"],
                        cycle["generated_fitness_function"]["fitness_function_id"],
                        cycle["selection_mechanism"]["mechanism_id"],
                        explanation["explanation_id"],
                    ],
                    "reverse_mapping": (
                        f"Outcome {explanation['status']} for {explanation['genome_id']} maps back to "
                        f"selection {cycle['selection_mechanism']['mechanism_id']}, fitness "
                        f"{cycle['generated_fitness_function']['fitness_function_id']}, law "
                        f"{cycle['generated_evolution_law']['law_id']}, and observation "
                        f"{observation_event['event_id']}."
                    ),
                }
            )
        self.reconstructions.extend(records)
        return records

    def export(self) -> list[dict[str, Any]]:
        return list(self.reconstructions)
