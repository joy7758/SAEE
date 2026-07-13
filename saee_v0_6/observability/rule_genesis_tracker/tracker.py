"""Track generated rule origins and ancestry."""

from __future__ import annotations

from typing import Any


class RuleGenesisTracker:
    """Build origin records for every generated evolution law."""

    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def track(self, cycle: dict[str, Any], observation_event: dict[str, Any]) -> dict[str, Any]:
        law = cycle["generated_evolution_law"]
        phase = cycle["phase_emergence"]
        dimensions = cycle["dimension_state"]["dimensions"]
        record = {
            "law_id": law["law_id"],
            "generation_index": cycle["generation_index"],
            "parents": law.get("parents", []),
            "origin_observation": law["origin_observation"],
            "origin_event": observation_event["event_id"],
            "origin_phase": phase["phase_id"],
            "source_terms": law["source_terms"],
            "source_dimensions": [
                dimension_id
                for dimension_id, dimension in dimensions.items()
                if dimension.get("source_token") in law["source_terms"]
            ],
            "genesis_explanation": (
                f"{law['law_id']} emerged from observation {law['origin_observation']} "
                f"using terms {', '.join(law['source_terms'][:4])}."
            ),
        }
        self.records[law["law_id"]] = record
        for parent in law.get("parents", []):
            self.edges.append(
                {
                    "from": parent,
                    "to": law["law_id"],
                    "edge_type": "rule_ancestry",
                    "generation_index": cycle["generation_index"],
                }
            )
        return record

    def export(self) -> dict[str, Any]:
        return {
            "graph_type": "rule_ancestry_graph",
            "nodes": [self.records[key] for key in sorted(self.records)],
            "edges": sorted(self.edges, key=lambda edge: (edge["generation_index"], edge["from"], edge["to"])),
        }
