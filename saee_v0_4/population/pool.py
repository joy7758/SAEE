"""Population pool for phase-transition evolution space."""

from __future__ import annotations

import copy
from typing import Any


class PopulationPoolV04:
    """Maintain a multi-lineage population across changing evolution spaces."""

    INITIAL_VARIATIONS = [
        "workflow_reorder",
        "niche_split",
        "safety_constraint_tuning",
        "coordination_bridge",
        "evolvability_probe",
    ]

    def initialize(self, seed_genome: dict[str, Any], size: int = 5) -> list[dict[str, Any]]:
        if size < 4:
            raise ValueError("v0.4 population size must be >= 4")
        founder = self._normalize(seed_genome)
        founder["selection_events"].append({"generation_index": 0, "event": "founder"})
        founder["phase_events"] = []
        population = [founder]
        for index, mutation in enumerate(self.INITIAL_VARIATIONS, start=1):
            child = self._normalize(founder)
            child["id"] = f"{founder['id']}_v04_p0_b{index}"
            child["parents"] = [founder["id"]]
            child["version"] = int(founder.get("version", 0)) + 1
            child["mutation_history"] = [
                {
                    "generation_index": 0,
                    "operator": mutation,
                    "source": "v0_4_initial_population",
                }
            ]
            child["selection_events"] = []
            child["phase_events"] = []
            self._add_scope(child, mutation)
            child["sandbox_evaluation"] = self._sandbox(child)
            population.append(child)
            if len(population) == size:
                break
        return population

    def reconfigure(self, decision: dict[str, Any], max_population: int = 12) -> list[dict[str, Any]]:
        """Apply topology decision while preserving dormant lineage memory."""
        retained: dict[str, dict[str, Any]] = {}
        for status, key in (
            ("active", "survival_set"),
            ("dormant", "dormant_set"),
            ("active", "revival_set"),
        ):
            for genome in decision.get(key, []):
                updated = copy.deepcopy(genome)
                updated["status"] = status
                retained[updated["id"]] = updated

        active = sorted(
            [genome for genome in retained.values() if genome.get("status") == "active"],
            key=lambda genome: (genome.get("fitness", {}).get("topology_score", 0.0), genome["id"]),
            reverse=True,
        )[:max_population]
        dormant = sorted(
            [genome for genome in retained.values() if genome.get("status") == "dormant"],
            key=lambda genome: genome["id"],
        )[:3]
        return sorted(active + dormant, key=lambda genome: genome["id"])

    def _normalize(self, genome: dict[str, Any]) -> dict[str, Any]:
        normalized = copy.deepcopy(genome)
        normalized.setdefault("id", "saee_seed")
        normalized.setdefault("version", 0)
        normalized.setdefault("parents", [])
        normalized.setdefault("mutation_history", [])
        normalized.setdefault("selection_events", [])
        normalized.setdefault("traits", {})
        normalized["traits"].setdefault("sensing", ["github", "news", "history", "paper"])
        normalized["traits"].setdefault("mutation_scope", [])
        normalized["traits"].setdefault(
            "constraints",
            ["no_permission_escalation", "no_external_code_execution"],
        )
        normalized["traits"].setdefault("niche_target", "agent_evolution_research")
        normalized.setdefault("status", "active")
        normalized["sandbox_evaluation"] = self._sandbox(normalized)
        return normalized

    def _sandbox(self, genome: dict[str, Any]) -> dict[str, Any]:
        constraints = set(genome["traits"].get("constraints", []))
        return {
            "valid": {
                "no_permission_escalation",
                "no_external_code_execution",
            }.issubset(constraints),
            "mode": "local_phase_transition_contract_check",
            "external_execution": False,
            "permission_expansion": False,
        }

    def _add_scope(self, genome: dict[str, Any], mutation: str) -> None:
        scope = genome["traits"].setdefault("mutation_scope", [])
        if mutation not in scope:
            scope.append(mutation)
