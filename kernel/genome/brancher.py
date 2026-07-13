"""Deterministic genome branching for SAEE kernel v0.1."""

from __future__ import annotations

import copy
from typing import Any

from kernel.config import BRANCH_COUNT, MUTATION_OPTIONS


class GenomeBrancher:
    """Create fixed-count offspring from a parent genome."""

    def branch(self, genome: dict[str, Any], signals: dict[str, Any]) -> list[dict[str, Any]]:
        offspring = []
        parent_id = genome["id"]
        next_version = int(genome.get("version", 0)) + 1

        for index in range(BRANCH_COUNT):
            mutation = MUTATION_OPTIONS[index % len(MUTATION_OPTIONS)]
            child = copy.deepcopy(genome)
            child["id"] = f"{parent_id}_g{next_version}_b{index}"
            child["version"] = next_version
            child["parents"] = [parent_id]
            child.setdefault("mutation_history", [])
            child["mutation_history"].append(
                {
                    "generation": next_version,
                    "branch_index": index,
                    "mutation": mutation,
                    "signal_source": signals.get("source", "unknown"),
                }
            )

            mutation_scope = child["traits"].setdefault("mutation_scope", [])
            if mutation not in mutation_scope:
                mutation_scope.append(mutation)

            offspring.append(child)

        return offspring

