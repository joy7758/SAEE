"""Hypergraph for genomes, laws, dimensions, fitness, selection, and regimes."""

from __future__ import annotations

import copy
from typing import Any


class HyperGraphLineage:
    """Record generated physics as typed nodes and hyperedges."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.hyperedges: list[dict[str, Any]] = []

    def add_node(self, node_id: str, node_type: str, payload: dict[str, Any], generation_index: int) -> None:
        self.nodes[node_id] = {
            "id": node_id,
            "node_type": node_type,
            "generation_index": generation_index,
            "payload": copy.deepcopy(payload),
        }

    def add_edge(
        self,
        edge_type: str,
        sources: list[str],
        targets: list[str],
        generation_index: int,
        payload: dict[str, Any] | None = None,
    ) -> None:
        edge = {
            "edge_id": f"edge_{len(self.hyperedges):05d}",
            "edge_type": edge_type,
            "sources": list(sources),
            "targets": list(targets),
            "generation_index": generation_index,
            "payload": copy.deepcopy(payload or {}),
        }
        self.hyperedges.append(edge)

    def record_cycle(self, cycle: dict[str, Any]) -> None:
        generation_index = cycle["generation_index"]
        law = cycle["generated_evolution_law"]
        fitness = cycle["generated_fitness_function"]
        selection = cycle["selection_mechanism"]
        regime = cycle["constructed_regime"]
        phase = cycle["phase_emergence"]

        self.add_node(law["law_id"], "generated_evolution_law", law, generation_index)
        self.add_node(fitness["fitness_function_id"], "generated_fitness_function", fitness, generation_index)
        self.add_node(selection["mechanism_id"], "selection_mechanism", selection, generation_index)
        self.add_node(regime["regime_id"], "constructed_regime", regime, generation_index)
        self.add_node(phase["phase_id"], "phase_emergence", phase, generation_index)

        for dimension in cycle["dimension_state"]["dimensions"].values():
            self.add_node(dimension["dimension_id"], "evolution_dimension", dimension, generation_index)

        for genome in cycle["population"]:
            self.add_node(genome["id"], "genome", genome, generation_index)
            for parent in genome.get("parents", []):
                self.add_edge("genome_descent", [parent], [genome["id"]], generation_index)

        self.add_edge(
            "law_generates_fitness",
            [law["law_id"]],
            [fitness["fitness_function_id"]],
            generation_index,
        )
        self.add_edge(
            "fitness_and_law_generate_selection",
            [law["law_id"], fitness["fitness_function_id"]],
            [selection["mechanism_id"]],
            generation_index,
        )
        self.add_edge(
            "phase_and_law_construct_regime",
            [phase["phase_id"], law["law_id"]],
            [regime["regime_id"]],
            generation_index,
        )

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "generated_evolution_physics_hypergraph",
            "nodes": [self.nodes[key] for key in sorted(self.nodes)],
            "hyperedges": list(self.hyperedges),
        }
