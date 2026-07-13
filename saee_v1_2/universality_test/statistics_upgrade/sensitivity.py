"""Observation-layer sensitivity surfaces for recorded Phi component curves."""

from __future__ import annotations

import random
from typing import Any

from saee_v1_2.universality_test.common_metrics import (
    clamp,
    detect_transition,
    phi_from_components,
)


PHI_C_MULTIPLIERS = [0.90, 1.00, 1.10]
RESOURCE_NOISE = [0.00, 0.05, 0.10, 0.20]
RATE_MULTIPLIERS = [0.80, 1.00, 1.20]
GOVERNANCE_DELAYS = [0, 2, 5]


def perturb_curve(
    run: dict[str, Any],
    resource_noise: float,
    rate_multiplier: float,
) -> list[float]:
    rng = random.Random(int(run["seed"]) + int(resource_noise * 1000) + int(rate_multiplier * 100))
    raw_curve = []
    for component in run["components"]:
        rc = clamp(component["resource_concentration"] * (1.0 + rng.uniform(-resource_noise, resource_noise)))
        raw_curve.append(
            phi_from_components(
                rc,
                component["reward_drift"],
                component["agent_dominance"],
            )
        )
    if rate_multiplier == 1.0:
        return [round(value, 6) for value in raw_curve]
    # Observation-layer rate proxy: compress or stretch the recorded trajectory
    # without changing the underlying simulator.
    scaled = []
    for index in range(len(raw_curve)):
        source = min(len(raw_curve) - 1, int(index * rate_multiplier))
        scaled.append(round(raw_curve[source], 6))
    return scaled


def apply_delay(step: int | None, delay: int, curve_length: int) -> int | None:
    if step is None:
        return None
    return min(curve_length - 1, step + delay)


def sensitivity_surface(
    runs: list[dict[str, Any]],
    phi_threshold: float = 0.60,
) -> list[dict[str, Any]]:
    rows = []
    for system_id in sorted({run["system_id"] for run in runs}):
        system_runs = [run for run in runs if run["system_id"] == system_id]
        for threshold_multiplier in PHI_C_MULTIPLIERS:
            for resource_noise in RESOURCE_NOISE:
                for rate_multiplier in RATE_MULTIPLIERS:
                    for governance_delay in GOVERNANCE_DELAYS:
                        transitioned = 0
                        transition_steps = []
                        for run in system_runs:
                            curve = perturb_curve(run, resource_noise, rate_multiplier)
                            event = detect_transition(
                                curve,
                                phi_threshold=phi_threshold * threshold_multiplier,
                            )
                            step = None if event is None else int(event["timestep"])
                            step = apply_delay(step, governance_delay, len(curve))
                            if step is not None:
                                transitioned += 1
                                transition_steps.append(step)
                        probability = transitioned / len(system_runs) if system_runs else 0.0
                        rows.append(
                            {
                                "system_id": system_id,
                                "phi_c_multiplier": threshold_multiplier,
                                "resource_noise": resource_noise,
                                "rate_multiplier": rate_multiplier,
                                "governance_delay": governance_delay,
                                "transition_probability": round(probability, 6),
                                "mean_transition_step": (
                                    None
                                    if not transition_steps
                                    else round(sum(transition_steps) / len(transition_steps), 6)
                                ),
                                "sensitivity_type": "observation_layer_recompute_from_recorded_components",
                            }
                        )
    return rows


def robustness_scores(surface_rows: list[dict[str, Any]], baseline_probability: dict[str, float]) -> dict[str, float]:
    scores = {}
    for system_id in sorted({row["system_id"] for row in surface_rows}):
        rows = [row for row in surface_rows if row["system_id"] == system_id]
        base = baseline_probability.get(system_id, 0.0)
        if not rows:
            scores[system_id] = 0.0
            continue
        drift = sum(abs(float(row["transition_probability"]) - base) for row in rows) / len(rows)
        scores[system_id] = round(clamp(1.0 - drift), 6)
    return scores

