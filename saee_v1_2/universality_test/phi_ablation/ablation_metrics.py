"""Metrics for Phi component ablations.

The functions in this module are observation-layer analyses. They do not
change DBI dynamics; they recompute bounded Phi variants from recorded
resource-concentration, reward-drift, and dominance components.
"""

from __future__ import annotations

from typing import Any

from saee_v1_2.universality_test.common_metrics import (
    bootstrap_ci,
    clamp,
    detect_transition,
    mean,
    median,
    pearson,
    phi_from_components,
    rank_correlation,
)


COMPONENT_KEYS = [
    "resource_concentration",
    "reward_drift",
    "agent_dominance",
]

ABLATIONS: dict[str, tuple[float, float, float]] = {
    "full": (0.35, 0.35, 0.30),
    "drop_RC": (0.00, 0.50, 0.50),
    "drop_RD": (0.50, 0.00, 0.50),
    "drop_AD": (0.50, 0.50, 0.00),
    "pair_RC_RD": (0.50, 0.50, 0.00),
    "pair_RC_AD": (0.50, 0.00, 0.50),
    "pair_RD_AD": (0.00, 0.50, 0.50),
    "equal": (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
}


def phi_curve_from_components(
    components: list[dict[str, float]],
    weights: tuple[float, float, float],
) -> list[float]:
    return [
        round(
            phi_from_components(
                item["resource_concentration"],
                item["reward_drift"],
                item["agent_dominance"],
                weights,
            ),
            6,
        )
        for item in components
    ]


def transition_label(phi_curve: list[float], phi_threshold: float = 0.60) -> int:
    return 1 if detect_transition(phi_curve, phi_threshold=phi_threshold) else 0


def agreement_score(
    reference_step: int | None,
    candidate_step: int | None,
    steps: int,
) -> float:
    if reference_step is None and candidate_step is None:
        return 1.0
    if reference_step is None or candidate_step is None:
        return 0.0
    return clamp(1.0 - abs(reference_step - candidate_step) / max(1, steps))


def auc_by_threshold(scores: list[float], labels: list[int]) -> float | None:
    positives = [score for score, label in zip(scores, labels) if label == 1]
    negatives = [score for score, label in zip(scores, labels) if label == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    total = len(positives) * len(negatives)
    for pos in positives:
        for neg in negatives:
            if pos > neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return wins / total


def summarize_ablation(
    runs: list[dict[str, Any]],
    ablation_name: str,
    weights: tuple[float, float, float],
    phi_threshold: float = 0.60,
    bootstrap_resamples: int = 5000,
) -> dict[str, Any]:
    by_system: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        by_system.setdefault(run["system_id"], []).append(run)

    transition_probability = {}
    transition_step_median = {}
    transition_step_ci = {}
    auc = {}
    rank_corr = {}
    pearson_corr = {}
    step_agreement = {}

    for system_id, system_runs in sorted(by_system.items()):
        labels = []
        scores = []
        candidate_steps = []
        agreement_values = []
        full_values = []
        candidate_values = []
        for run in system_runs:
            candidate_curve = phi_curve_from_components(run["components"], weights)
            full_curve = phi_curve_from_components(run["components"], ABLATIONS["full"])
            event = detect_transition(candidate_curve, phi_threshold=phi_threshold)
            full_event = detect_transition(full_curve, phi_threshold=phi_threshold)
            labels.append(1 if full_event else 0)
            scores.append(max(candidate_curve) if candidate_curve else 0.0)
            step = None if event is None else int(event["timestep"])
            full_step = None if full_event is None else int(full_event["timestep"])
            if step is not None:
                candidate_steps.append(float(step))
            agreement_values.append(
                agreement_score(full_step, step, len(candidate_curve))
            )
            full_values.extend(full_curve)
            candidate_values.extend(candidate_curve)

        transition_count = sum(1 for run in system_runs if detect_transition(
            phi_curve_from_components(run["components"], weights),
            phi_threshold=phi_threshold,
        ))
        total = len(system_runs)
        transition_probability[system_id] = round(transition_count / total, 6) if total else 0.0
        transition_step_median[system_id] = (
            None if median(candidate_steps) is None else round(median(candidate_steps) or 0.0, 6)
        )
        transition_step_ci[system_id] = bootstrap_ci(
            candidate_steps,
            resamples=bootstrap_resamples,
            seed=6000 + len(ablation_name) + len(system_id),
            statistic="median",
        )
        auc_value = auc_by_threshold(scores, labels)
        auc[system_id] = None if auc_value is None else round(auc_value, 6)
        rank_value = rank_correlation(full_values, candidate_values)
        rank_corr[system_id] = None if rank_value is None else round(rank_value, 6)
        pearson_value = pearson(full_values, candidate_values)
        pearson_corr[system_id] = None if pearson_value is None else round(pearson_value, 6)
        step_agreement[system_id] = (
            None if mean(agreement_values) is None else round(mean(agreement_values) or 0.0, 6)
        )

    return {
        "name": ablation_name,
        "weights": {
            "RC": weights[0],
            "RD": weights[1],
            "AD": weights[2],
        },
        "transition_probability_by_system": transition_probability,
        "transition_step_median_by_system": transition_step_median,
        "transition_step_bootstrap_95_ci_by_system": transition_step_ci,
        "auc_against_full_transition_label": auc,
        "rank_correlation_with_full_phi": rank_corr,
        "pearson_correlation_with_full_phi": pearson_corr,
        "transition_step_agreement_with_full": step_agreement,
    }


def component_importance(ablations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full = next(item for item in ablations if item["name"] == "full")
    rows = []
    mapping = {
        "resource_concentration": "drop_RC",
        "reward_drift": "drop_RD",
        "agent_dominance": "drop_AD",
    }
    for component, drop_name in mapping.items():
        dropped = next(item for item in ablations if item["name"] == drop_name)
        for system_id, full_prob in full["transition_probability_by_system"].items():
            drop_prob = dropped["transition_probability_by_system"].get(system_id, 0.0)
            agreement = dropped["transition_step_agreement_with_full"].get(system_id)
            rows.append(
                {
                    "component": component,
                    "system_id": system_id,
                    "full_transition_probability": full_prob,
                    "dropped_transition_probability": drop_prob,
                    "transition_probability_delta": round(full_prob - drop_prob, 6),
                    "step_agreement_after_drop": agreement,
                }
            )
    return rows

