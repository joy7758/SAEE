"""Graph of recursive self-model updates."""

from __future__ import annotations

from typing import Any


class RecursiveUnderstandingGraph:
    """Record how the self-model changes evolution behavior."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def record(
        self,
        previous_model: dict[str, Any],
        next_model: dict[str, Any],
        feedback: dict[str, Any],
        generation_index: int,
    ) -> None:
        self.nodes[previous_model["self_model_id"]] = dict(previous_model)
        self.nodes[next_model["self_model_id"]] = dict(next_model)
        self.edges.append(
            {
                "from": previous_model["self_model_id"],
                "to": next_model["self_model_id"],
                "edge_type": "recursive_self_model_update",
                "generation_index": generation_index,
                "feedback_id": feedback["feedback_id"],
            }
        )

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "recursive_understanding_graph",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"])),
        }
