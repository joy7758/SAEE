"""Directed lineage graph for genomes, spaces, phases, and regimes."""

from __future__ import annotations

import copy
from typing import Any


class V04LineageGraph:
    """Preserve population lineage and evolution-space mutation history."""

    def __init__(self) -> None:
        self.genome_nodes: dict[str, dict[str, Any]] = {}
        self.genome_edges: list[dict[str, Any]] = []
        self.space_nodes: dict[str, dict[str, Any]] = {}
        self.space_edges: list[dict[str, Any]] = []
        self.phase_events: list[dict[str, Any]] = []
        self.regime_events: list[dict[str, Any]] = []
        self._last_space_id: str | None = None

    def record_population(self, population: list[dict[str, Any]], generation_index: int) -> None:
        for genome in population:
            self.ensure_genome(genome, generation_index)
            for parent in genome.get("parents", []):
                self.add_genome_edge(parent, genome["id"], "parent", generation_index)

    def record_mutations(self, events: list[dict[str, Any]]) -> None:
        for event in events:
            for parent in event.get("parents", []):
                self.add_genome_edge(parent, event["child"], event["event_type"], event["generation_index"])

    def record_selection(self, decision: dict[str, Any], generation_index: int) -> None:
        for key in ("survival_set", "dormant_set", "extinction_set", "revival_set"):
            for genome in decision.get(key, []):
                self.ensure_genome(genome, generation_index)
                node = self.genome_nodes[genome["id"]]
                node["status"] = genome.get("status")
                node["selection_events"] = copy.deepcopy(genome.get("selection_events", []))
                node["last_seen_generation"] = generation_index

    def record_space(
        self,
        evolution_space: dict[str, Any],
        mutation_event: dict[str, Any],
        phase: dict[str, Any],
        regime_event: dict[str, Any],
    ) -> None:
        space_id = evolution_space["space_id"]
        generation_index = mutation_event["generation_index"]
        self.space_nodes[space_id] = {
            "space_id": space_id,
            "version": evolution_space["version"],
            "generation_index": generation_index,
            "geometry_type": evolution_space["geometry_type"],
            "selection_topology": evolution_space["selection_topology"],
            "mutation_operator_mode": evolution_space["mutation_operator_mode"],
            "active_dimensions": [
                name
                for name, spec in evolution_space["dimensions"].items()
                if spec.get("active", True)
            ],
            "phase_type": phase["phase_type"],
            "regime": regime_event["regime"],
            "mutation_changes": copy.deepcopy(mutation_event["changes"]),
        }
        if self._last_space_id and self._last_space_id != space_id:
            self.space_edges.append(
                {
                    "from": self._last_space_id,
                    "to": space_id,
                    "event_type": "evolution_space_mutation",
                    "generation_index": generation_index,
                }
            )
        self._last_space_id = space_id
        self.phase_events.append(copy.deepcopy(phase))
        self.regime_events.append(copy.deepcopy(regime_event))

    def ensure_genome(self, genome: dict[str, Any], generation_index: int) -> None:
        node = self.genome_nodes.setdefault(
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

    def add_genome_edge(self, parent: str, child: str, event_type: str, generation_index: int) -> None:
        edge = {
            "from": parent,
            "to": child,
            "event_type": event_type,
            "generation_index": generation_index,
        }
        if parent != child and edge not in self.genome_edges:
            self.genome_edges.append(edge)

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "phase_transition_evolution_space_dag",
            "genome_graph": {
                "nodes": [self.genome_nodes[key] for key in sorted(self.genome_nodes)],
                "edges": sorted(
                    self.genome_edges,
                    key=lambda edge: (edge["generation_index"], edge["from"], edge["to"], edge["event_type"]),
                ),
            },
            "evolution_space_graph": {
                "nodes": [self.space_nodes[key] for key in sorted(self.space_nodes)],
                "edges": sorted(
                    self.space_edges,
                    key=lambda edge: (edge["generation_index"], edge["from"], edge["to"], edge["event_type"]),
                ),
            },
            "phase_events": copy.deepcopy(self.phase_events),
            "regime_events": copy.deepcopy(self.regime_events),
        }
