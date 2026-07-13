"""Lineage DAG preserving population and rule evolution."""

from __future__ import annotations

import copy
from typing import Any


class V03LineageDAG:
    """Directed acyclic lineage graph for genomes and rule genomes."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.rule_nodes: dict[str, dict[str, Any]] = {}
        self.rule_edges: list[dict[str, Any]] = []

    def record_population(self, population: list[dict[str, Any]], generation_index: int) -> None:
        for genome in population:
            self.ensure_node(genome, generation_index)
            for parent in genome.get("parents", []):
                self.add_edge(parent, genome["id"], "parent", generation_index)

    def record_events(self, events: list[dict[str, Any]]) -> None:
        for event in events:
            for parent in event["parents"]:
                self.add_edge(parent, event["child"], event["event_type"], event["generation_index"])

    def record_selection(self, decision: dict[str, list[dict[str, Any]]], generation_index: int) -> None:
        for key in ("survival_set", "dormant_set", "extinction_set", "revival_set"):
            for genome in decision[key]:
                self.ensure_node(genome, generation_index)
                self.nodes[genome["id"]]["status"] = genome.get("status")
                self.nodes[genome["id"]]["selection_events"] = copy.deepcopy(genome.get("selection_events", []))
                self.nodes[genome["id"]]["last_seen_generation"] = generation_index

    def record_rule(self, rule: dict[str, Any], generation_index: int) -> None:
        self.rule_nodes[rule["id"]] = {
            "id": rule["id"],
            "version": rule["version"],
            "parents": copy.deepcopy(rule.get("parents", [])),
            "generation_index": generation_index,
            "mutable_fields": copy.deepcopy(rule.get("mutable_fields", [])),
            "guards": copy.deepcopy(rule.get("guards", [])),
        }
        for parent in rule.get("parents", []):
            edge = {
                "from": parent,
                "to": rule["id"],
                "event_type": "rule_mutation",
                "generation_index": generation_index,
            }
            if edge not in self.rule_edges:
                self.rule_edges.append(edge)

    def ensure_node(self, genome: dict[str, Any], generation_index: int) -> None:
        node = self.nodes.setdefault(
            genome["id"],
            {
                "id": genome["id"],
                "parents": copy.deepcopy(genome.get("parents", [])),
                "created_generation": generation_index,
                "last_seen_generation": generation_index,
                "status": genome.get("status", "active"),
                "mutation_history": copy.deepcopy(genome.get("mutation_history", [])),
                "selection_events": copy.deepcopy(genome.get("selection_events", [])),
            },
        )
        node["last_seen_generation"] = max(node["last_seen_generation"], generation_index)

    def add_edge(self, parent: str, child: str, event_type: str, generation_index: int) -> None:
        edge = {
            "from": parent,
            "to": child,
            "event_type": event_type,
            "generation_index": generation_index,
        }
        if edge not in self.edges and parent != child:
            self.edges.append(edge)

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "directed_acyclic_evolution_graph",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"], edge["event_type"])),
            "rule_graph": {
                "nodes": [self.rule_nodes[key] for key in sorted(self.rule_nodes)],
                "edges": sorted(self.rule_edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"])),
            },
        }

