"""Single lineage DAG for the SAEE v1.0 stable runtime."""

from __future__ import annotations

from typing import Any


class LineageDAG:
    """Record genome descent and selection in one DAG-like graph."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def record_population(self, population: list[dict[str, Any]], generation_index: int) -> None:
        for genome in population:
            self.nodes[genome["id"]] = {
                "id": genome["id"],
                "generation_index": generation_index,
                "version": genome.get("version"),
                "status": genome.get("status", "active"),
                "fitness_score": genome.get("fitness_score"),
            }
            for parent in genome.get("parents", []):
                self.edges.append(
                    {
                        "from": parent,
                        "to": genome["id"],
                        "edge_type": "descent",
                        "generation_index": generation_index,
                    }
                )

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "lineage_dag",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"])),
        }

