#!/usr/bin/env python3
"""Run the SAEE v1.0 long-horizon experiment layer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from saee_experiments.analysis.drift_monitor import DriftMonitor
from saee_experiments.analysis.emergence_observer import EmergenceObserver
from saee_experiments.analysis.report_generator import ExperimentReportGenerator
from saee_experiments.analysis.stability_analyzer import StabilityAnalyzer
from saee_experiments.logging.evolution_trace_logger import EvolutionTraceLogger
from saee_experiments.runner.experiment_runner import ExperimentRunner, parse_simple_yaml


DEFAULT_CONFIG = ROOT / "saee_experiments" / "configs" / "experiment_config.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v1.0 long-horizon experiment")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--generation-count", type=int, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = parse_simple_yaml(args.config)
    if args.generation_count is not None:
        config["generation_count"] = args.generation_count
    if args.output_dir is not None:
        config["output_dir"] = str(args.output_dir)
    output_dir = ROOT / str(config["output_dir"])

    experiment = ExperimentRunner().run(config, ROOT)
    trace_logger = EvolutionTraceLogger()
    trace = trace_logger.build_trace(experiment)
    stability = StabilityAnalyzer().analyze(experiment, trace)
    drift = DriftMonitor().monitor(experiment, trace)
    emergence = EmergenceObserver().observe(trace)

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_logger.write_jsonl(trace, output_dir / "evolution_trace.jsonl")
    (output_dir / "experiment_record.json").write_text(
        json.dumps(experiment, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "drift_report.json").write_text(
        json.dumps(drift, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "emergence_report.json").write_text(
        json.dumps(emergence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_generator = ExperimentReportGenerator()
    report_generator.write_reports(output_dir, experiment, stability, drift, emergence)
    report_generator.write_reports(ROOT / "saee_experiments", experiment, stability, drift, emergence)

    constitution = experiment["constitution"]
    if constitution["kernel_modified"]:
        raise SystemExit("SAEE_EXPERIMENT_BOOTSTRAP: FAIL kernel modified")
    if constitution["new_evolution_mechanics"]:
        raise SystemExit("SAEE_EXPERIMENT_BOOTSTRAP: FAIL new evolution mechanics introduced")
    if constitution["observer_feedback_into_kernel"]:
        raise SystemExit("SAEE_EXPERIMENT_BOOTSTRAP: FAIL observer feedback entered kernel")
    if stability["collapse_event_count"]:
        collapse_status = f"collapse_events={stability['collapse_event_count']}"
    else:
        collapse_status = "collapse_events=0"
    print(
        "SAEE_EXPERIMENT_BOOTSTRAP: PASS "
        f"generations={experiment['kernel_record']['generation_count']} "
        f"population={len(experiment['kernel_record']['population'])} "
        f"{collapse_status} "
        f"lineage_nodes={len(experiment['kernel_record']['lineage_dag']['nodes'])} "
        f"observation_only=True "
        f"output={output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
