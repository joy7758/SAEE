"""Analyze lineage graph dynamics by generation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


class GraphDynamics:
    """Measure edge-type and generation-level graph dynamics."""

    def analyze(self, record: dict[str, Any]) -> dict[str, Any]:
        graph = record["identity_preserving_lineage_graph"]
        edge_type_counts = Counter(edge["edge_type"] for edge in graph.get("edges", []))
        by_generation: dict[int, Counter[str]] = defaultdict(Counter)
        for edge in graph.get("edges", []):
            by_generation[int(edge["generation_index"])][edge["edge_type"]] += 1
        return {
            "analysis_type": "graph_dynamics",
            "edge_type_counts": dict(sorted(edge_type_counts.items())),
            "generation_edge_counts": [
                {
                    "generation_index": generation,
                    "edge_counts": dict(sorted(counter.items())),
                    "total_edges": sum(counter.values()),
                }
                for generation, counter in sorted(by_generation.items())
            ],
            "continuity_edge_ratio": round(
                edge_type_counts.get("identity_anchor_continuity", 0)
                / max(1, sum(edge_type_counts.values())),
                6,
            ),
        }

