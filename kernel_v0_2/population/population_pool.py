"""Population expansion and reconfiguration for SAEE Kernel v0.2."""

from __future__ import annotations

import copy
from typing import Any


class PopulationPool:
    """Manage multiple coexisting genomes across generations."""

    def from_seed(self, seed_genome: dict[str, Any], initial_size: int = 3) -> list[dict[str, Any]]:
        if initial_size < 2:
            raise ValueError("initial_size must be >= 2 for v0.2 population mode")

        root = self._prepare_genome(copy.deepcopy(seed_genome), status="active")
        root["selection_events"].append(
            {
                "generation_id": 0,
                "event": "founder",
                "reason": "seed genome used to initialize population",
            }
        )
        population = [root]

        initial_mutations = ["prompt_shift", "workflow_reorder", "fitness_adjustment"]
        for index in range(1, initial_size):
            child = copy.deepcopy(root)
            mutation = initial_mutations[(index - 1) % len(initial_mutations)]
            child["id"] = f"{root['id']}_p0_b{index}"
            child["parents"] = [root["id"]]
            child["mutation_history"] = [
                {
                    "generation_id": 0,
                    "mutation": mutation,
                    "source": "initial_population_expansion",
                }
            ]
            self._add_mutation_scope(child, mutation)
            population.append(child)

        return population

    def expand(
        self,
        population: list[dict[str, Any]],
        environment_state: dict[str, Any],
        generation_id: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        active = [copy.deepcopy(genome) for genome in population if genome.get("status") == "active"]
        candidates = [copy.deepcopy(genome) for genome in population if genome.get("status") != "extinct"]
        branch_events: list[dict[str, Any]] = []

        for index, parent in enumerate(active):
            mutation = self._mutation_for_environment(environment_state, index)
            child = copy.deepcopy(parent)
            child["id"] = f"{parent['id']}_g{generation_id}_m{index}"
            child["version"] = int(parent.get("version", 0)) + 1
            child["parents"] = [parent["id"]]
            child["status"] = "active"
            child["selection_events"] = []
            child.setdefault("mutation_history", [])
            child["mutation_history"].append(
                {
                    "generation_id": generation_id,
                    "mutation": mutation,
                    "source": environment_state["environment_id"],
                }
            )
            self._add_mutation_scope(child, mutation)
            child["sandbox_evaluation"] = self._sandbox_evaluate(child)
            candidates.append(child)
            branch_events.append(
                {
                    "event": "mutation",
                    "generation_id": generation_id,
                    "parents": [parent["id"]],
                    "child": child["id"],
                    "mutation": mutation,
                }
            )

        if len(active) >= 2:
            for index in range(len(active) - 1):
                left = active[index]
                right = active[index + 1]
                child = self._recombine(left, right, environment_state, generation_id, index)
                candidates.append(child)
                branch_events.append(
                    {
                        "event": "recombination",
                        "generation_id": generation_id,
                        "parents": child["parents"],
                        "child": child["id"],
                        "mutation": "cross_lineage_recombination",
                    }
                )

        return candidates, branch_events

    def reconfigure(
        self,
        decision: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        next_population: dict[str, dict[str, Any]] = {}
        for status, key in (
            ("active", "survival_set"),
            ("dormant", "dormant_set"),
            ("active", "revival_set"),
        ):
            for genome in decision.get(key, []):
                updated = copy.deepcopy(genome)
                updated["status"] = status
                next_population[updated["id"]] = updated
        return sorted(next_population.values(), key=lambda genome: genome["id"])

    def _prepare_genome(self, genome: dict[str, Any], status: str) -> dict[str, Any]:
        genome.setdefault("parents", [])
        genome.setdefault("mutation_history", [])
        genome.setdefault("selection_events", [])
        genome["status"] = status
        return genome

    def _add_mutation_scope(self, genome: dict[str, Any], mutation: str) -> None:
        scope = genome["traits"].setdefault("mutation_scope", [])
        if mutation not in scope:
            scope.append(mutation)

    def _mutation_for_environment(self, environment_state: dict[str, Any], index: int) -> str:
        dominant = environment_state.get("dominant_pressures", [])
        pressure = dominant[index % len(dominant)] if dominant else "baseline"
        mapping = {
            "repo_growth": "workflow_reorder",
            "issue_cluster": "feedback_loop_tuning",
            "regulation_shift": "safety_constraint_tuning",
            "enterprise_adoption": "niche_shift",
            "past_failure": "rollback_bias",
            "paper_trend": "framework_trait_absorption",
        }
        return mapping.get(pressure, "mutation_pressure_tuning")

    def _recombine(
        self,
        left: dict[str, Any],
        right: dict[str, Any],
        environment_state: dict[str, Any],
        generation_id: int,
        index: int,
    ) -> dict[str, Any]:
        child = copy.deepcopy(left)
        child["id"] = f"{left['id']}_x_{right['id']}_g{generation_id}_r{index}"
        child["version"] = max(int(left.get("version", 0)), int(right.get("version", 0))) + 1
        child["parents"] = [left["id"], right["id"]]
        child["status"] = "active"
        child["selection_events"] = []
        child["traits"]["sensing"] = sorted(
            set(left["traits"].get("sensing", [])) | set(right["traits"].get("sensing", []))
        )
        child["traits"]["mutation_scope"] = sorted(
            set(left["traits"].get("mutation_scope", []))
            | set(right["traits"].get("mutation_scope", []))
            | {"cross_lineage_recombination"}
        )
        child["mutation_history"] = [
            *left.get("mutation_history", []),
            *right.get("mutation_history", []),
            {
                "generation_id": generation_id,
                "mutation": "cross_lineage_recombination",
                "source": environment_state["environment_id"],
            },
        ]
        child["sandbox_evaluation"] = self._sandbox_evaluate(child)
        return child

    def _sandbox_evaluate(self, genome: dict[str, Any]) -> dict[str, Any]:
        constraints = set(genome["traits"].get("constraints", []))
        valid = {
            "no_permission_escalation",
            "no_external_code_execution",
        }.issubset(constraints)
        return {
            "valid": valid,
            "mode": "local_static_sandbox_check",
            "external_execution": False,
            "reason": "required safety constraints present" if valid else "missing required safety constraints",
        }

