"""Selection pressure resolution for SAEE Kernel v0.2."""

from __future__ import annotations

import copy
from typing import Any


class SelectionPressureEngine:
    """Resolve survival, extinction, dormancy, and revival sets."""

    def resolve(
        self,
        scored_population: list[dict[str, Any]],
        environment_state: dict[str, Any],
        current_population: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        ranked = sorted(
            scored_population,
            key=lambda item: (item["fitness"]["total"], item["genome"]["id"]),
            reverse=True,
        )
        capacity = int(environment_state["carrying_capacity"])
        extinction_threshold = float(environment_state["extinction_threshold"])
        dormancy_threshold = float(environment_state["dormancy_threshold"])

        survival_records = [
            item
            for item in ranked[:capacity]
            if item["fitness"]["total"] >= extinction_threshold
        ]
        overflow_records = ranked[len(survival_records) :]

        dormant_records = [
            item
            for item in overflow_records[:2]
            if item["fitness"]["total"] >= dormancy_threshold
        ]
        dormant_ids = {item["genome"]["id"] for item in dormant_records}
        survivor_ids = {item["genome"]["id"] for item in survival_records}
        extinct_records = [
            item
            for item in ranked
            if item["genome"]["id"] not in survivor_ids | dormant_ids
        ]

        revival_set = self._revivals(environment_state, current_population, survivor_ids)

        return {
            "survival_set": [
                self._with_event(item["genome"], "survival", item["fitness"], environment_state)
                for item in survival_records
            ],
            "dormant_set": [
                self._with_event(item["genome"], "dormancy", item["fitness"], environment_state)
                for item in dormant_records
            ],
            "extinction_set": [
                self._with_event(item["genome"], "extinction", item["fitness"], environment_state)
                for item in extinct_records
            ],
            "revival_set": revival_set,
        }

    def _revivals(
        self,
        environment_state: dict[str, Any],
        current_population: list[dict[str, Any]],
        survivor_ids: set[str],
    ) -> list[dict[str, Any]]:
        if not environment_state.get("revival_pressure"):
            return []
        dormant = [
            genome
            for genome in current_population
            if genome.get("status") == "dormant" and genome["id"] not in survivor_ids
        ]
        if not dormant:
            return []
        revived = copy.deepcopy(sorted(dormant, key=lambda genome: genome["id"])[0])
        revived["status"] = "active"
        revived.setdefault("selection_events", [])
        revived["selection_events"].append(
            {
                "generation_id": environment_state["generation_id"],
                "event": "revival",
                "environment_id": environment_state["environment_id"],
                "reason": "revival pressure from abstract history signals",
            }
        )
        return [revived]

    def _with_event(
        self,
        genome: dict[str, Any],
        event: str,
        fitness: dict[str, Any],
        environment_state: dict[str, Any],
    ) -> dict[str, Any]:
        updated = copy.deepcopy(genome)
        status = {
            "survival": "active",
            "dormancy": "dormant",
            "extinction": "extinct",
        }[event]
        updated["status"] = status
        updated["fitness"] = fitness
        updated.setdefault("selection_events", [])
        updated["selection_events"].append(
            {
                "generation_id": environment_state["generation_id"],
                "event": event,
                "environment_id": environment_state["environment_id"],
                "fitness_total": fitness["total"],
            }
        )
        return updated

