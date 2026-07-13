"""Selection for the SAEE v1.0 stable runtime."""

from __future__ import annotations

import copy
from typing import Any


def select_population(evaluated: list[dict[str, Any]], population_size: int, generation_index: int) -> dict[str, Any]:
    """Select the next single population pool."""

    ranked = sorted(evaluated, key=lambda item: (float(item["score"]), item["genome"]["id"]), reverse=True)
    survivors = []
    rejected = []
    for index, item in enumerate(ranked):
        genome = copy.deepcopy(item["genome"])
        genome["fitness_score"] = item["score"]
        genome["status"] = "active" if index < population_size else "rejected"
        genome.setdefault("selection_history", [])
        genome["selection_history"].append(
            {
                "generation_index": generation_index,
                "event": "selected" if index < population_size else "rejected",
                "fitness_score": item["score"],
                "selection_model": "ranked_single_pool_selection",
            }
        )
        if index < population_size:
            survivors.append(genome)
        else:
            rejected.append(genome)
    return {
        "survivors": sorted(survivors, key=lambda genome: genome["id"]),
        "rejected": sorted(rejected, key=lambda genome: genome["id"]),
        "selection_model": "ranked_single_pool_selection",
    }

