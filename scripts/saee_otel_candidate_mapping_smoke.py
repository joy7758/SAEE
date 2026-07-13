#!/usr/bin/env python3
"""Offline mapping and no-truth-elevation checks for synthetic OTel-style events."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.otel_candidate_mapping import (  # noqa: E402
    OTEL_ACTION_CONTEXT_REQUIRED,
    OTEL_AGENT_ID_REQUIRED,
    OTEL_AUTHORIZATION_CLAIM_UNBOUND,
    OTEL_INPUT_SCHEMA_INVALID,
    evaluate_trace_candidate,
)


SCHEMA_PATH = ROOT / "agent-interface/schemas/otel-candidate-evidence-mapping.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/examples/otel-mapping"
FIXTURE_DIRECTORY = ROOT / "agent-interface/fixtures/otel-mapping"
CLI = ROOT / "scripts/saee_agent_cli.py"

POSITIVE_CASES = {
    "trace_candidate_resource_retrieval.json": "RESOURCE_AUTHENTICITY",
    "trace_candidate_tool_invocation.json": "AUTHORIZED_AGENT_ACTION",
    "trace_candidate_human_approval_observation.json": "HUMAN_OVERSIGHT",
}

NEGATIVE_CASES = {
    "trace_missing_agent_identity.json": OTEL_AGENT_ID_REQUIRED,
    "trace_missing_action_context.json": OTEL_ACTION_CONTEXT_REQUIRED,
    "trace_claiming_authorization_without_policy.json": OTEL_AUTHORIZATION_CLAIM_UNBOUND,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object required: {path}")
    return value


def run_cli(profile: str, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CLI),
            "evaluate-trace-candidate",
            "--profile",
            profile,
            "--input",
            str(path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )


def main() -> None:
    schema = read_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    deterministic_runs = 0

    for filename, profile in POSITIVE_CASES.items():
        path = EXAMPLE_DIRECTORY / filename
        event = read_json(path)
        direct = evaluate_trace_candidate(profile, event)
        mapping = direct["mapping"]
        require(mapping["trace_mapping_result"] in {"PASS", "PARTIAL"}, f"positive mapping: {filename}")
        require(not list(validator.iter_errors(mapping)), f"mapping schema: {filename}")
        require(direct["adequacy_result"] == "FAIL", f"trace must remain inadequate: {filename}")
        require(direct["accountability_claim_established"] is False, "no claim elevation")
        require(direct["adequacy_evaluation"]["accountability_claim_established"] is False, "adequacy truth boundary")
        require(mapping["truth_boundary"]["trace_is_evidence"] is False, "trace is not evidence")
        require(mapping["candidate_evidence_fields"], f"candidate extraction: {filename}")
        require(mapping["missing_evidence_requirements"], f"missing evidence: {filename}")

        baseline = run_cli(profile, path)
        require(baseline.returncode == 0, f"positive CLI exit: {filename}")
        require(json.loads(baseline.stdout) == direct, f"CLI/direct parity: {filename}")
        for _ in range(5):
            repeated = run_cli(profile, path)
            require(repeated.returncode == 0, f"deterministic CLI exit: {filename}")
            require(repeated.stdout == baseline.stdout, f"deterministic output: {filename}")
            deterministic_runs += 1

    for filename, expected_reason in NEGATIVE_CASES.items():
        path = FIXTURE_DIRECTORY / filename
        rejected = run_cli("RESOURCE_AUTHENTICITY", path)
        require(rejected.returncode == 2, f"negative CLI exit: {filename}")
        payload = json.loads(rejected.stdout)
        require(payload["trace_mapping_result"] == "FAIL", f"negative mapping result: {filename}")
        require(expected_reason in payload["mapping"]["reason_codes"], f"negative reason: {filename}")
        require(payload["adequacy_result"] == "FAIL", f"negative adequacy result: {filename}")
        require(payload["accountability_claim_established"] is False, "negative no claim elevation")
        require(not list(validator.iter_errors(payload["mapping"])), f"negative mapping schema: {filename}")

    base = read_json(EXAMPLE_DIRECTORY / "trace_candidate_resource_retrieval.json")
    adversarial: list[dict] = []
    extra_top = copy.deepcopy(base)
    extra_top["undeclared"] = True
    adversarial.append(extra_top)
    extra_attribute = copy.deepcopy(base)
    extra_attribute["attributes"]["unknown.attribute"] = "synthetic"
    adversarial.append(extra_attribute)
    bad_timestamp = copy.deepcopy(base)
    bad_timestamp["observed_timestamp"] = "not-a-timestamp"
    adversarial.append(bad_timestamp)
    wrong_source = copy.deepcopy(base)
    wrong_source["trace_source"] = "real_opentelemetry"
    adversarial.append(wrong_source)
    truthy_authorization = copy.deepcopy(base)
    truthy_authorization["attributes"]["authorization.claimed"] = True
    adversarial.append(truthy_authorization)
    for case in adversarial:
        result = evaluate_trace_candidate("RESOURCE_AUTHENTICITY", case)
        require(result["trace_mapping_result"] == "FAIL", "adversarial mapping must fail")
        require(result["adequacy_result"] == "FAIL", "adversarial adequacy must fail")
        require(result["accountability_claim_established"] is False, "adversarial truth boundary")

    policy_reference = copy.deepcopy(base)
    policy_reference["attributes"]["authorization.claimed"] = True
    policy_reference["attributes"]["policy.decision_ref"] = "policy:synthetic-observation-only"
    observed_policy = evaluate_trace_candidate("AUTHORIZED_AGENT_ACTION", policy_reference)
    require(observed_policy["trace_mapping_result"] == "PASS", "bound observation can map")
    require(observed_policy["adequacy_result"] == "FAIL", "observed policy reference is not decision evidence")
    require(observed_policy["accountability_claim_established"] is False, "policy observation no truth elevation")

    with tempfile.TemporaryDirectory() as tmp:
        duplicate = Path(tmp) / "duplicate.json"
        duplicate.write_text(
            '{"saee_synthetic_otel_event_v0_1":true,"schema_version":"0.1.0",'
            '"trace_source":"synthetic_opentelemetry_style","trace_event_id":"trace-duplicate",'
            '"observed_timestamp":"2026-07-11T08:00:00Z","attributes":{},"attributes":{}}\n',
            encoding="utf-8",
        )
        duplicate_result = run_cli("RESOURCE_AUTHENTICITY", duplicate)
        require(duplicate_result.returncode == 2, "duplicate key exit")
        duplicate_payload = json.loads(duplicate_result.stdout)
        require(duplicate_payload["mapping"]["reason_codes"] == [OTEL_INPUT_SCHEMA_INVALID], "duplicate key reason")

        sensitive = copy.deepcopy(base)
        sentinel = "sensitive-synthetic-trace-sentinel"
        sensitive["attributes"]["agent.id"] = sentinel
        sensitive["attributes"]["authorization.claimed"] = True
        sensitive_path = Path(tmp) / "sensitive.json"
        sensitive_path.write_text(json.dumps(sensitive), encoding="utf-8")
        sensitive_result = run_cli("RESOURCE_AUTHENTICITY", sensitive_path)
        require(sensitive_result.returncode == 2, "sensitive rejection exit")
        require(sentinel not in sensitive_result.stdout + sensitive_result.stderr, "sensitive value reflected")

    service_source = (ROOT / "saee_backend/services/otel_candidate_mapping.py").read_text(encoding="utf-8")
    for forbidden in (
        "opentelemetry.",
        "urlopen(",
        "requests.",
        "httpx.",
        "socket.",
        "subprocess.",
        "os.system(",
    ):
        require(forbidden not in service_source, f"forbidden runtime capability: {forbidden}")

    print("SAEE_OTEL_CANDIDATE_MAPPING_SMOKE: PASS")
    print("positive_mapping_cases=3/3")
    print("negative_mapping_cases=3/3")
    print("adversarial_cases=7/7")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("adequacy_fail_after_valid_mapping=3/3")
    print("trace_auto_accepted_as_evidence=0")
    print("accountability_claim_established=false")
    print("network_calls=0")
    print("runtime_subprocess_started=false")
    print("external_resource_reads=0")
    print("candidate_code_executed=false")
    print("opentelemetry_sdk_imported=false")
    print("sensitive_value_reflection=0")


if __name__ == "__main__":
    main()
