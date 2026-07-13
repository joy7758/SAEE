#!/usr/bin/env python3
"""Run and persist the fixed 3 x 5 security boundary reliability study."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rehearsal_runtime.multi_agent_runner import live_ark_clients
from saee_backend.services.rehearsal_runtime.security_reliability_study import build_security_report, run_security_reliability_suite

SCHEMA = ROOT / "agent-interface/reliability/saee-security-boundary-reliability-study.schema.v0.3.json"
RESULT = ROOT / "agent-interface/reliability/saee-security-boundary-reliability-result.v0.3.json"
REPORT = ROOT / "docs/research/SAEE_SECURITY_BOUNDARY_RELIABILITY_STUDY_V0_3.md"


def progress(agent: str, run_number: int, status: str) -> None:
    print(f"security_boundary_run agent={agent} run={run_number}/5 status={status}", flush=True)


def main() -> int:
    study = run_security_reliability_suite(live_ark_clients(), runs=5, progress=progress)
    errors = list(Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).iter_errors(study))
    if errors:
        raise ValueError(f"security reliability schema invalid: {errors[0].message}")
    RESULT.write_text(json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(build_security_report(study), encoding="utf-8")
    print("SAEE_SECURITY_BOUNDARY_RELIABILITY_STUDY_RESULT")
    print(f"study_complete={str(study['study_complete']).lower()}")
    print(f"total_runs_executed={study['total_runs_executed']}/{study['total_runs_requested']}")
    print(f"total_runs_completed={study['total_runs_completed']}/{study['total_runs_requested']}")
    print(f"total_contract_failed_runs={study['total_contract_failed_runs']}")
    for agent in study["agent_profiles"]:
        print(f"{agent['agent_profile']}={agent['completed_runs']}/{agent['run_count']}")
    print("security_certification_established=false")
    print("ranking_generated=false")
    print("production_ready=false")
    return 0 if study["study_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
