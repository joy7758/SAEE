"""Generate self-descriptions for observed evolution."""

from __future__ import annotations

from typing import Any


class SelfDescriptionGenerator:
    """Produce structured self-explanations from observation records."""

    def __init__(self) -> None:
        self.descriptions: list[dict[str, Any]] = []

    def describe(
        self,
        cycle: dict[str, Any],
        observation_event: dict[str, Any],
        rule_record: dict[str, Any],
        fitness_explanations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        dimension_events = cycle["dimension_state"]["dimension_events"]
        collapsed = [event["dimension_id"] for event in dimension_events if event["event_type"] == "dimension_collapse"]
        survived = cycle["selection_decision"]["survival_set"]
        description = {
            "description_id": f"self_desc_g{cycle['generation_index']:03d}",
            "generation_index": cycle["generation_index"],
            "why_i_evolved_this_structure": observation_event["semantic_claim"],
            "why_this_rule_emerged": rule_record["genesis_explanation"],
            "why_this_population_survived": self._population_survival_text(survived, fitness_explanations),
            "why_this_dimension_collapsed": self._dimension_collapse_text(collapsed, cycle),
            "observer_statement": (
                f"I observed my generated law {cycle['generated_evolution_law']['law_id']} "
                f"through event {observation_event['event_id']} and mapped it to semantic lineage."
            ),
        }
        self.descriptions.append(description)
        return description

    def export(self) -> list[dict[str, Any]]:
        return list(self.descriptions)

    def _population_survival_text(self, survived: list[str], explanations: list[dict[str, Any]]) -> str:
        if not survived:
            return "No surviving population was recorded in this cycle."
        explanation_by_id = {item["genome_id"]: item for item in explanations}
        examples = []
        for genome_id in survived[:3]:
            explanation = explanation_by_id.get(genome_id)
            if explanation:
                examples.append(f"{genome_id} survived with score {explanation['selection_score']}")
            else:
                examples.append(f"{genome_id} survived by selection decision")
        return "; ".join(examples) + "."

    def _dimension_collapse_text(self, collapsed: list[str], cycle: dict[str, Any]) -> str:
        if not collapsed:
            return "No dimension collapsed in this cycle."
        signature = cycle["observation"]["phase_signal"]["signature"]
        return f"Dimensions {', '.join(collapsed)} collapsed under phase signature {signature}."
