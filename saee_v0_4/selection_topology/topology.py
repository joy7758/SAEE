"""Mutable selection topology for SAEE v0.4."""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import Any


class SelectionTopologyEngine:
    """Resolve survival through topology, not a fixed ranking model."""

    def resolve(
        self,
        projections: list[dict[str, Any]],
        environment: dict[str, Any],
        evolution_space: dict[str, Any],
        previous_population: list[dict[str, Any]],
    ) -> dict[str, Any]:
        topology = evolution_space.get("selection_topology", "niche_field")
        annotated = [self._annotate(item, topology, environment) for item in projections]
        capacity = int(environment.get("carrying_capacity", 6))
        dormancy_limit = int(environment.get("dormancy_limit", 3))

        if topology == "niche_graph":
            survivors = self._niche_representatives(annotated, capacity)
        elif topology == "pressure_field":
            survivors = self._pressure_field(annotated, capacity)
        elif topology == "competition_field":
            survivors = self._competition_field(annotated, max(3, capacity - 1))
        elif topology == "graph_competition":
            survivors = self._graph_competition(annotated, capacity)
        else:
            survivors = self._niche_representatives(annotated, capacity)

        survivor_ids = {item["genome"]["id"] for item in survivors}
        dormancy_candidates = [
            item
            for item in sorted(annotated, key=self._rank_key, reverse=True)
            if item["genome"]["id"] not in survivor_ids
            and item["topology_score"] >= environment.get("dormancy_threshold", 0.35)
        ][:dormancy_limit]
        dormant_ids = {item["genome"]["id"] for item in dormancy_candidates}
        extinct = [
            item
            for item in annotated
            if item["genome"]["id"] not in survivor_ids | dormant_ids
        ]
        revival = self._revive(previous_population, environment, survivor_ids)

        return {
            "topology_type": topology,
            "survival_set": [
                self._mark(item, "survival", "active", environment, topology)
                for item in survivors
            ],
            "dormant_set": [
                self._mark(item, "dormancy", "dormant", environment, topology)
                for item in dormancy_candidates
            ],
            "extinction_set": [
                self._mark(item, "extinction", "extinct", environment, topology)
                for item in extinct
            ],
            "revival_set": revival,
            "niche_map": self._niche_map(annotated),
            "pressure_summary": {
                "capacity": capacity,
                "dormancy_limit": dormancy_limit,
                "environment_id": environment["environment_id"],
            },
        }

    def _annotate(
        self,
        item: dict[str, Any],
        topology: str,
        environment: dict[str, Any],
    ) -> dict[str, Any]:
        annotated = copy.deepcopy(item)
        geometry = annotated["fitness_geometry"]
        score = float(geometry["geometry_score"])
        coordinates = geometry["coordinates"]
        if topology == "pressure_field":
            score += coordinates.get(environment["dominant_dimension"], 0.0) * 0.12
        elif topology == "competition_field":
            score -= geometry.get("lineage_competition", 0.0) * 0.16
            score += coordinates.get("safety", 0.0) * 0.07
        elif topology == "niche_graph":
            score += coordinates.get("niche_diversity", 0.0) * 0.10
            if "recombination" in annotated["genome"]["traits"].get("mutation_scope", []):
                score += 0.04
        elif topology == "graph_competition":
            score -= geometry.get("lineage_competition", 0.0) * 0.10
            score += coordinates.get("technical", 0.0) * 0.05
        annotated["topology_score"] = round(max(0.0, min(1.0, score)), 6)
        return annotated

    def _niche_representatives(self, annotated: list[dict[str, Any]], capacity: int) -> list[dict[str, Any]]:
        by_niche: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in annotated:
            by_niche[item["fitness_geometry"]["niche"]].append(item)
        survivors: list[dict[str, Any]] = []
        for niche in sorted(by_niche):
            survivors.append(sorted(by_niche[niche], key=self._rank_key, reverse=True)[0])
            if len(survivors) >= capacity:
                return survivors
        survivor_ids = {item["genome"]["id"] for item in survivors}
        for item in sorted(annotated, key=self._rank_key, reverse=True):
            if item["genome"]["id"] not in survivor_ids:
                survivors.append(item)
                survivor_ids.add(item["genome"]["id"])
            if len(survivors) >= capacity:
                break
        return survivors

    def _pressure_field(self, annotated: list[dict[str, Any]], capacity: int) -> list[dict[str, Any]]:
        return sorted(annotated, key=self._rank_key, reverse=True)[:capacity]

    def _competition_field(self, annotated: list[dict[str, Any]], capacity: int) -> list[dict[str, Any]]:
        threshold = 0.42
        ranked = [item for item in sorted(annotated, key=self._rank_key, reverse=True) if item["topology_score"] >= threshold]
        return ranked[:capacity] or sorted(annotated, key=self._rank_key, reverse=True)[:3]

    def _graph_competition(self, annotated: list[dict[str, Any]], capacity: int) -> list[dict[str, Any]]:
        by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in annotated:
            parents = item["genome"].get("parents", ["founder"]) or ["founder"]
            by_parent[parents[0]].append(item)
        survivors: list[dict[str, Any]] = []
        for parent in sorted(by_parent):
            survivors.extend(sorted(by_parent[parent], key=self._rank_key, reverse=True)[:2])
        return sorted(survivors, key=self._rank_key, reverse=True)[:capacity]

    def _revive(
        self,
        previous_population: list[dict[str, Any]],
        environment: dict[str, Any],
        survivor_ids: set[str],
    ) -> list[dict[str, Any]]:
        if not environment.get("revival_pressure", False):
            return []
        dormant = [
            genome
            for genome in previous_population
            if genome.get("status") == "dormant" and genome["id"] not in survivor_ids
        ]
        if not dormant:
            return []
        genome = copy.deepcopy(sorted(dormant, key=lambda item: item["id"])[0])
        genome["status"] = "active"
        genome.setdefault("selection_events", [])
        genome["selection_events"].append(
            {
                "generation_index": environment["generation_index"],
                "event": "revival",
                "environment_id": environment["environment_id"],
                "topology_type": "revival_from_dormancy",
            }
        )
        return [genome]

    def _mark(
        self,
        item: dict[str, Any],
        event: str,
        status: str,
        environment: dict[str, Any],
        topology: str,
    ) -> dict[str, Any]:
        genome = copy.deepcopy(item["genome"])
        genome["status"] = status
        genome["fitness"] = {
            "geometry_score": item["fitness_geometry"]["geometry_score"],
            "topology_score": item["topology_score"],
            "niche": item["fitness_geometry"]["niche"],
            "geometry_type": item["fitness_geometry"]["geometry_type"],
            "selection_topology": topology,
        }
        genome.setdefault("selection_events", [])
        genome["selection_events"].append(
            {
                "generation_index": environment["generation_index"],
                "event": event,
                "environment_id": environment["environment_id"],
                "selection_topology": topology,
                "topology_score": item["topology_score"],
            }
        )
        return genome

    def _niche_map(self, annotated: list[dict[str, Any]]) -> dict[str, list[str]]:
        niches: dict[str, list[str]] = defaultdict(list)
        for item in annotated:
            niches[item["fitness_geometry"]["niche"]].append(item["genome"]["id"])
        return {niche: sorted(ids) for niche, ids in sorted(niches.items())}

    def _rank_key(self, item: dict[str, Any]) -> tuple[float, float, str]:
        return (
            float(item["topology_score"]),
            float(item["fitness_geometry"]["geometry_score"]),
            item["genome"]["id"],
        )
