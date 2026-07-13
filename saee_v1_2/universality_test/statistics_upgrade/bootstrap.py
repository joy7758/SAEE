"""Bootstrap summaries for transition runs."""

from __future__ import annotations

from typing import Any

from saee_v1_2.universality_test.common_metrics import (
    bernoulli_bootstrap_ci,
    bootstrap_ci,
    mean,
    median,
    variance,
)


def summarize_group(
    rows: list[dict[str, Any]],
    bootstrap_resamples: int,
    seed: int,
) -> dict[str, Any]:
    transitioned = [row for row in rows if row.get("transition_step") is not None]
    steps = [float(row["transition_step"]) for row in transitioned]
    phis = [
        float(row["transition_phi"])
        for row in transitioned
        if row.get("transition_phi") is not None
    ]
    return {
        "num_runs": len(rows),
        "transition_count": len(transitioned),
        "transition_probability": round(len(transitioned) / len(rows), 6) if rows else 0.0,
        "transition_probability_bootstrap_95_ci": bernoulli_bootstrap_ci(
            len(transitioned),
            len(rows),
            resamples=bootstrap_resamples,
            seed=seed,
        ),
        "transition_step_mean": None if mean(steps) is None else round(mean(steps) or 0.0, 6),
        "transition_step_median": None if median(steps) is None else round(median(steps) or 0.0, 6),
        "transition_step_variance": None if variance(steps) is None else round(variance(steps) or 0.0, 6),
        "transition_step_bootstrap_95_ci": bootstrap_ci(
            steps,
            resamples=bootstrap_resamples,
            seed=seed + 17,
            statistic="median",
        ),
        "transition_phi_mean": None if mean(phis) is None else round(mean(phis) or 0.0, 6),
        "transition_phi_variance": None if variance(phis) is None else round(variance(phis) or 0.0, 6),
    }

