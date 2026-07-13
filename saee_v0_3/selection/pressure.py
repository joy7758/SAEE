"""Selection pressure and survival-state resolution for SAEE v0.3."""

from __future__ import annotations

import copy
from typing import Any


class V03SelectionPressure:
    """Resolve population survival under active rule genome thresholds."""

    def resolve(
        self,
        scored: list[dict[str, Any]],
        environment: dict[str, Any],
        previous_population: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        ranked = sorted(scored, key=lambda item: (item["fitness"]["total"], item["genome"]["id"]), reverse=True)
        capacity = int(environment["carrying_capacity"])
        extinction_threshold = float(environment["extinction_threshold"])
        dormancy_threshold = float(environment["dormancy_threshold"])
        survival_records = [
            item
            for item in ranked[:capacity]
            if item["fitness"]["total"] >= extinction_threshold
        ]
        survivor_ids = {item["genome"]["id"] for item in survival_records}
        dormant_records = [
            item
            for item in ranked
            if item["genome"]["id"] not in survivor_ids and item["fitness"]["total"] >= dormancy_threshold
        ][:2]
        dormant_ids = {item["genome"]["id"] for item in dormant_records}
        extinct_records = [
            item
            for item in ranked
            if item["genome"]["id"] not in survivor_ids | dormant_ids
        ]
        revived = self._revive(environment, previous_population, survivor_ids)
        return {
            "survival_set": [self._mark(item["genome"], "survival", "active", item["fitness"], environment) for item in survival_records],
            "dormant_set": [self._mark(item["genome"], "dormancy", "dormant", item["fitness"], environment) for item in dormant_records],
            "extinction_set": [self._mark(item["genome"], "extinction", "extinct", item["fitness"], environment) for item in extinct_records],
            "revival_set": revived,
        }

    def _revive(
        self,
        environment: dict[str, Any],
        previous_population: list[dict[str, Any]],
        survivor_ids: set[str],
    ) -> list[dict[str, Any]]:
        if not environment["revival_pressure"]:
            return []
        dormant = [genome for genome in previous_population if genome.get("status") == "dormant" and genome["id"] not in survivor_ids]
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
            }
        )
        return [genome]

    def _mark(
        self,
        genome: dict[str, Any],
        event: str,
        status: str,
        fitness: dict[str, Any],
        environment: dict[str, Any],
    ) -> dict[str, Any]:
        updated = copy.deepcopy(genome)
        updated["status"] = status
        updated["fitness"] = fitness
        updated.setdefault("selection_events", [])
        updated["selection_events"].append(
            {
                "generation_index": environment["generation_index"],
                "event": event,
                "environment_id": environment["environment_id"],
                "fitness_total": fitness["total"],
            }
        )
        return updated

