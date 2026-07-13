#!/usr/bin/env python3
"""Run MARL-lite, bond-percolation, and SIR baselines."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.universality_test.baselines.baseline_metrics import (  # noqa: E402
    mean_curve,
    model_similarity,
    summarize_binary_runs,
)
from saee_v1_2.universality_test.baselines.bond_percolation import (  # noqa: E402
    run_bond_percolation,
)
from saee_v1_2.universality_test.baselines.marl_public_goods_q import (  # noqa: E402
    run_marl_public_goods,
)
from saee_v1_2.universality_test.baselines.plots import (  # noqa: E402
    write_baseline_comparison,
    write_baseline_heatmaps,
)
from saee_v1_2.universality_test.baselines.sir_epidemic import (  # noqa: E402
    run_sir_epidemic,
)
from saee_v1_2.universality_test.common_metrics import (  # noqa: E402
    CLAIM_BOUNDARIES,
    write_csv,
    write_json,
)


DEFAULT_OUTPUT_DIR = Path("saee_v1_2/universality_test/results/baselines")


BASELINES = {
    "marl_public_goods_q_learning": run_marl_public_goods,
    "bond_percolation": run_bond_percolation,
    "sir_epidemic": run_sir_epidemic,
}


def run_suite(seeds: int, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_by_baseline = {}
    mean_curves = {}
    for name, runner in BASELINES.items():
        rows = []
        curves = []
        for offset in range(seeds):
            result = runner(740000 + offset)
            rows.append(result)
            curves.append(result["phi_curve"])
        rows_by_baseline[name] = rows
        mean_curves[name] = mean_curve(curves)

    summary = {
        "schema": "saee.universality_test.baseline_suite_summary.v1",
        "num_seeds": seeds,
        "baselines": {
            "marl_public_goods_q_learning": {
                **summarize_binary_runs(rows_by_baseline["marl_public_goods_q_learning"]),
                "native_metrics": ["team_return", "policy_entropy"],
                "phi_compatibility": True,
            },
            "bond_percolation": {
                **summarize_binary_runs(rows_by_baseline["bond_percolation"]),
                "native_metrics": ["giant_component_fraction", "occupation_probability"],
                "phi_compatibility": "partial",
            },
            "sir_epidemic": {
                **summarize_binary_runs(rows_by_baseline["sir_epidemic"]),
                "native_metrics": ["infected_fraction", "outbreak_size"],
                "phi_compatibility": "partial",
            },
        },
        "cross_model_similarity_matrix_csv": "results/baselines/baseline_similarity_matrix.csv",
        "mean_phi_curves": mean_curves,
        "claim_boundaries": CLAIM_BOUNDARIES,
    }

    summary_path = output_dir / "baseline_suite_summary.json"
    matrix_path = output_dir / "baseline_similarity_matrix.csv"
    comparison_path = output_dir / "baseline_comparison.svg"
    heatmap_path = output_dir / "baseline_heatmaps.svg"
    manifest_path = output_dir / "baseline_manifest.json"
    write_json(summary_path, summary)
    write_csv(
        matrix_path,
        model_similarity(mean_curves),
        fields=["model_a", "model_b", "curve_similarity"],
    )
    write_baseline_comparison(comparison_path, mean_curves)
    write_baseline_heatmaps(heatmap_path, summary)
    write_json(
        manifest_path,
        {
            "schema": "saee.universality_test.baseline_manifest.v1",
            "created_files": [
                str(summary_path),
                str(matrix_path),
                str(comparison_path),
                str(heatmap_path),
                str(manifest_path),
            ],
            "num_seeds": seeds,
            "baselines": list(BASELINES),
            "forbidden_core_modified": False,
            "claim_boundaries": CLAIM_BOUNDARIES,
        },
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=120)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    summary = run_suite(seeds=args.seeds, output_dir=output_dir)
    print(
        "SAEE_BASELINES: "
        + " ".join(
            f"{name}_p={item['transition_probability']}"
            for name, item in summary["baselines"].items()
        )
        + f" output={output_dir}"
    )


if __name__ == "__main__":
    main()
