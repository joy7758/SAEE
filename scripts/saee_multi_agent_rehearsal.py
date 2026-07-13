#!/usr/bin/env python3
"""Run the fixed three-model Ark comparison and write redacted local artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rehearsal_runtime.comparison_report import build_comparison_report
from saee_backend.services.rehearsal_runtime.multi_agent_runner import live_ark_clients, run_comparison_experiment

SCHEMA = ROOT / "agent-interface/benchmark/saee-controlled-agent-comparison.schema.v0.1.json"
RESULT = ROOT / "agent-interface/benchmark/saee-agent-comparison-result.v0.1.json"
REPORT = ROOT / "docs/product/SAEE_AGENT_REHEARSAL_COMPARISON_REPORT.md"


def main() -> int:
    experiment = run_comparison_experiment(live_ark_clients())
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(experiment))
    if errors:
        raise ValueError(f"comparison schema invalid: {errors[0].message}")
    RESULT.write_text(json.dumps(experiment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(build_comparison_report(experiment), encoding="utf-8")
    print("SAEE_MULTI_AGENT_REHEARSAL_RESULT")
    print(f"experiment_complete={str(experiment['experiment_complete']).lower()}")
    print(f"agents_tested={experiment['agents_tested']}/3")
    for item in experiment["agent_results"]:
        print(f"{item['agent_profile']}={item['status']}")
    print("ranking_generated=false")
    print("external_world_actions=false")
    print("production_ready=false")
    return 0 if experiment["experiment_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
