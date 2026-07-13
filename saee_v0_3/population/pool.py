"""Population pool for SAEE v0.3."""

from __future__ import annotations

import copy
from typing import Any

from saee_v0_3.genome.contracts import normalize_genome, safety_valid


class PopulationPoolV03:
    """Maintain active and dormant genomes without collapsing to one lineage."""

    def initialize(self, seed_genome: dict[str, Any], size: int = 4) -> list[dict[str, Any]]:
        if size < 3:
            raise ValueError("v0.3 population size must be >= 3")
        founder = normalize_genome(seed_genome)
        founder["selection_events"].append({"generation_index": 0, "event": "founder"})
        population = [founder]
        for index, mutation in enumerate(["prompt_shift", "workflow_reorder", "fitness_adjustment"], start=1):
            child = normalize_genome(founder)
            child["id"] = f"{founder['id']}_v03_p0_b{index}"
            child["parents"] = [founder["id"]]
            child["mutation_history"] = [
                {
                    "generation_index": 0,
                    "mutation": mutation,
                    "source": "v0_3_initial_population",
                }
            ]
            self._add_scope(child, mutation)
            population.append(child)
            if len(population) == size:
                break
        return population

    def expand(
        self,
        population: list[dict[str, Any]],
        environment: dict[str, Any],
        rule_genome: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        generation_index = int(environment["generation_index"])
        active = [genome for genome in population if genome.get("status") == "active"]
        candidates = [copy.deepcopy(genome) for genome in population if genome.get("status") != "extinct"]
        events: list[dict[str, Any]] = []
        mutation_pressure = float(rule_genome["mutation"]["pressure"])

        for index, parent in enumerate(active):
            mutation = self._mutation_for(environment, index, mutation_pressure)
            child = copy.deepcopy(parent)
            child["id"] = f"{parent['id']}_v03_g{generation_index}_m{index}"
            child["version"] = int(parent.get("version", 0)) + 1
            child["parents"] = [parent["id"]]
            child["status"] = "active"
            child["selection_events"] = []
            child.setdefault("mutation_history", [])
            child["mutation_history"].append(
                {
                    "generation_index": generation_index,
                    "mutation": mutation,
                    "source": environment["environment_id"],
                    "rule_genome": rule_genome["id"],
                }
            )
            child["sandbox_evaluation"] = self._sandbox(child)
            self._add_scope(child, mutation)
            candidates.append(child)
            events.append(
                {
                    "event_type": "mutation",
                    "generation_index": generation_index,
                    "parents": [parent["id"]],
                    "child": child["id"],
                    "mutation": mutation,
                }
            )

        if rule_genome["mutation"].get("recombination_enabled", True) and len(active) >= 2:
            for index in range(len(active) - 1):
                left = active[index]
                right = active[index + 1]
                child = self._recombine(left, right, environment, rule_genome, index)
                candidates.append(child)
                events.append(
                    {
                        "event_type": "recombination",
                        "generation_index": generation_index,
                        "parents": child["parents"],
                        "child": child["id"],
                        "mutation": "meta_guarded_recombination",
                    }
                )

        return candidates, events

    def reconfigure(self, decision: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        retained: dict[str, dict[str, Any]] = {}
        for status, key in (
            ("active", "survival_set"),
            ("dormant", "dormant_set"),
            ("active", "revival_set"),
        ):
            for genome in decision[key]:
                updated = copy.deepcopy(genome)
                updated["status"] = status
                retained[updated["id"]] = updated
        return sorted(retained.values(), key=lambda genome: genome["id"])

    def _mutation_for(self, environment: dict[str, Any], index: int, mutation_pressure: float) -> str:
        dominant = environment.get("dominant_pressures", ["baseline"])
        pressure = dominant[index % len(dominant)]
        mapping = {
            "repo_growth": "workflow_reorder",
            "pr_pattern": "coordination_trait",
            "regulation_shift": "safety_constraint_tuning",
            "market_pull": "niche_shift",
            "past_failure": "rollback_bias",
            "framework_trend": "framework_trait_absorption",
        }
        mutation = mapping.get(pressure, "baseline_variation")
        return f"{mutation}_p{mutation_pressure:.2f}"

    def _recombine(
        self,
        left: dict[str, Any],
        right: dict[str, Any],
        environment: dict[str, Any],
        rule_genome: dict[str, Any],
        index: int,
    ) -> dict[str, Any]:
        child = copy.deepcopy(left)
        generation_index = int(environment["generation_index"])
        child["id"] = f"{left['id']}_X_{right['id']}_v03_g{generation_index}_r{index}"
        child["version"] = max(int(left.get("version", 0)), int(right.get("version", 0))) + 1
        child["parents"] = [left["id"], right["id"]]
        child["status"] = "active"
        child["selection_events"] = []
        child["traits"]["sensing"] = sorted(set(left["traits"].get("sensing", [])) | set(right["traits"].get("sensing", [])))
        child["traits"]["mutation_scope"] = sorted(
            set(left["traits"].get("mutation_scope", []))
            | set(right["traits"].get("mutation_scope", []))
            | {"meta_guarded_recombination"}
        )
        child["mutation_history"] = [
            *left.get("mutation_history", []),
            *right.get("mutation_history", []),
            {
                "generation_index": generation_index,
                "mutation": "meta_guarded_recombination",
                "source": environment["environment_id"],
                "rule_genome": rule_genome["id"],
            },
        ]
        child["sandbox_evaluation"] = self._sandbox(child)
        return child

    def _sandbox(self, genome: dict[str, Any]) -> dict[str, Any]:
        return {
            "valid": safety_valid(genome),
            "mode": "local_static_sandbox_check",
            "external_execution": False,
        }

    def _add_scope(self, genome: dict[str, Any], mutation: str) -> None:
        scope = genome["traits"].setdefault("mutation_scope", [])
        if mutation not in scope:
            scope.append(mutation)

