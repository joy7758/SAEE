"""MARL-lite public-goods Q-learning baseline."""

from __future__ import annotations

import math
import random
from typing import Any

from saee_v1_2.universality_test.baselines.baseline_metrics import (
    bounded_phi,
    concentration_from_values,
    transition_summary,
    ws_graph,
)
from saee_v1_2.universality_test.common_metrics import clamp


def run_marl_public_goods(seed: int, steps: int = 160, agents: int = 48) -> dict[str, Any]:
    rng = random.Random(seed)
    graph = ws_graph(agents, degree=4, beta=0.18, rng=rng)
    q_cooperate = [rng.uniform(-0.05, 0.05) for _ in range(agents)]
    q_defect = [rng.uniform(-0.05, 0.05) for _ in range(agents)]
    wealth = [1.0 for _ in range(agents)]
    initial_defect_bias = 0.5
    epsilon = 0.18
    alpha = 0.12
    gamma = 0.92
    phi_curve = []
    native_curve = []
    entropy_curve = []
    dominance_curve = []
    for _ in range(steps):
        actions = []
        for index in range(agents):
            if rng.random() < epsilon:
                action = rng.choice(["cooperate", "defect"])
            else:
                action = "cooperate" if q_cooperate[index] >= q_defect[index] else "defect"
            actions.append(action)
        payoffs = [0.0 for _ in range(agents)]
        for index in range(agents):
            group = [index] + sorted(graph[index])
            contributors = sum(1 for item in group if actions[item] == "cooperate")
            benefit = 1.62 * contributors / len(group)
            for item in group:
                payoffs[item] += benefit - (0.68 if actions[item] == "cooperate" else 0.0)
        for index, payoff in enumerate(payoffs):
            wealth[index] = max(0.0, 0.985 * wealth[index] + payoff)
            if actions[index] == "cooperate":
                q_cooperate[index] += alpha * (payoff + gamma * max(q_cooperate[index], q_defect[index]) - q_cooperate[index])
            else:
                q_defect[index] += alpha * (payoff + gamma * max(q_cooperate[index], q_defect[index]) - q_defect[index])
        defect_probs = [
            1.0 / (1.0 + math.exp(q_cooperate[index] - q_defect[index]))
            for index in range(agents)
        ]
        mean_defect = sum(defect_probs) / agents
        policy_entropy = 0.0
        for probability in defect_probs:
            p = clamp(probability, 1e-6, 1 - 1e-6)
            policy_entropy += -(p * math.log(p) + (1 - p) * math.log(1 - p)) / math.log(2)
        policy_entropy /= agents
        resource_concentration = concentration_from_values(wealth)
        reward_drift = clamp(abs(mean_defect - initial_defect_bias) * 2.0)
        dominance = clamp(max(max(defect_probs), 1.0 - min(defect_probs)))
        phi_curve.append(round(bounded_phi(resource_concentration, reward_drift, dominance), 6))
        native_curve.append(round(sum(payoffs) / agents / 5.0, 6))
        entropy_curve.append(round(policy_entropy, 6))
        dominance_curve.append(round(dominance, 6))
        epsilon = max(0.03, epsilon * 0.992)
    event = transition_summary(phi_curve)
    return {
        "baseline": "marl_public_goods_q_learning",
        "seed": seed,
        "phi_curve": phi_curve,
        "native_curve": native_curve,
        "entropy_curve": entropy_curve,
        "dominance_curve": dominance_curve,
        "transition_step": event["transition_step"],
        "native_final": native_curve[-1],
        "native_metrics": {
            "team_return": native_curve[-1],
            "policy_entropy": entropy_curve[-1],
        },
    }

