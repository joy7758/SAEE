"""Discover attractor states from behavior trajectories."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


class AttractorDiscoveryEngine:
    """Detect recurring state signatures in observed evolution behavior."""

    def discover(self, behavior: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
        signatures: list[dict[str, Any]] = []
        for point in behavior["trajectory"]:
            signature = self._signature(point)
            signatures.append(
                {
                    "generation_index": point["generation_index"],
                    "state_signature": signature,
                    "population_count": point["population_count"],
                    "mean_identity_score": point["mean_identity_score"],
                    "semantic_drift_after": point["semantic_drift_after"],
                }
            )
        counts = Counter(item["state_signature"] for item in signatures)
        basins: dict[str, list[int]] = defaultdict(list)
        for item in signatures:
            basins[item["state_signature"]].append(item["generation_index"])
        attractors = []
        for signature, count in counts.most_common():
            if count < 2:
                continue
            attractors.append(
                {
                    "attractor_id": f"attractor_{len(attractors) + 1:03d}",
                    "state_signature": signature,
                    "support_count": count,
                    "support_generations": basins[signature],
                    "attractor_type": "identity_stable_reflexive_attractor"
                    if "identity:stable" in signature
                    else "transient_behavioral_attractor",
                }
            )
        if not attractors and signatures:
            attractors.append(
                {
                    "attractor_id": "attractor_001",
                    "state_signature": signatures[-1]["state_signature"],
                    "support_count": 1,
                    "support_generations": [signatures[-1]["generation_index"]],
                    "attractor_type": "single_observed_terminal_state",
                }
            )
        return {
            "analysis_type": "attractor_discovery",
            "state_signatures": signatures,
            "attractors": attractors,
            "convergence_basins": [
                {
                    "state_signature": signature,
                    "generations": generations,
                    "basin_size": len(generations),
                }
                for signature, generations in sorted(basins.items())
            ],
            "identity_anchor_hash_count": record["stability_summary"]["identity_anchor_hash_count"],
        }

    def _signature(self, point: dict[str, Any]) -> str:
        identity = "stable" if point["identity_break_count"] == 0 and point["mean_identity_score"] >= 0.58 else "fragile"
        drift = "bounded" if point["semantic_drift_after"] <= 0.32 else "unbounded"
        population = "dense" if point["population_count"] >= 10 else "sparse"
        mutation = "active" if point["explanation_driven_mutation_count"] > 0 else "quiet"
        return f"identity:{identity}|drift:{drift}|population:{population}|mutation:{mutation}"

