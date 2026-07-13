"""Lineage graph that keeps identity continuity explicit."""

from __future__ import annotations

from typing import Any


class IdentityPreservingLineageGraph:
    """Record identity continuity edges across generations."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.breaks: list[dict[str, Any]] = []

    def record(
        self,
        population: list[dict[str, Any]],
        identity_selection: dict[str, Any],
        consistency: dict[str, Any],
        identity_snapshot: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        anchor = identity_snapshot["identity_anchor"]
        anchor_id = anchor["identity_anchor_id"]
        self.nodes[anchor_id] = {
            "id": anchor_id,
            "node_type": "identity_anchor",
            "anchor_hash": anchor["anchor_hash"],
        }
        for genome in population:
            identity = genome.get("identity_continuity", {})
            self.nodes[genome["id"]] = {
                "id": genome["id"],
                "node_type": "genome",
                "generation_index": generation_index,
                "status": genome.get("status"),
                "identity_continuity_score": identity.get("identity_continuity_score"),
                "identity_preserved": identity.get("identity_preserved"),
                "identity_anchor_id": anchor_id,
            }
            self._edge(anchor_id, genome["id"], "identity_anchor_continuity", generation_index, {
                "identity_continuity_score": identity.get("identity_continuity_score"),
            })
            for parent in genome.get("parents", []):
                self._edge(parent, genome["id"], "identity_preserving_descent", generation_index, {
                    "identity_anchor_id": anchor_id,
                })
            if not identity.get("identity_preserved", True):
                self.breaks.append(
                    {
                        "generation_index": generation_index,
                        "genome_id": genome["id"],
                        "identity_anchor_id": anchor_id,
                        "reason": "identity_not_preserved",
                    }
                )
        record = {
            "generation_index": generation_index,
            "identity_anchor_id": anchor_id,
            "population_count": len(population),
            "suppressed_count": identity_selection["suppressed_count"],
            "consistency_rejected_count": consistency["rejected_count"],
            "continuity_break_count": len(self.breaks),
            "status": "identity_continuity_preserved" if not self.breaks else "identity_break_detected",
        }
        return record

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "identity_preserving_lineage_graph",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"], edge["edge_type"])),
            "identity_breaks": list(self.breaks),
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

