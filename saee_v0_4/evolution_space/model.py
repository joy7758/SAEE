"""Mutable evolution-space model for SAEE v0.4."""

from __future__ import annotations

import copy
from typing import Any


class EvolutionSpace:
    """Represent the evolving space in which evolution occurs."""

    def __init__(self) -> None:
        self.state = {
            "space_id": "evolution_space_v0_4_seed",
            "version": 0,
            "dimensions": {
                "technical": {"weight": 0.20, "active": True},
                "market": {"weight": 0.16, "active": True},
                "safety": {"weight": 0.22, "active": True},
                "cost": {"weight": 0.08, "active": True},
                "novelty": {"weight": 0.14, "active": True},
                "evolvability": {"weight": 0.20, "active": True},
            },
            "geometry_type": "weighted_manifold",
            "selection_topology": "niche_field",
            "mutation_operator_mode": "baseline",
            "history": [],
        }

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self.state)

    def active_dimensions(self) -> list[str]:
        return [
            name
            for name, spec in self.state["dimensions"].items()
            if spec.get("active", True)
        ]

    def mutate(self, phase: dict[str, Any], regime: str, generation_index: int) -> dict[str, Any]:
        """Mutate dimensions, geometry, topology, and operator mode."""
        mutation_event = {
            "generation_index": generation_index,
            "phase_type": phase["phase_type"],
            "regime": regime,
            "changes": [],
        }
        dimensions = self.state["dimensions"]

        if regime == "exploration":
            dimensions.setdefault("niche_diversity", {"weight": 0.10, "active": True})
            dimensions["novelty"]["weight"] = min(0.30, dimensions["novelty"]["weight"] + 0.02)
            self.state["geometry_type"] = "expanding_simplex"
            self.state["selection_topology"] = "pressure_field"
            self.state["mutation_operator_mode"] = "operator_discovery"
            mutation_event["changes"].append("activate_niche_diversity_dimension")
        elif regime == "diversification":
            dimensions.setdefault("coordination", {"weight": 0.09, "active": True})
            dimensions["evolvability"]["weight"] = min(0.32, dimensions["evolvability"]["weight"] + 0.02)
            self.state["geometry_type"] = "multi_niche_manifold"
            self.state["selection_topology"] = "niche_graph"
            self.state["mutation_operator_mode"] = "recombination_expansion"
            mutation_event["changes"].append("activate_coordination_dimension")
        elif regime == "collapse_reset":
            dimensions["cost"]["active"] = True
            dimensions["safety"]["weight"] = min(0.35, dimensions["safety"]["weight"] + 0.03)
            self.state["geometry_type"] = "stability_basin"
            self.state["selection_topology"] = "competition_field"
            self.state["mutation_operator_mode"] = "conservative_repair"
            mutation_event["changes"].append("stabilize_safety_cost_space")
        else:
            dimensions["technical"]["weight"] = min(0.30, dimensions["technical"]["weight"] + 0.01)
            self.state["geometry_type"] = "weighted_manifold"
            self.state["selection_topology"] = "graph_competition"
            self.state["mutation_operator_mode"] = "local_refinement"
            mutation_event["changes"].append("tighten_technical_gradient")

        self.state["version"] += 1
        self.state["space_id"] = f"evolution_space_v0_4_g{generation_index:03d}_{regime}"
        self.state["history"].append(mutation_event)
        return mutation_event

