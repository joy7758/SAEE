"""SIR epidemic threshold baseline."""

from __future__ import annotations

import random
from typing import Any

from saee_v1_2.universality_test.baselines.baseline_metrics import (
    bounded_phi,
    concentration_from_values,
    er_graph,
    transition_summary,
)
from saee_v1_2.universality_test.common_metrics import clamp


def run_sir_epidemic(seed: int, nodes: int = 72, beta_points: int = 21) -> dict[str, Any]:
    rng = random.Random(seed)
    graph = er_graph(nodes, p=0.055, rng=rng)
    betas = [0.02 + index * (0.42 / (beta_points - 1)) for index in range(beta_points)]
    gamma = 0.18
    phi_curve = []
    native_curve = []
    dominance_curve = []
    entropy_curve = []
    for beta in betas:
        state = ["S" for _ in range(nodes)]
        state[rng.randrange(nodes)] = "I"
        infected_ever = set(index for index, value in enumerate(state) if value == "I")
        peak_infected = 1
        for _ in range(42):
            next_state = list(state)
            for node, value in enumerate(state):
                if value == "I":
                    for neighbor in graph[node]:
                        if state[neighbor] == "S" and rng.random() < beta:
                            next_state[neighbor] = "I"
                            infected_ever.add(neighbor)
                    if rng.random() < gamma:
                        next_state[node] = "R"
            state = next_state
            peak_infected = max(peak_infected, sum(1 for value in state if value == "I"))
            if peak_infected == 0:
                break
        outbreak = len(infected_ever) / nodes
        resource_concentration = concentration_from_values(
            [1.0 if index in infected_ever else 0.0 for index in range(nodes)]
        )
        reward_drift = clamp(beta / max(betas))
        dominance = outbreak
        phi_curve.append(round(bounded_phi(resource_concentration, reward_drift, dominance), 6))
        native_curve.append(round(outbreak, 6))
        dominance_curve.append(round(dominance, 6))
        entropy_curve.append(round(clamp(1.0 - outbreak), 6))
    event = transition_summary(phi_curve)
    return {
        "baseline": "sir_epidemic",
        "seed": seed,
        "phi_curve": phi_curve,
        "native_curve": native_curve,
        "entropy_curve": entropy_curve,
        "dominance_curve": dominance_curve,
        "transition_step": event["transition_step"],
        "native_final": native_curve[-1],
        "native_metrics": {
            "infected_fraction": native_curve[-1],
            "outbreak_size": len(infected_ever),
            "peak_infected_fraction": peak_infected / nodes,
        },
    }

