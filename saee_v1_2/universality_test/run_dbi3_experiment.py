#!/usr/bin/env python3
"""Run DBI-3 public-goods imitation network reviewer-proofing experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.universality_test.analysis.dbi3_metrics import (  # noqa: E402
    manifest,
    summarize_dbi3_runs,
)
from saee_v1_2.universality_test.common_metrics import (  # noqa: E402
    svg_line_chart,
    write_csv,
    write_json,
)
from saee_v1_2.universality_test.dbi3_public_goods_model import (  # noqa: E402
    DBI3Config,
    DBI3Simulation,
)


GRAPH_PRESETS = ["ER", "WS", "BA"]
GOVERNANCE = ["none", "weak", "strong"]
DEFAULT_OUTPUT_DIR = Path("saee_v1_2/universality_test/results/dbi3")


def run_all(
    seeds: int,
    steps: int,
    node_count: int,
    bootstrap_resamples: int,
    output_dir: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_rows = []
    run_summaries = []
    mean_curves: dict[str, dict[str, list[list[float]]]] = {
        governance: {"phi": [], "entropy": [], "dominance": []}
        for governance in GOVERNANCE
    }
    trace_path = output_dir / "dbi3_trace.jsonl"
    with trace_path.open("w", encoding="utf-8") as trace_handle:
        for graph_preset in GRAPH_PRESETS:
            for governance in GOVERNANCE:
                for seed_offset in range(seeds):
                    seed = 930000 + seed_offset
                    config = DBI3Config(
                        experiment_id=f"DBI3_{graph_preset}_{governance}_{seed_offset:03d}",
                        governance=governance,
                        graph_preset=graph_preset,
                        seed=seed,
                        steps=steps,
                        node_count=node_count,
                    )
                    result = DBI3Simulation(config).run()
                    transition_phi = (
                        None
                        if result.transition_event is None
                        else result.transition_event["phi"]
                    )
                    transition_slope = (
                        None
                        if result.transition_event is None
                        else result.transition_event["transition_slope"]
                    )
                    pre_entropy = (
                        None
                        if result.transition_event is None
                        else result.transition_event["pre_transition_entropy"]
                    )
                    run_summaries.append(
                        {
                            "system_id": "DBI-3",
                            "graph_preset": graph_preset,
                            "governance": governance,
                            "seed": seed,
                            "transition_step": result.phase_transition_step,
                            "transition_phi": transition_phi,
                            "delta_phi_at_transition": transition_slope,
                            "pre_transition_entropy": pre_entropy,
                            "final_phi": result.metrics[-1]["phi"],
                            "final_entropy": result.metrics[-1]["entropy"],
                            "final_dominance": result.metrics[-1]["agent_dominance"],
                        }
                    )
                    mean_curves[governance]["phi"].append(
                        [metric["phi"] for metric in result.metrics]
                    )
                    mean_curves[governance]["entropy"].append(
                        [metric["entropy"] for metric in result.metrics]
                    )
                    mean_curves[governance]["dominance"].append(
                        [metric["agent_dominance"] for metric in result.metrics]
                    )
                    run_trace = result.summary()
                    run_trace["phi_curve"] = [metric["phi"] for metric in result.metrics]
                    run_trace["entropy_curve"] = [
                        metric["entropy"] for metric in result.metrics
                    ]
                    run_trace["dominance_curve"] = [
                        metric["agent_dominance"] for metric in result.metrics
                    ]
                    run_trace["components"] = [
                        {
                            "resource_concentration": metric[
                                "resource_concentration"
                            ],
                            "reward_drift": metric["reward_drift"],
                            "agent_dominance": metric["agent_dominance"],
                        }
                        for metric in result.metrics
                    ]
                    trace_handle.write(json.dumps(run_trace, sort_keys=True) + "\n")
                    for timestep, metric in enumerate(result.metrics):
                        metrics_rows.append(
                            {
                                "system_id": "DBI-3",
                                "graph_preset": graph_preset,
                                "governance": governance,
                                "seed": seed,
                                "timestep": timestep,
                                "phi": metric["phi"],
                                "entropy": metric["entropy"],
                                "dominance": metric["agent_dominance"],
                                "resource_concentration": metric["resource_concentration"],
                                "reward_drift": metric["reward_drift"],
                                "transition_step": result.phase_transition_step,
                                "transition_phi": transition_phi,
                                "delta_phi_at_transition": transition_slope,
                                "pre_transition_entropy": pre_entropy,
                            }
                        )

    fields = [
        "system_id",
        "graph_preset",
        "governance",
        "seed",
        "timestep",
        "phi",
        "entropy",
        "dominance",
        "resource_concentration",
        "reward_drift",
        "transition_step",
        "transition_phi",
        "delta_phi_at_transition",
        "pre_transition_entropy",
    ]
    metrics_path = output_dir / "dbi3_metrics.csv"
    write_csv(metrics_path, metrics_rows, fields=fields)
    summary = summarize_dbi3_runs(
        run_summaries,
        num_seeds=seeds,
        graph_presets=GRAPH_PRESETS,
        bootstrap_resamples=bootstrap_resamples,
    )
    summary_path = output_dir / "dbi3_summary.json"
    write_json(summary_path, summary)

    def average_curves(curves: list[list[float]]) -> list[float]:
        if not curves:
            return []
        width = min(len(curve) for curve in curves)
        return [
            round(sum(curve[index] for curve in curves) / len(curves), 6)
            for index in range(width)
        ]

    colors = {"none": "#b91c1c", "weak": "#1d4ed8", "strong": "#047857"}
    panels = []
    for field, label in [("phi", "DBI-3 Phi(t)"), ("entropy", "DBI-3 entropy"), ("dominance", "DBI-3 dominance")]:
        panels.append(
            {
                "label": label,
                "threshold": 0.60 if field == "phi" else None,
                "series": [
                    {
                        "name": governance,
                        "color": colors[governance],
                        "values": average_curves(mean_curves[governance][field]),
                    }
                    for governance in GOVERNANCE
                ],
            }
        )
    svg_path = output_dir / "dbi3_curves.svg"
    svg_line_chart(svg_path, "DBI-3 public-goods imitation network", panels)
    manifest_path = output_dir / "dbi3_manifest.json"
    write_json(
        manifest_path,
        {
            **manifest(
                [summary_path, metrics_path, trace_path, svg_path, manifest_path],
                num_seeds=seeds,
                bootstrap_resamples=bootstrap_resamples,
                graph_presets=GRAPH_PRESETS,
            ),
            "created_at_unix": int(time.time()),
        },
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=120)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--node-count", type=int, default=64)
    parser.add_argument("--bootstrap-resamples", type=int, default=5000)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    summary = run_all(
        seeds=args.seeds,
        steps=args.steps,
        node_count=args.node_count,
        bootstrap_resamples=args.bootstrap_resamples,
        output_dir=output_dir,
    )
    print(
        "SAEE_DBI3: "
        f"none_p={summary['transition_probability']['none']} "
        f"weak_p={summary['transition_probability']['weak']} "
        f"strong_p={summary['transition_probability']['strong']} "
        f"output={output_dir}"
    )


if __name__ == "__main__":
    main()
