#!/usr/bin/env python3
"""Run the 120-seed and bootstrap statistical upgrade."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
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
    write_csv,
    write_json,
)
from saee_v1_2.universality_test.dbi2_model import DBI2Config, DBI2Simulation  # noqa: E402
from saee_v1_2.universality_test.dbi3_public_goods_model import (  # noqa: E402
    DBI3Config,
    DBI3Simulation,
)
from saee_v1_2.universality_test.statistics_upgrade.bootstrap import (  # noqa: E402
    summarize_group,
)
from saee_v1_2.universality_test.statistics_upgrade.plots import (  # noqa: E402
    write_sensitivity_surface,
    write_transition_step_violin,
)
from saee_v1_2.universality_test.statistics_upgrade.sensitivity import (  # noqa: E402
    GOVERNANCE_DELAYS,
    PHI_C_MULTIPLIERS,
    RATE_MULTIPLIERS,
    RESOURCE_NOISE,
    robustness_scores,
    sensitivity_surface,
)


DEFAULT_OUTPUT_DIR = Path("saee_v1_2/universality_test/results/statistics_upgrade")
DBI3_METRICS = Path("saee_v1_2/universality_test/results/dbi3/dbi3_metrics.csv")
GOVERNANCE = ["none", "weak", "strong"]


def components_from_metrics(metrics: list[dict]) -> list[dict[str, float]]:
    return [
        {
            "resource_concentration": float(metric["resource_concentration"]),
            "reward_drift": float(metric["reward_drift"]),
            "agent_dominance": float(metric["agent_dominance"]),
        }
        for metric in metrics
    ]


def row_from_result(system_id: str, governance: str, seed: int, metrics: list[dict], event: dict | None) -> dict:
    curve = [float(metric["phi"]) for metric in metrics]
    detected = detect_transition(curve, phi_threshold=0.60)
    event = event or detected
    return {
        "system_id": system_id,
        "governance": governance,
        "seed": seed,
        "phi_curve": curve,
        "components": components_from_metrics(metrics),
        "transition_step": None if event is None else int(event["timestep"]),
        "transition_phi": None if event is None else float(event["phi"]),
        "transition_slope": None if event is None else float(event.get("transition_slope", 0.0)),
    }


def collect_dbi1_dbi2(seeds: int, steps: int) -> list[dict]:
    rows = []
    for governance in GOVERNANCE:
        for offset in range(seeds):
            dbi1_seed = 810000 + offset
            result1 = ParasiticPhaseSimulation(
                ExperimentConfig(
                    experiment_id=f"STAT_DBI1_{governance}_{offset:03d}",
                    governance=governance,
                    seed=dbi1_seed,
                    steps=steps,
                )
            ).run()
            rows.append(row_from_result("DBI-1", governance, dbi1_seed, result1.metrics, result1.transition_event))

            dbi2_seed = 820000 + offset
            result2 = DBI2Simulation(
                DBI2Config(
                    experiment_id=f"STAT_DBI2_{governance}_{offset:03d}",
                    governance=governance,
                    seed=dbi2_seed,
                    steps=steps,
                )
            ).run()
            rows.append(row_from_result("DBI-2", governance, dbi2_seed, result2.metrics, result2.transition_event))
    return rows


def load_or_generate_dbi3(root: Path, seeds: int, steps: int) -> list[dict]:
    metrics_path = root / DBI3_METRICS
    if metrics_path.exists():
        grouped: dict[tuple[str, int, str], list[dict]] = {}
        with metrics_path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                key = (row["governance"], int(row["seed"]), row["graph_preset"])
                grouped.setdefault(key, []).append(row)
        rows = []
        for (governance, seed, graph), items in grouped.items():
            items.sort(key=lambda item: int(item["timestep"]))
            metrics = [
                {
                    "phi": float(item["phi"]),
                    "resource_concentration": float(item["resource_concentration"]),
                    "reward_drift": float(item["reward_drift"]),
                    "agent_dominance": float(item["dominance"]),
                }
                for item in items
            ]
            event = detect_transition([metric["phi"] for metric in metrics], phi_threshold=0.60)
            row = row_from_result("DBI-3", governance, seed, metrics, event)
            row["graph_preset"] = graph
            rows.append(row)
        return rows

    rows = []
    for governance in GOVERNANCE:
        for offset in range(seeds):
            seed = 830000 + offset
            result = DBI3Simulation(
                DBI3Config(
                    experiment_id=f"STAT_DBI3_{governance}_{offset:03d}",
                    governance=governance,
                    graph_preset=["ER", "WS", "BA"][offset % 3],
                    seed=seed,
                    steps=steps,
                )
            ).run()
            rows.append(row_from_result("DBI-3", governance, seed, result.metrics, result.transition_event))
    return rows


def run_upgrade(
    seeds: int,
    steps: int,
    bootstrap_resamples: int,
    output_dir: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    core_runs = collect_dbi1_dbi2(seeds=seeds, steps=steps)
    core_runs.extend(load_or_generate_dbi3(ROOT, seeds=seeds, steps=steps))

    grouped_summary = {}
    for system_id in ["DBI-1", "DBI-2", "DBI-3"]:
        for governance in GOVERNANCE:
            rows = [
                row for row in core_runs
                if row["system_id"] == system_id and row["governance"] == governance
            ]
            grouped_summary[f"{system_id}:{governance}"] = summarize_group(
                rows,
                bootstrap_resamples=bootstrap_resamples,
                seed=9000 + len(system_id) + len(governance),
            )

    none_runs = [row for row in core_runs if row["governance"] == "none"]
    surface_rows = sensitivity_surface(none_runs)
    baseline_probability = {
        system_id: grouped_summary[f"{system_id}:none"]["transition_probability"]
        for system_id in ["DBI-1", "DBI-2", "DBI-3"]
    }
    robustness = robustness_scores(surface_rows, baseline_probability)

    summary = {
        "schema": "saee.universality_test.statistical_upgrade_summary.v1",
        "num_seeds": seeds,
        "bootstrap_resamples": bootstrap_resamples,
        "steps": steps,
        "systems": ["DBI-1", "DBI-2", "DBI-3"],
        "governance_regimes": GOVERNANCE,
        "grouped_transition_statistics": grouped_summary,
        "perturbations": {
            "phi_c_multiplier": PHI_C_MULTIPLIERS,
            "resource_noise": RESOURCE_NOISE,
            "rate_multiplier": RATE_MULTIPLIERS,
            "governance_delay": GOVERNANCE_DELAYS,
            "sensitivity_type": "observation_layer_recompute_from_recorded_components",
        },
        "robustness_scores": robustness,
        "claim_boundaries": CLAIM_BOUNDARIES,
    }

    interval_path = output_dir / "bootstrap_transition_intervals.json"
    summary_path = output_dir / "statistical_upgrade_summary.json"
    surface_path = output_dir / "sensitivity_surface_rows.csv"
    sensitivity_svg = output_dir / "sensitivity_surfaces.svg"
    violin_svg = output_dir / "transition_step_violin.svg"
    manifest_path = output_dir / "statistics_upgrade_manifest.json"
    write_json(summary_path, summary)
    write_json(
        interval_path,
        {
            "schema": "saee.universality_test.bootstrap_transition_intervals.v1",
            "bootstrap_resamples": bootstrap_resamples,
            "grouped_transition_statistics": grouped_summary,
            "claim_boundaries": CLAIM_BOUNDARIES,
        },
    )
    write_csv(
        surface_path,
        surface_rows,
        fields=[
            "system_id",
            "phi_c_multiplier",
            "resource_noise",
            "rate_multiplier",
            "governance_delay",
            "transition_probability",
            "mean_transition_step",
            "sensitivity_type",
        ],
    )
    write_sensitivity_surface(sensitivity_svg, surface_rows)
    write_transition_step_violin(violin_svg, grouped_summary)
    write_json(
        manifest_path,
        {
            "schema": "saee.universality_test.statistics_upgrade_manifest.v1",
            "created_files": [
                str(summary_path),
                str(interval_path),
                str(surface_path),
                str(sensitivity_svg),
                str(violin_svg),
                str(manifest_path),
            ],
            "num_seeds": seeds,
            "bootstrap_resamples": bootstrap_resamples,
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
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    summary = run_upgrade(
        seeds=args.seeds,
        steps=args.steps,
        bootstrap_resamples=args.bootstrap_resamples,
        output_dir=output_dir,
    )
    print(
        "SAEE_STATISTICS_UPGRADE: "
        + " ".join(
            f"{system}={score}"
            for system, score in summary["robustness_scores"].items()
        )
        + f" output={output_dir}"
    )


if __name__ == "__main__":
    main()
