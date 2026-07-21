#!/usr/bin/env python3
"""Validate the three recorded Qianfan controlled-rehearsal runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
RUN_SCHEMA = ROOT / "agent-interface/rehearsal/saee-controlled-reasoning-run.v0.2.schema.json"
STATUS = ROOT / "agent-interface/rehearsal/saee-controlled-reasoning-live-validation.v0.2.json"


class EvidenceInvalid(RuntimeError):
    """Raised when supplied external Provider evidence is invalid."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceInvalid(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-evidence",
        action="store_true",
        help="Fail with NOT_AVAILABLE when the external Provider evidence is absent.",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        default=ROOT,
        help="Root used to resolve run_ref paths; defaults to the repository root.",
    )
    return parser.parse_args()


def validate_evidence(evidence_root: Path) -> tuple[int, int]:
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    schema = json.loads(RUN_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    require(status["status"] == "controlled_external_reasoning_model_rehearsal_validated_in_synthetic_world", "status")
    require(len(status["live_runs"]) == 3, "three live runs")
    categories = set()
    total_provider_rounds = 0
    for record in status["live_runs"]:
        path = evidence_root / record["run_ref"]
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
    return len(status["live_runs"]), total_provider_rounds


def main() -> None:
    args = parse_args()
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    evidence_root = args.evidence_root.resolve()
    expected_paths = [evidence_root / record["run_ref"] for record in status["live_runs"]]
    present_count = sum(path.is_file() for path in expected_paths)
    require_evidence = args.require_evidence or os.environ.get("SAEE_PROVIDER_EVIDENCE_MODE") == "required"

    if present_count == 0:
        if require_evidence:
            print("external_provider_evidence_status=NOT_AVAILABLE")
            print("EXTERNAL_EVIDENCE_NOT_AVAILABLE", file=sys.stderr)
            raise SystemExit(1)
        print("external_provider_evidence_status=NOT_REQUIRED")
        print("external_provider_evidence_verified=false")
        print(
            "SAEE_CONTROLLED_REASONING_LIVE_EVIDENCE_SMOKE: PASS "
            "live_runs=0/3 normal_check_requires_external_provider_evidence=false"
        )
        return

    if present_count != len(expected_paths):
        print("external_provider_evidence_status=PRESENT_UNVERIFIED")
        print(
            "SAEE_CONTROLLED_REASONING_LIVE_EVIDENCE_SMOKE: FAIL "
            f"partial external evidence present={present_count}/{len(expected_paths)}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print("external_provider_evidence_status=PRESENT_UNVERIFIED")
    try:
        live_run_count, total_provider_rounds = validate_evidence(evidence_root)
    except (EvidenceInvalid, json.JSONDecodeError, OSError, KeyError, TypeError) as exc:
        print("external_provider_evidence_status=INVALID")
        print("SAEE_CONTROLLED_REASONING_LIVE_EVIDENCE_SMOKE: FAIL " + str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    print("external_provider_evidence_status=VERIFIED")
    print(
        "SAEE_CONTROLLED_REASONING_LIVE_EVIDENCE_SMOKE: PASS "
        f"live_runs={live_run_count}/3 provider_rounds={total_provider_rounds} matched_profiles=3/3 "
        "trace_bindings=3/3 provider_bindings=3/3 external_world_actions=0 secret_leakage=0"
    )


if __name__ == "__main__":
    main()
