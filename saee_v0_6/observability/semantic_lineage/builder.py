"""Build semantic lineage from observed cycles."""

from __future__ import annotations

from typing import Any


class SemanticLineageBuilder:
    """Convert structural events into meaning-level transitions."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def add_cycle(
        self,
        cycle: dict[str, Any],
        observation_event: dict[str, Any],
        rule_record: dict[str, Any],
        fitness_explanations: list[dict[str, Any]],
    ) -> None:
        generation = cycle["generation_index"]
        meaning_id = f"meaning_g{generation:03d}_{cycle['generated_evolution_law']['law_id']}"
        self.nodes[meaning_id] = {
            "id": meaning_id,
            "node_type": "semantic_generation_state",
            "generation_index": generation,
            "meaning": observation_event["semantic_claim"],
            "law_id": cycle["generated_evolution_law"]["law_id"],
            "regime_id": cycle["constructed_regime"]["regime_id"],
        }
        self._edge(observation_event["event_id"], meaning_id, "cause_of", generation)
        self._edge(rule_record["law_id"], meaning_id, "meaning_of_rule", generation)
        for explanation in fitness_explanations:
            explanation_id = explanation["explanation_id"]
            self.nodes[explanation_id] = {
                "id": explanation_id,
                "node_type": "fitness_selection_meaning",
                "generation_index": generation,
                "meaning": explanation["explanation"],
                "genome_id": explanation["genome_id"],
            }
            self._edge(meaning_id, explanation_id, "meaning_transition", generation)

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "semantic_lineage_graph",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"], edge["edge_type"])),
        }

    def _edge(self, source: str, target: str, edge_type: str, generation_index: int) -> None:
        self.edges.append(
            {
                "from": source,
                "to": target,
                "edge_type": edge_type,
                "generation_index": generation_index,
            }
        )
