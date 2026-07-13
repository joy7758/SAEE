"""Passive emergence observation for SAEE v1.0 experiments."""

from __future__ import annotations

from collections import Counter
from typing import Any


class EmergenceObserver:
    """Identify repeated patterns and persistent structures without feedback."""

    def observe(self, trace: list[dict[str, Any]]) -> dict[str, Any]:
        pattern_counts: Counter[str] = Counter()
        lineage_prefix_counts: Counter[str] = Counter()
        persistent_constraints: Counter[str] = Counter()
        for item in trace:
            scores = item["fitness_values"]
            if not scores:
                continue
            selected = item["selection_result"]["selected_ids"]
            mean_score = sum(float(score["score"]) for score in scores) / len(scores)
            pattern = "high_fitness_plateau" if mean_score >= 0.55 else "adaptive_search"
            pattern_counts[pattern] += 1
            for genome in item["population_state"]:
                lineage_prefix = genome["id"].split("_g", 1)[0]
                lineage_prefix_counts[lineage_prefix] += 1
                for constraint in genome.get("traits", {}).get("constraints", []):
                    persistent_constraints[constraint] += 1
            if len(selected) == len(item["population_state"]):
                pattern_counts["full_population_retained"] += 1
        stable_sublineages = [
            {
                "lineage_prefix": prefix,
                "support": count,
            }
            for prefix, count in lineage_prefix_counts.most_common(10)
            if count >= max(3, len(trace) // 10)
        ]
        return {
            "analysis_type": "emergence_observer",
            "repeated_patterns": [
                {
                    "pattern": pattern,
                    "support": count,
                }
                for pattern, count in sorted(pattern_counts.items())
            ],
            "stable_sublineages": stable_sublineages,
            "persistent_genome_structures": [
                {
                    "structure": constraint,
                    "support": count,
                }
                for constraint, count in sorted(persistent_constraints.items())
            ],
            "kernel_influence": False,
            "observation_only": True,
        }

