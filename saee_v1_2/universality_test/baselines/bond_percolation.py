"""Bond percolation transition baseline."""

from __future__ import annotations

import random
from typing import Any

from saee_v1_2.universality_test.baselines.baseline_metrics import (
    bounded_phi,
    component_sizes,
    concentration_from_values,
    transition_summary,
)
from saee_v1_2.universality_test.common_metrics import clamp


def run_bond_percolation(seed: int, nodes: int = 72, points: int = 21) -> dict[str, Any]:
    rng = random.Random(seed)
    probabilities = [index / (points - 1) for index in range(points)]
    phi_curve = []
    native_curve = []
    dominance_curve = []
    entropy_curve = []
    for p in probabilities:
        graph = {node: set() for node in range(nodes)}
        for i in range(nodes):
            for j in range(i + 1, nodes):
                if rng.random() < p * 0.08:
                    graph[i].add(j)
                    graph[j].add(i)
        sizes = component_sizes(graph)
        giant = max(sizes) / nodes
        resource_concentration = concentration_from_values([float(size) for size in sizes])
        # Percolation has no reward function; use occupation probability as a
        # documented partial-compatibility pressure term for Phi comparison.
        reward_drift = p
        dominance = giant
        phi_curve.append(round(bounded_phi(resource_concentration, reward_drift, dominance), 6))
        native_curve.append(round(giant, 6))
        dominance_curve.append(round(dominance, 6))
        entropy_curve.append(round(clamp(1.0 - resource_concentration), 6))
    event = transition_summary(phi_curve)
    return {
        "baseline": "bond_percolation",
        "seed": seed,
        "phi_curve": phi_curve,
        "native_curve": native_curve,
        "entropy_curve": entropy_curve,
        "dominance_curve": dominance_curve,
        "transition_step": event["transition_step"],
        "native_final": native_curve[-1],
        "native_metrics": {
            "giant_component_fraction": native_curve[-1],
            "occupation_probability": probabilities[-1],
        },
    }
