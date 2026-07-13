"""Aggregation helpers for DBI-3 public-goods imitation outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from saee_v1_2.universality_test.common_metrics import (
    CLAIM_BOUNDARIES,
    bernoulli_bootstrap_ci,
    bootstrap_ci,
    mean,
    median,
    variance,
)


def summarize_dbi3_runs(
    run_summaries: list[dict[str, Any]],
    num_seeds: int,
    graph_presets: list[str],
    bootstrap_resamples: int = 5000,
) -> dict[str, Any]:
    transition_probability = {}
    transition_step = {}
    all_transition_phi = []
    for governance in ["none", "weak", "strong"]:
        rows = [row for row in run_summaries if row["governance"] == governance]
        transitioned = [row for row in rows if row["transition_step"] is not None]
        steps = [float(row["transition_step"]) for row in transitioned]
        phis = [
            float(row["transition_phi"])
            for row in transitioned
            if row.get("transition_phi") is not None
        ]
        all_transition_phi.extend(phis)
        transition_probability[governance] = round(
            len(transitioned) / len(rows), 6
        ) if rows else 0.0
        transition_step[governance] = {
            "mean": None if mean(steps) is None else round(mean(steps) or 0.0, 6),
            "median": None if median(steps) is None else round(median(steps) or 0.0, 6),
            "bootstrap_95_ci": bootstrap_ci(
                steps,
                resamples=bootstrap_resamples,
                seed=8100 + len(governance),
                statistic="median",
            ),
            "transition_probability_bootstrap_95_ci": bernoulli_bootstrap_ci(
                len(transitioned),
                len(rows),
                resamples=bootstrap_resamples,
                seed=8200 + len(governance),
            ),
        }

    return {
        "schema": "saee.universality_test.dbi3_summary.v1",
        "dbi3_design": "public_goods_imitation_network",
        "num_seeds": num_seeds,
        "graph_presets": graph_presets,
        "bootstrap_resamples": bootstrap_resamples,
        "transition_probability": transition_probability,
        "transition_step": transition_step,
        "phi_transition_stats": {
            "mean_transition_phi": (
                None
                if mean(all_transition_phi) is None
                else round(mean(all_transition_phi) or 0.0, 6)
            ),
            "variance_transition_phi": (
                None
                if variance(all_transition_phi) is None
                else round(variance(all_transition_phi) or 0.0, 6)
            ),
        },
        "boundaries": CLAIM_BOUNDARIES,
    }


def manifest(
    created_files: list[Path],
    num_seeds: int,
    bootstrap_resamples: int,
    graph_presets: list[str],
) -> dict[str, Any]:
    return {
        "schema": "saee.universality_test.dbi3_manifest.v1",
        "created_files": [str(path) for path in created_files],
        "num_seeds": num_seeds,
        "bootstrap_resamples": bootstrap_resamples,
        "graph_presets": graph_presets,
        "claim_boundaries": CLAIM_BOUNDARIES,
        "forbidden_core_modified": False,
    }
