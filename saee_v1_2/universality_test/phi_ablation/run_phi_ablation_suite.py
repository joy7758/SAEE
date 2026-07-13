#!/usr/bin/env python3
"""Run Phi ablations across DBI-1, DBI-2, and DBI-3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.parasitic_phase.model import (  # noqa: E402
    ExperimentConfig,
    ParasiticPhaseSimulation,
)
from saee_v1_2.universality_test.common_metrics import (  # noqa: E402
    CLAIM_BOUNDARIES,
    detect_transition,
    phi_from_components,
    write_csv,
    write_json,
)
from saee_v1_2.universality_test.dbi2_model import DBI2Config, DBI2Simulation  # noqa: E402
from saee_v1_2.universality_test.dbi3_public_goods_model import (  # noqa: E402
    DBI3Config,
    DBI3Simulation,
)
from saee_v1_2.universality_test.phi_ablation.ablation_metrics import (  # noqa: E402
    ABLATIONS,
    component_importance,
    phi_curve_from_components,
    summarize_ablation,
)
from saee_v1_2.universality_test.phi_ablation.plots import (  # noqa: E402
    write_ablation_heatmap,
)


DEFAULT_OUTPUT_DIR = Path("saee_v1_2/universality_test/results/phi_ablation")


def components_from_metrics(metrics: list[dict]) -> list[dict[str, float]]:
    return [
        {
            "resource_concentration": float(metric["resource_concentration"]),
            "reward_drift": float(metric["reward_drift"]),
            "agent_dominance": float(metric["agent_dominance"]),
        }
        for metric in metrics
    ]


def collect_runs(seeds: int, steps: int) -> list[dict]:
    runs = []
    for seed_offset in range(seeds):
        dbi1 = ParasiticPhaseSimulation(
            ExperimentConfig(
                experiment_id=f"PHI_ABLATION_DBI1_{seed_offset:03d}",
                governance="none",
                seed=410000 + seed_offset,
                steps=steps,
            )
        ).run()
        runs.append(
            {
                "system_id": "DBI-1",
                "seed": 410000 + seed_offset,
                "steps": steps,
                "components": components_from_metrics(dbi1.metrics),
            }
        )

        dbi2 = DBI2Simulation(
            DBI2Config(
                experiment_id=f"PHI_ABLATION_DBI2_{seed_offset:03d}",
                governance="none",
                seed=520000 + seed_offset,
                steps=steps,
            )
        ).run()
        runs.append(
            {
                "system_id": "DBI-2",
                "seed": 520000 + seed_offset,
                "steps": steps,
                "components": components_from_metrics(dbi2.metrics),
            }
        )

        dbi3 = DBI3Simulation(
            DBI3Config(
                experiment_id=f"PHI_ABLATION_DBI3_{seed_offset:03d}",
                governance="none",
                graph_preset=["ER", "WS", "BA"][seed_offset % 3],
                seed=630000 + seed_offset,
                steps=steps,
            )
        ).run()
        runs.append(
            {
                "system_id": "DBI-3",
                "seed": 630000 + seed_offset,
                "steps": steps,
                "components": components_from_metrics(dbi3.metrics),
            }
        )
    return runs


def random_weights(rng: random.Random) -> tuple[float, float, float]:
    values = [rng.random() for _ in range(3)]
    total = sum(values)
    return (values[0] / total, values[1] / total, values[2] / total)


def random_weight_controls(runs: list[dict], samples: int, phi_threshold: float) -> dict:
    rng = random.Random(20260706)
    rows = []
    for index in range(samples):
        weights = random_weights(rng)
        by_system: dict[str, list[int]] = {}
        for run in runs:
            curve = phi_curve_from_components(run["components"], weights)
            by_system.setdefault(run["system_id"], []).append(
                1 if detect_transition(curve, phi_threshold=phi_threshold) else 0
            )
        rows.append(
            {
                "sample": index,
                "weights": {"RC": weights[0], "RD": weights[1], "AD": weights[2]},
                "transition_probability_by_system": {
                    system: round(sum(values) / len(values), 6)
                    for system, values in sorted(by_system.items())
                },
            }
        )
    return {
        "num_weight_samples": samples,
        "summary": rows,
    }


def permutation_controls(runs: list[dict], phi_threshold: float) -> dict:
    rng = random.Random(20260707)
    output = {}
    for system_id in ["DBI-1", "DBI-2", "DBI-3"]:
        labels = []
        for run in [item for item in runs if item["system_id"] == system_id]:
            shuffled = []
            rc = [item["resource_concentration"] for item in run["components"]]
            rd = [item["reward_drift"] for item in run["components"]]
            ad = [item["agent_dominance"] for item in run["components"]]
            rng.shuffle(rc)
            rng.shuffle(rd)
            rng.shuffle(ad)
            for index in range(len(run["components"])):
                shuffled.append(
                    {
                        "resource_concentration": rc[index],
                        "reward_drift": rd[index],
                        "agent_dominance": ad[index],
                    }
                )
            curve = phi_curve_from_components(shuffled, ABLATIONS["full"])
            labels.append(1 if detect_transition(curve, phi_threshold=phi_threshold) else 0)
        output[system_id] = round(sum(labels) / len(labels), 6) if labels else 0.0
    return output


def roc_rows(ablations: list[dict]) -> list[dict]:
    rows = []
    for ablation in ablations:
        for system_id, auc in ablation["auc_against_full_transition_label"].items():
            rows.append(
                {
                    "ablation": ablation["name"],
                    "system_id": system_id,
                    "auc_against_full_transition_label": auc,
                    "rank_correlation_with_full_phi": ablation[
                        "rank_correlation_with_full_phi"
                    ].get(system_id),
                    "pearson_correlation_with_full_phi": ablation[
                        "pearson_correlation_with_full_phi"
                    ].get(system_id),
                    "transition_step_agreement_with_full": ablation[
                        "transition_step_agreement_with_full"
                    ].get(system_id),
                }
            )
    return rows


def run_suite(
    seeds: int,
    steps: int,
    bootstrap_resamples: int,
    random_weight_samples: int,
    output_dir: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    runs = collect_runs(seeds=seeds, steps=steps)
    ablations = [
        summarize_ablation(
            runs,
            name,
            weights,
            bootstrap_resamples=bootstrap_resamples,
        )
        for name, weights in ABLATIONS.items()
    ]
    summary = {
        "schema": "saee.universality_test.phi_ablation_summary.v1",
        "systems": ["DBI-1", "DBI-2", "DBI-3"],
        "num_seeds": seeds,
        "steps": steps,
        "bootstrap_resamples": bootstrap_resamples,
        "ablations": ablations,
        "random_weight_controls": random_weight_controls(
            runs,
            samples=random_weight_samples,
            phi_threshold=0.60,
        ),
        "permutation_controls": permutation_controls(runs, phi_threshold=0.60),
        "claim_boundaries": CLAIM_BOUNDARIES,
    }
    summary_path = output_dir / "phi_ablation_summary.json"
    importance_path = output_dir / "phi_component_importance.csv"
    roc_path = output_dir / "phi_component_roc.csv"
    heatmap_path = output_dir / "phi_ablation_heatmap.svg"
    manifest_path = output_dir / "phi_ablation_manifest.json"
    write_json(summary_path, summary)
    write_csv(
        importance_path,
        component_importance(ablations),
        fields=[
            "component",
            "system_id",
            "full_transition_probability",
            "dropped_transition_probability",
            "transition_probability_delta",
            "step_agreement_after_drop",
        ],
    )
    write_csv(
        roc_path,
        roc_rows(ablations),
        fields=[
            "ablation",
            "system_id",
            "auc_against_full_transition_label",
            "rank_correlation_with_full_phi",
            "pearson_correlation_with_full_phi",
            "transition_step_agreement_with_full",
        ],
    )
    write_ablation_heatmap(heatmap_path, ablations)
    write_json(
        manifest_path,
        {
            "schema": "saee.universality_test.phi_ablation_manifest.v1",
            "created_files": [
                str(summary_path),
                str(importance_path),
                str(roc_path),
                str(heatmap_path),
                str(manifest_path),
            ],
            "systems": ["DBI-1", "DBI-2", "DBI-3"],
            "num_seeds": seeds,
            "bootstrap_resamples": bootstrap_resamples,
            "random_weight_samples": random_weight_samples,
            "forbidden_core_modified": False,
            "claim_boundaries": CLAIM_BOUNDARIES,
        },
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=120)
    parser.add_argument("--steps", type=int, default=160)
    parser.add_argument("--bootstrap-resamples", type=int, default=5000)
    parser.add_argument("--random-weight-samples", type=int, default=100)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    summary = run_suite(
        seeds=args.seeds,
        steps=args.steps,
        bootstrap_resamples=args.bootstrap_resamples,
        random_weight_samples=args.random_weight_samples,
        output_dir=output_dir,
    )
    full = next(item for item in summary["ablations"] if item["name"] == "full")
    print(
        "SAEE_PHI_ABLATION: "
        f"DBI1={full['transition_probability_by_system']['DBI-1']} "
        f"DBI2={full['transition_probability_by_system']['DBI-2']} "
        f"DBI3={full['transition_probability_by_system']['DBI-3']} "
        f"output={output_dir}"
    )


if __name__ == "__main__":
    main()
