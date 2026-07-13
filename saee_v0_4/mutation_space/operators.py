"""Runtime-extensible mutation operators for SAEE v0.4."""

from __future__ import annotations

import copy
from typing import Any


class MutationOperatorRegistry:
    """Select and mutate operators based on evolution-space mode."""

    BASE_OPERATORS = {
        "trait_shift": "Add or emphasize one trait dimension.",
        "threshold_adjustment": "Adjust safety or survival thresholds.",
        "niche_split": "Split one lineage toward a niche target.",
        "recombination": "Combine two parent lineages.",
    }

    MODE_OPERATORS = {
        "operator_discovery": ["trait_shift", "niche_split", "novel_operator_seed"],
        "recombination_expansion": ["recombination", "niche_split", "cross_niche_bridge"],
        "conservative_repair": ["threshold_adjustment", "stability_repair"],
        "local_refinement": ["trait_shift", "threshold_adjustment"],
        "baseline": ["trait_shift", "recombination"],
    }

    def active_operators(self, evolution_space: dict[str, Any]) -> list[str]:
        mode = evolution_space.get("mutation_operator_mode", "baseline")
        return list(self.MODE_OPERATORS.get(mode, self.MODE_OPERATORS["baseline"]))

    def mutate_population(
        self,
        population: list[dict[str, Any]],
        evolution_space: dict[str, Any],
        generation_index: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        operators = self.active_operators(evolution_space)
        active = [genome for genome in population if genome.get("status") == "active"]
        candidates = [copy.deepcopy(genome) for genome in population if genome.get("status") != "extinct"]
        events: list[dict[str, Any]] = []

        for index, parent in enumerate(active):
            operator = operators[index % len(operators)]
            child = copy.deepcopy(parent)
            child["id"] = f"{parent['id']}_v04_g{generation_index}_{operator}_{index}"
            child["parents"] = [parent["id"]]
            child["version"] = int(parent.get("version", 0)) + 1
            child["status"] = "active"
            child["selection_events"] = []
            child.setdefault("mutation_history", [])
            child["mutation_history"].append(
                {
                    "generation_index": generation_index,
                    "operator": operator,
                    "evolution_space_id": evolution_space["space_id"],
                }
            )
            scope = child["traits"].setdefault("mutation_scope", [])
            if operator not in scope:
                scope.append(operator)
            if operator in {"niche_split", "cross_niche_bridge", "novel_operator_seed"}:
                child["traits"]["niche_target"] = f"{child['traits'].get('niche_target', 'general')}_{operator}"
            candidates.append(child)
            events.append(
                {
                    "event_type": "operator_mutation",
                    "generation_index": generation_index,
                    "operator": operator,
                    "parents": [parent["id"]],
                    "child": child["id"],
                }
            )

        if "recombination" in operators and len(active) >= 2:
            left, right = active[0], active[-1]
            child = copy.deepcopy(left)
            child["id"] = f"{left['id']}_X_{right['id']}_v04_g{generation_index}"
            child["parents"] = [left["id"], right["id"]]
            child["version"] = max(int(left.get("version", 0)), int(right.get("version", 0))) + 1
            child["status"] = "active"
            child["selection_events"] = []
            child["traits"]["mutation_scope"] = sorted(
                set(left["traits"].get("mutation_scope", []))
                | set(right["traits"].get("mutation_scope", []))
                | {"recombination"}
            )
            child.setdefault("mutation_history", [])
            child["mutation_history"].append(
                {
                    "generation_index": generation_index,
                    "operator": "recombination",
                    "evolution_space_id": evolution_space["space_id"],
                }
            )
            candidates.append(child)
            events.append(
                {
                    "event_type": "operator_recombination",
                    "generation_index": generation_index,
                    "operator": "recombination",
                    "parents": child["parents"],
                    "child": child["id"],
                }
            )

        return candidates, events

