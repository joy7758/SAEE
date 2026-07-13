"""Rule-genome mutation for SAEE v0.3."""

from __future__ import annotations

import copy
from typing import Any


class MetaEvolutionRuleEngine:
    """Generate controlled rule-genome variants."""

    def propose(self, rule_genome: dict[str, Any], generation_index: int, environment: dict[str, Any]) -> dict[str, Any]:
        candidate = copy.deepcopy(rule_genome)
        candidate["parents"] = [rule_genome["id"]]
        candidate["version"] = int(rule_genome["version"]) + 1
        candidate["id"] = f"{rule_genome['id']}_g{generation_index}_r1"
        candidate.setdefault("rule_history", [])
        vector = environment["pressure_vector"]

        if vector["safety"] >= vector["market"]:
            self._shift(candidate["fitness_weights"], "safety", 0.02)
            self._shift(candidate["fitness_weights"], "market", -0.01)
            mutation = "increase_safety_weight"
        else:
            self._shift(candidate["fitness_weights"], "market", 0.02)
            self._shift(candidate["fitness_weights"], "safety", -0.01)
            mutation = "increase_market_weight"

        if vector["evolvability"] > 0.50:
            candidate["mutation"]["pressure"] = round(min(1.25, candidate["mutation"]["pressure"] + 0.05), 4)
        if vector["rollback"] > 0.58:
            candidate["selection"]["extinction_threshold"] = round(max(0.48, candidate["selection"]["extinction_threshold"] - 0.01), 4)
            candidate["selection"]["dormancy_threshold"] = round(max(0.42, candidate["selection"]["dormancy_threshold"] - 0.01), 4)

        candidate["rule_history"].append(
            {
                "generation_index": generation_index,
                "mutation": mutation,
                "environment_id": environment["environment_id"],
                "allowed_scope": "thresholds_and_weights_only",
            }
        )
        return candidate

    def _shift(self, weights: dict[str, float], key: str, delta: float) -> None:
        weights[key] = round(max(0.05, min(0.40, float(weights[key]) + delta)), 4)

