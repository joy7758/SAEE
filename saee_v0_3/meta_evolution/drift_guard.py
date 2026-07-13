"""Drift guard constraints for SAEE v0.3 meta-evolution."""

from __future__ import annotations

from typing import Any


class DriftGuard:
    """Reject rule mutations that break SAEE invariants."""

    REQUIRED_GUARDS = {
        "preserve_lineage_dag",
        "preserve_genome_schema",
        "preserve_fitness_vector",
        "preserve_abstract_sensing",
        "preserve_population_mode",
    }

    def validate(self, record: dict[str, Any], rule_genome: dict[str, Any]) -> dict[str, Any]:
        checks = {
            "population_based": len(record.get("population", [])) >= 3,
            "lineage_graph": bool(record.get("lineage_graph", {}).get("edges")),
            "rule_graph": bool(record.get("lineage_graph", {}).get("rule_graph", {}).get("nodes")),
            "abstract_sensing": all(
                cycle["environment_state"]["signal_mode"] == "abstract_local"
                for cycle in record.get("cycles", [])
            ),
            "fitness_vector": self._fitness_has_components(record),
            "allowed_rule_scope": set(rule_genome.get("guards", [])) >= self.REQUIRED_GUARDS,
            "no_external_execution": "no_external_repo_execution" in record.get("boundaries", []),
        }
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "guarded_invariants": sorted(self.REQUIRED_GUARDS),
        }

    def _fitness_has_components(self, record: dict[str, Any]) -> bool:
        for cycle in record.get("cycles", []):
            for score in cycle.get("fitness_scores", []):
                components = score.get("fitness", {}).get("components", {})
                if not {"technical", "market", "safety", "cost", "novelty", "evolvability"}.issubset(components):
                    return False
        return True

