"""Lineage DAG that records interpretation influence."""

from __future__ import annotations

import copy
from typing import Any


class ExplanationInfluencedDAG:
    """Record genome lineage with explanation and self-model influence."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def record_cycle(
        self,
        population: list[dict[str, Any]],
        mutation_events: list[dict[str, Any]],
        decision: dict[str, Any],
        feedback: dict[str, Any],
        self_model: dict[str, Any],
        generation_index: int,
    ) -> None:
        for genome in population:
            self.nodes[genome["id"]] = {
                "id": genome["id"],
                "generation_index": generation_index,
                "status": genome.get("status"),
                "parents": copy.deepcopy(genome.get("parents", [])),
                "interpretation_history": copy.deepcopy(genome.get("interpretation_history", [])),
                "selection_score": genome.get("selection_score"),
            }
            for parent in genome.get("parents", []):
                self._edge(parent, genome["id"], "genome_descent", generation_index, {})
        for event in mutation_events:
            if "child" in event:
                self._edge(
                    event.get("parent", event.get("parents", ["unknown"])[0] if event.get("parents") else "unknown"),
                    event["child"],
                    "explanation_influence",
                    generation_index,
                    {
                        "feedback_input_id": feedback["feedback_id"],
                        "self_model_id": self_model["self_model_id"],
                        "mutation_probability": event.get("mutation_probability"),
                        "explanation_quality": event.get("explanation_quality"),
                    },
                )
        for key in ("survival_set", "dormant_set", "extinction_set"):
            for genome in decision.get(key, []):
                self._edge(
                    feedback["feedback_id"],
                    genome["id"],
                    "semantic_selection_influence",
                    generation_index,
                    {
                        "self_model_id": self_model["self_model_id"],
                        "outcome": key,
                    },
                )

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "explanation_influenced_dag",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"], edge["edge_type"])),
        }

    def _edge(self, source: str, target: str, edge_type: str, generation_index: int, payload: dict[str, Any]) -> None:
        self.edges.append(
            {
                "from": source,
                "to": target,
                "edge_type": edge_type,
                "generation_index": generation_index,
                "payload": payload,
            }
        )
