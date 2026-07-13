"""Counterfactual rule trials for SAEE v0.3."""

from __future__ import annotations

from typing import Any


class CounterfactualRuleSimulator:
    """Evaluate candidate rule genomes before adoption."""

    def compare(
        self,
        baseline_record: dict[str, Any],
        candidate_record: dict[str, Any],
    ) -> dict[str, Any]:
        baseline = self._summary(baseline_record)
        candidate = self._summary(candidate_record)
        delta = {
            "average_fitness_delta": round(candidate["average_fitness"] - baseline["average_fitness"], 6),
            "population_size_delta": candidate["population_size"] - baseline["population_size"],
            "extinction_delta": candidate["extinction_count"] - baseline["extinction_count"],
            "dormancy_delta": candidate["dormancy_count"] - baseline["dormancy_count"],
            "lineage_edge_delta": candidate["lineage_edges"] - baseline["lineage_edges"],
        }
        adopted = (
            delta["average_fitness_delta"] >= -0.02
            and candidate["population_size"] >= 3
            and candidate["lineage_edges"] >= baseline["lineage_edges"]
            and candidate["signal_mode"] == "abstract_local"
        )
        return {
            "baseline": baseline,
            "candidate": candidate,
            "delta": delta,
            "adopt_candidate": adopted,
            "reason": "candidate preserves guarded ecology" if adopted else "candidate failed guarded counterfactual trial",
        }

    def _summary(self, record: dict[str, Any]) -> dict[str, Any]:
        cycles = record["cycles"]
        final_cycle = cycles[-1]
        all_scores = [
            score["fitness"]["total"]
            for cycle in cycles
            for score in cycle["fitness_scores"]
        ]
        return {
            "average_fitness": round(sum(all_scores) / len(all_scores), 6) if all_scores else 0.0,
            "population_size": len(record["population"]),
            "extinction_count": sum(len(cycle["selection_pressure"]["extinction_set"]) for cycle in cycles),
            "dormancy_count": sum(len(cycle["selection_pressure"]["dormant_set"]) for cycle in cycles),
            "lineage_edges": len(record["lineage_graph"]["edges"]),
            "signal_mode": final_cycle["environment_state"]["signal_mode"],
        }

