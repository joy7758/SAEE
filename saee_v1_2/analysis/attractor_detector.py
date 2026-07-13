"""Attractor detection from simulation trajectories."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from saee_v1_2.metrics.attractor_metrics import attractor_convergence_rate, population_centroid


def state_signature(state: dict[str, Any]) -> str:
    centroid = population_centroid(state)
    bins = tuple(round(value, 1) for value in centroid)
    pressure_bin = round(float(state["observer"]["reflexive_pressure"]), 1)
    return f"centroid={bins}|pressure={pressure_bin}"


class AttractorDetectionSystem:
    """Detect stable states and convergence basins."""

    def detect(self, trace: list[dict[str, Any]]) -> dict[str, Any]:
        signatures = [
            {
                "generation": state["generation"],
                "state_signature": state_signature(state),
                "centroid": list(population_centroid(state)),
            }
            for state in trace
        ]
        counts = Counter(item["state_signature"] for item in signatures)
        basins: dict[str, list[int]] = defaultdict(list)
        for item in signatures:
            basins[item["state_signature"]].append(item["generation"])
        attractors = []
        for signature, count in counts.most_common():
            if count >= 3:
                attractors.append(
                    {
                        "attractor_id": f"v12_attractor_{len(attractors) + 1:03d}",
                        "state_signature": signature,
                        "support_count": count,
                        "support_generations": basins[signature],
                    }
                )
        if not attractors and signatures:
            terminal_signature = signatures[-1]["state_signature"]
            attractors.append(
                {
                    "attractor_id": "v12_attractor_001",
                    "state_signature": terminal_signature,
                    "support_count": counts[terminal_signature],
                    "support_generations": basins[terminal_signature],
                }
            )
        convergence = attractor_convergence_rate(trace)
        terminal_rate = convergence[-1]["convergence_rate"] if convergence else 0.0
        return {
            "analysis_type": "attractor_detection",
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
            "phase_stability_regions": [
                {
                    "attractor_id": attractor["attractor_id"],
                    "state_signature": attractor["state_signature"],
                    "region_label": "stable_region" if attractor["support_count"] >= 3 else "weak_region",
                }
                for attractor in attractors
            ],
            "attractor_convergence": convergence,
            "terminal_convergence_rate": terminal_rate,
        }

