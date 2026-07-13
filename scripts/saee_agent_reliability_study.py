#!/usr/bin/env python3
"""Execute the fixed 3 x 10 Ark reliability study and write redacted artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rehearsal_runtime.multi_agent_runner import live_ark_clients
from saee_backend.services.rehearsal_runtime.reliability_analyzer import analyze_reliability_study, build_reliability_report
from saee_backend.services.rehearsal_runtime.reliability_runner import run_reliability_suite

SCHEMA = ROOT / "agent-interface/reliability/saee-agent-reliability-study.schema.v0.1.json"
RESULT = ROOT / "agent-interface/reliability/saee-agent-reliability-result.v0.1.json"
REPORT = ROOT / "docs/product/SAEE_AGENT_RELIABILITY_STUDY_REPORT.md"


def progress(agent: str, run_number: int, status: str) -> None:
    print(f"reliability_run agent={agent} run={run_number}/10 status={status}", flush=True)


def main() -> int:
    base = run_reliability_suite(live_ark_clients(), runs=10, progress=progress)
    study = analyze_reliability_study(base)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(study))
    if errors:
        raise ValueError(f"reliability schema invalid: {errors[0].message}")
    RESULT.write_text(json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(build_reliability_report(study), encoding="utf-8")
    print("SAEE_AGENT_RELIABILITY_STUDY_RESULT")
    print(f"study_complete={str(study['study_complete']).lower()}")
    print(f"total_runs_executed={study['total_runs_executed']}/{study['total_runs_requested']}")
    print(f"total_runs_completed={study['total_runs_completed']}/{study['total_runs_requested']}")
    print(f"total_contract_failed_runs={study['total_contract_failed_runs']}")
    for agent in study["agent_profiles"]:
        print(f"{agent['agent_profile']}={agent['completed_runs']}/{agent['run_count']}")
    print("ranking_generated=false")
    print("reliability_probability_estimated=false")
    print("external_world_actions=false")
    print("production_ready=false")
    return 0 if study["study_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
