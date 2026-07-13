"""Directed acyclic lineage graph for SAEE Kernel v0.2."""

from __future__ import annotations

import copy
from typing import Any


class LineageGraph:
    """Store genomes as graph nodes and parent-child events as edges."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def record_population(self, population: list[dict[str, Any]], generation_id: int) -> None:
        for genome in population:
            self.ensure_node(genome, generation_id)
            for parent in genome.get("parents", []):
                self.add_edge(parent, genome["id"], "initial_parent", generation_id)

    def record_branch_events(self, population: list[dict[str, Any]], branch_events: list[dict[str, Any]]) -> None:
        by_id = {genome["id"]: genome for genome in population}
        for event in branch_events:
            child = by_id[event["child"]]
            self.ensure_node(child, event["generation_id"])
            for parent in event["parents"]:
                self.add_edge(parent, event["child"], event["event"], event["generation_id"])

    def record_selection_decision(self, decision: dict[str, list[dict[str, Any]]], generation_id: int) -> None:
        for event, key in (
            ("survival", "survival_set"),
            ("dormancy", "dormant_set"),
            ("extinction", "extinction_set"),
            ("revival", "revival_set"),
        ):
            for genome in decision.get(key, []):
                self.ensure_node(genome, generation_id)
                self.nodes[genome["id"]]["status"] = genome["status"]
                self.nodes[genome["id"]]["selection_events"] = copy.deepcopy(
                    genome.get("selection_events", [])
                )
                self.nodes[genome["id"]]["last_seen_generation"] = generation_id
                if event == "revival":
                    self.add_edge(genome["id"], genome["id"], "revival", generation_id)

    def ensure_node(self, genome: dict[str, Any], generation_id: int) -> None:
        node = self.nodes.setdefault(
            genome["id"],
            {
                "id": genome["id"],
                "parents": copy.deepcopy(genome.get("parents", [])),
                "created_generation": generation_id,
                "last_seen_generation": generation_id,
                "status": genome.get("status", "active"),
                "mutation_history": copy.deepcopy(genome.get("mutation_history", [])),
                "selection_events": copy.deepcopy(genome.get("selection_events", [])),
            },
        )
        node["last_seen_generation"] = max(node["last_seen_generation"], generation_id)
        node["status"] = genome.get("status", node["status"])

    def add_edge(self, parent: str, child: str, event_type: str, generation_id: int) -> None:
        edge = {
            "from": parent,
            "to": child,
            "event_type": event_type,
            "generation_id": generation_id,
        }
        if edge not in self.edges:
            self.edges.append(edge)

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "directed_acyclic_evolution_graph",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_id"], edge["from"], edge["to"], edge["event_type"])),
        }

