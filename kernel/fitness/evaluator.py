"""Weighted local fitness evaluation for SAEE kernel v0.1."""

from __future__ import annotations

from typing import Any


class FitnessEvaluator:
    """Evaluate one genome against deterministic mock signals."""

    def evaluate(self, genome: dict[str, Any], signals: dict[str, Any]) -> dict[str, float]:
        weights = genome["traits"].get("fitness_weights", {})
        mutation_scope = genome["traits"].get("mutation_scope", [])
        constraints = set(genome["traits"].get("constraints", []))

        components = {
            "technical": 1.0 if "repo_growth_pattern" in signals.get("github_signals", []) else 0.4,
            "market": 1.0 if "enterprise_adoption" in signals.get("news_signals", []) else 0.4,
            "safety": 1.0
            if {
                "no_permission_escalation",
                "no_external_code_execution",
            }.issubset(constraints)
            else 0.2,
            "cost": 0.8,
            "novelty": min(1.0, 0.2 + (0.1 * len(set(mutation_scope)))),
            "evolvability": 1.0 if len(mutation_scope) > 0 else 0.3,
        }

        total = 0.0
        total_weight = 0.0
        for key, value in components.items():
            weight = float(weights.get(key, 0.0))
            total += value * weight
            total_weight += weight

        if total_weight == 0:
            total = sum(components.values()) / len(components)
        else:
            total = total / total_weight

        return {**components, "total": round(total, 6)}

