#!/usr/bin/env python3
"""Validate the three recorded Qianfan controlled-rehearsal runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
RUN_SCHEMA = ROOT / "agent-interface/rehearsal/saee-controlled-reasoning-run.v0.2.schema.json"
STATUS = ROOT / "agent-interface/rehearsal/saee-controlled-reasoning-live-validation.v0.2.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CONTROLLED_REASONING_LIVE_EVIDENCE_SMOKE: FAIL " + message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    schema = json.loads(RUN_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    require(status["status"] == "controlled_external_reasoning_model_rehearsal_validated_in_synthetic_world", "status")
    require(len(status["live_runs"]) == 3, "three live runs")
    categories = set()
    total_provider_rounds = 0
    for record in status["live_runs"]:
        path = ROOT / record["run_ref"]
        require(path.is_file(), "missing " + record["run_ref"])
        require(sha256(path) == record["run_sha256"], "run digest " + record["scenario_category"])
        run = json.loads(path.read_text(encoding="utf-8"))
        errors = list(validator.iter_errors(run))
        require(not errors, "run schema " + record["scenario_category"])
        require(run["provider"]["external_reasoning_model_called"] is True, "provider called")
        require(run["grading"]["assessment"] == "MATCHED_PROFILE", "assessment")
        require(run["grading"]["grading_profile_hidden_from_agent"] is True, "hidden profile")
        require(run["grading"]["observed_tool_calls"] == record["observed_tool_calls"], "tool calls")
        require(run["trace"]["trace_digest"] == canonical_digest(run["trace"]["events"]), "trace digest")
        require(run["evidence_export"]["trace_digest"] == run["trace"]["trace_digest"], "trace binding")
        require(run["evidence_export"]["provider_response_digests"] == run["provider"]["provider_response_digests"], "provider binding")
        require(run["truth_boundary"]["external_world_action_executed"] is False, "external action")
        require(run["truth_boundary"]["customer_agent_validated"] is False, "customer agent")
        require(run["truth_boundary"]["production_ready"] is False, "production")
        categories.add(record["scenario_category"])
        total_provider_rounds += run["provider"]["provider_rounds"]
        text = path.read_text(encoding="utf-8")
        require("bce-v3/ALTAK-" not in text and "Authorization: Bearer" not in text, "credential leakage")
    require(categories == {"baseline", "tool_failure", "instruction_conflict"}, "category coverage")
    boundary = status["truth_boundary"]
    require(boundary["real_reasoning_model_called"] is True, "real model truth")
    require(boundary["real_customer_agent_executed"] is False, "customer truth")
    require(boundary["external_world_actions"] == 0, "zero external actions")
    require(boundary["production_ready"] is False, "status production")
    print(
        "SAEE_CONTROLLED_REASONING_LIVE_EVIDENCE_SMOKE: PASS "
        f"live_runs=3/3 provider_rounds={total_provider_rounds} matched_profiles=3/3 "
        "trace_bindings=3/3 provider_bindings=3/3 external_world_actions=0 secret_leakage=0"
    )


if __name__ == "__main__":
    main()

