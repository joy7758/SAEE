"""Explain generated fitness and selection decisions."""

from __future__ import annotations

from typing import Any


class FitnessInterpretabilityLayer:
    """Create explanations for generated fitness and survival outcomes."""

    def __init__(self) -> None:
        self.explanations: list[dict[str, Any]] = []

    def explain_cycle(self, cycle: dict[str, Any]) -> list[dict[str, Any]]:
        explanations = []
        population_by_id = {genome["id"]: genome for genome in cycle["population"]}
        for status, key in (
            ("survived", "survival_set"),
            ("dormant", "dormant_set"),
            ("extinct", "extinction_set"),
        ):
            for genome_id in cycle["selection_decision"].get(key, []):
                genome = population_by_id.get(genome_id)
                if genome is None:
                    genome = {"id": genome_id, "fitness": {}, "selection_score": 0.0}
                explanations.append(self._explain_genome(cycle, genome, status))
        self.explanations.extend(explanations)
        return explanations

    def export(self) -> list[dict[str, Any]]:
        return list(self.explanations)

    def _explain_genome(self, cycle: dict[str, Any], genome: dict[str, Any], status: str) -> dict[str, Any]:
        fitness = genome.get("fitness", {})
        components = fitness.get("components", [])
        top_components = sorted(
            components,
            key=lambda item: (float(item.get("contribution", 0.0)), item.get("term_id", "")),
            reverse=True,
        )[:3]
        return {
            "explanation_id": f"fitness_explain_g{cycle['generation_index']:03d}_{genome['id']}",
            "generation_index": cycle["generation_index"],
            "genome_id": genome["id"],
            "status": status,
            "fitness_function_id": cycle["generated_fitness_function"]["fitness_function_id"],
            "selection_mechanism_id": cycle["selection_mechanism"]["mechanism_id"],
            "selection_score": genome.get("selection_score", 0.0),
            "top_fitness_factors": top_components,
            "explanation": (
                f"{genome['id']} became {status} because generated fitness "
                f"{cycle['generated_fitness_function']['fitness_function_id']} and selection mechanism "
                f"{cycle['selection_mechanism']['mechanism_id']} assigned score {genome.get('selection_score', 0.0)}."
            ),
        }
