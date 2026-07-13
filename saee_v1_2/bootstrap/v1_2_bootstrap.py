#!/usr/bin/env python3
"""Bootstrap SAEE v1.2 empirical alignment outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.experiments.run_saee_experiment import run_experiment


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_summary(summary: dict[str, object]) -> None:
    validation = summary.get("validation", {})
    if not isinstance(validation, dict):
        raise SystemExit("SAEE_V1_2_BOOTSTRAP: FAIL missing validation map")
    failed = [key for key, value in validation.items() if value is not True]
    if failed:
        raise SystemExit("SAEE_V1_2_BOOTSTRAP: FAIL " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generations", type=int, default=24)
    parser.add_argument("--population-size", type=int, default=12)
    parser.add_argument("--dimensions", type=int, default=3)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--baseline-seed", type=int, default=29)
    parser.add_argument(
        "--output-dir",
        default="saee_v1_2/results/demo-run",
        help="Local output directory for reproducible empirical reports.",
    )
    args = parser.parse_args()

    record = run_experiment(
        generations=args.generations,
        population_size=args.population_size,
        dimensions=args.dimensions,
        seed=args.seed,
        baseline_seed=args.baseline_seed,
    )
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    _write_json(output_dir / "experiment_summary.json", record["summary"])
    _write_json(output_dir / "simulation_logs" / "saee_trace.json", record["saee_record"])
    _write_json(output_dir / "metric_reports" / "metric_report.json", record["metric_report"])
    _write_json(output_dir / "metric_reports" / "attractor_report.json", record["attractor_report"])
    _write_json(
        output_dir / "metric_reports" / "regime_transition_report.json",
        record["regime_transition_report"],
    )
    _write_json(output_dir / "metric_reports" / "coupling_report.json", record["coupling_report"])
    _write_json(
        output_dir / "comparison_reports" / "baseline_comparison.json",
        record["comparison_report"],
    )
    validate_summary(record["summary"])
    summary = record["summary"]
    print(
        "SAEE_V1_2_BOOTSTRAP: PASS "
        f"generations={summary['generations']} "
        f"metrics={summary['metric_count']} "
        f"attractors={summary['attractor_count']} "
        f"transitions={summary['regime_transition_frequency']} "
        f"coupling={summary['coupling_strength_coefficient']} "
        f"baselines={summary['baseline_count']} "
        f"output={output_dir}"
    )


if __name__ == "__main__":
    main()
