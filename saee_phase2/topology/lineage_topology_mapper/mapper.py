"""Map lineage graph topology from observed evolution."""

from __future__ import annotations

from collections import Counter
from typing import Any


class LineageTopologyMapper:
    """Measure branching, bottlenecks, and diversity changes."""

    def map(self, record: dict[str, Any]) -> dict[str, Any]:
        graph = record["identity_preserving_lineage_graph"]
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        descent_edges = [edge for edge in edges if edge["edge_type"] == "identity_preserving_descent"]
        anchor_edges = [edge for edge in edges if edge["edge_type"] == "identity_anchor_continuity"]
        outdegree = Counter(edge["from"] for edge in descent_edges)
        indegree = Counter(edge["to"] for edge in descent_edges)
        generation_population = {
            cycle["generation_index"]: len(cycle["population"])
            for cycle in record["cycles"]
        }
        diversity_series = [
            {
                "generation_index": generation,
                "population_count": count,
            }
            for generation, count in sorted(generation_population.items())
        ]
        bottlenecks = [
            {
                "node_id": node_id,
                "outdegree": degree,
            }
            for node_id, degree in outdegree.most_common()
            if degree >= 2
        ]
        branching_density = round(len(descent_edges) / max(1, len(nodes)), 6)
        return {
            "analysis_type": "lineage_topology_mapping",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "descent_edge_count": len(descent_edges),
            "identity_anchor_edge_count": len(anchor_edges),
            "branching_density": branching_density,
            "bottlenecks": bottlenecks,
            "max_outdegree": max(outdegree.values(), default=0),
            "max_indegree": max(indegree.values(), default=0),
            "diversity_series": diversity_series,
            "diversity_change": self._diversity_change(diversity_series),
            "identity_break_count": len(graph.get("identity_breaks", [])),
        }

    def _diversity_change(self, series: list[dict[str, Any]]) -> str:
        if len(series) < 2:
            return "insufficient_observation"
        start = series[0]["population_count"]
        end = series[-1]["population_count"]
        if end > start:
            return "diversity_growth"
        if end < start:
            return "diversity_decay"
        return "diversity_stable"

