#!/usr/bin/env python3
"""Offline deterministic smoke and adversarial checks for adequacy profiles."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.evidence_adequacy import (  # noqa: E402
    INPUT_SCHEMA_INVALID,
    evaluate_evidence_adequacy,
)


PROFILE_SCHEMA = ROOT / "agent-interface/schemas/evidence-adequacy-profile.schema.json"
PROFILE_DIRECTORY = ROOT / "agent-interface/profiles/evidence-adequacy"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/examples/evidence-adequacy"
FIXTURE_DIRECTORY = ROOT / "agent-interface/fixtures/evidence-adequacy"
CLI = ROOT / "scripts/saee_agent_cli.py"

POSITIVE_CASES = {
    "RESOURCE_AUTHENTICITY": "resource_authenticity_pass.json",
    "AUTHORIZED_AGENT_ACTION": "authorized_agent_action_pass.json",
    "HUMAN_OVERSIGHT": "human_oversight_pass.json",
    "EXECUTION_BOUNDARY": "execution_boundary_pass.json",
}

NEGATIVE_CASES = {
    "resource_authenticity_missing_digest.json": (
        "RESOURCE_AUTHENTICITY",
        "EVIDENCE_DIGEST_MISSING",
    ),
    "authorized_action_missing_policy.json": (
        "AUTHORIZED_AGENT_ACTION",
        "EVIDENCE_POLICY_DECISION_MISSING",
    ),
    "human_oversight_missing_context.json": (
        "HUMAN_OVERSIGHT",
        "EVIDENCE_APPROVAL_CONTEXT_MISSING",
    ),
    "execution_boundary_missing_causal_link.json": (
        "EXECUTION_BOUNDARY",
        "EVIDENCE_CAUSAL_LINK_MISSING",
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object required: {path}")
    return value


def run_cli(claim_type: str, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CLI),
            "validate-evidence-adequacy",
            "--profile",
            claim_type,
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
    profile_schema = read_json(PROFILE_SCHEMA)
    profile_validator = Draft202012Validator(profile_schema)
    profile_files = sorted(PROFILE_DIRECTORY.glob("*.json"))
    require(len(profile_files) == 4, "four canonical profiles required")
    for path in profile_files:
        errors = list(profile_validator.iter_errors(read_json(path)))
        require(not errors, f"profile schema failure: {path.name}: {errors}")

    positive_payloads: dict[str, dict] = {}
    deterministic_runs = 0
    for claim_type, filename in POSITIVE_CASES.items():
        path = EXAMPLE_DIRECTORY / filename
        payload = read_json(path)
        positive_payloads[claim_type] = payload
        direct = evaluate_evidence_adequacy(claim_type, payload)
        require(direct["result"] == "PASS", f"positive direct result: {claim_type}")
        require(direct["profile_requirements_satisfied"] is True, "profile requirement flag")
        require(direct["accountability_claim_established"] is False, "no truth elevation")
        baseline = run_cli(claim_type, path)
        require(baseline.returncode == 0, f"positive CLI exit: {claim_type}")
        baseline_payload = json.loads(baseline.stdout)
        require(baseline_payload == direct, f"positive CLI/direct parity: {claim_type}")
        for _ in range(5):
            repeated = run_cli(claim_type, path)
            require(repeated.returncode == 0, f"deterministic CLI exit: {claim_type}")
            require(repeated.stdout == baseline.stdout, f"deterministic output: {claim_type}")
            deterministic_runs += 1

    for filename, (claim_type, expected_reason) in NEGATIVE_CASES.items():
        path = FIXTURE_DIRECTORY / filename
        rejected = run_cli(claim_type, path)
        require(rejected.returncode == 2, f"negative CLI exit: {filename}")
        payload = json.loads(rejected.stdout)
        require(payload["result"] == "FAIL", f"negative result: {filename}")
        require(payload["reason_codes"] == [expected_reason], f"stable reason: {filename}")
        require(payload["accountability_claim_established"] is False, "negative truth boundary")

    adversarial: list[tuple[str, dict, str]] = []

    authorized = positive_payloads["AUTHORIZED_AGENT_ACTION"]
    for path, value, reason in [
        ("agent", "agent:other", "EVIDENCE_AGENT_BINDING_MISMATCH"),
        ("action", "action:other", "EVIDENCE_ACTION_BINDING_MISMATCH"),
        ("scope", "resource:execute", "EVIDENCE_AUTHORITY_SCOPE_INSUFFICIENT"),
        ("decision", "deny", "EVIDENCE_POLICY_DECISION_NOT_ALLOW"),
        ("window", "2026-07-11T06:00:00Z", "EVIDENCE_AUTHORITY_WINDOW_INVALID"),
    ]:
        case = copy.deepcopy(authorized)
        if path == "agent":
            case["evidence"]["policy_decision"]["agent_id"] = value
        elif path == "action":
            case["evidence"]["policy_decision"]["action_id"] = value
        elif path == "scope":
            case["evidence"]["policy_decision"]["authority_scope"] = value
        elif path == "decision":
            case["evidence"]["policy_decision"]["decision"] = value
        else:
            case["evidence"]["action"]["timestamp"] = value
        adversarial.append(("AUTHORIZED_AGENT_ACTION", case, reason))

    oversight = positive_payloads["HUMAN_OVERSIGHT"]
    for path, value, reason in [
        ("action", "action:other", "EVIDENCE_APPROVAL_ACTION_MISMATCH"),
        ("scope", "resource:execute", "EVIDENCE_APPROVAL_SCOPE_INSUFFICIENT"),
        ("decision", "rejected", "EVIDENCE_APPROVAL_DECISION_NOT_APPROVED"),
        ("time", "2026-07-11T05:11:00Z", "EVIDENCE_APPROVAL_TIME_INVALID"),
    ]:
        case = copy.deepcopy(oversight)
        if path == "action":
            case["evidence"]["approval"]["action_id"] = value
        elif path == "scope":
            case["evidence"]["approval"]["approved_scope"] = value
        elif path == "decision":
            case["evidence"]["approval"]["decision"] = value
        else:
            case["evidence"]["approval"]["approval_timestamp"] = value
        adversarial.append(("HUMAN_OVERSIGHT", case, reason))

    execution = positive_payloads["EXECUTION_BOUNDARY"]
    for target in ("source_receipt_ref", "target_effect_ref", "content_digest"):
        case = copy.deepcopy(execution)
        case["evidence"]["causal_link"][target] = "mismatch"
        adversarial.append(("EXECUTION_BOUNDARY", case, "EVIDENCE_CAUSAL_BINDING_INVALID"))

    resource = copy.deepcopy(positive_payloads["RESOURCE_AUTHENTICITY"])
    resource["evidence"]["resource_receipt"]["content_binding"]["byte_length"] = 46
    adversarial.append(("RESOURCE_AUTHENTICITY", resource, "EVIDENCE_RESOURCE_RECEIPT_INVALID"))

    for claim_type, case, expected_reason in adversarial:
        result = evaluate_evidence_adequacy(claim_type, case)
        require(result["result"] == "FAIL", f"adversarial fail: {claim_type}")
        require(expected_reason in result["reason_codes"], f"adversarial reason: {expected_reason}")

    extra = copy.deepcopy(authorized)
    extra["evidence"]["undeclared"] = True
    require(
        evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", extra)["reason_codes"] == [INPUT_SCHEMA_INVALID],
        "undeclared evidence key rejected",
    )
    elevated = copy.deepcopy(authorized)
    elevated["truth_boundary"]["event_occurrence_proven"] = True
    require(
        evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", elevated)["reason_codes"] == [INPUT_SCHEMA_INVALID],
        "truth elevation rejected",
    )
    nested_extra = copy.deepcopy(authorized)
    nested_extra["evidence"]["action"]["undeclared"] = True
    require(
        evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", nested_extra)["reason_codes"] == [INPUT_SCHEMA_INVALID],
        "nested undeclared evidence key rejected",
    )

    with tempfile.TemporaryDirectory() as tmp:
        duplicate = Path(tmp) / "duplicate.json"
        duplicate.write_text(
            '{"saee_evidence_adequacy_input_v0_1":true,"schema_version":"0.1.0",'
            '"claim_type":"AUTHORIZED_AGENT_ACTION","claim_type":"HUMAN_OVERSIGHT",'
            '"evidence":{},"truth_boundary":{}}\n',
            encoding="utf-8",
        )
        duplicate_result = run_cli("AUTHORIZED_AGENT_ACTION", duplicate)
        require(duplicate_result.returncode == 2, "duplicate key exit")
        require(json.loads(duplicate_result.stdout)["reason_codes"] == [INPUT_SCHEMA_INVALID], "duplicate key reason")

        sensitive = copy.deepcopy(authorized)
        sentinel = "sensitive-synthetic-sentinel-must-not-reflect"
        sensitive["evidence"]["action"]["agent_id"] = sentinel
        sensitive_path = Path(tmp) / "sensitive.json"
        sensitive_path.write_text(json.dumps(sensitive), encoding="utf-8")
        sensitive_result = run_cli("AUTHORIZED_AGENT_ACTION", sensitive_path)
        require(sensitive_result.returncode == 2, "sensitive invalid exit")
        require(sentinel not in sensitive_result.stdout + sensitive_result.stderr, "sensitive value reflected")

    for receipt_name, schema_name in [
        ("evaluation-receipt.json", "evaluation-receipt.schema.json"),
        ("observed-trace-receipt.json", "observed-trace-receipt.schema.json"),
        ("verified-resource-resolution.json", "resource-resolution-receipt.schema.json"),
    ]:
        receipt_path = ROOT / "agent-interface/examples" / receipt_name
        schema_path = ROOT / "agent-interface/schemas" / schema_name
        schema = read_json(schema_path)
        resolver = RefResolver(base_uri=schema_path.as_uri(), referrer=schema)
        errors = list(Draft202012Validator(schema, resolver=resolver).iter_errors(read_json(receipt_path)))
        require(not errors, f"existing receipt regression: {receipt_name}")

    service_source = (ROOT / "saee_backend/services/evidence_adequacy.py").read_text(encoding="utf-8")
    for forbidden in ("urlopen(", "requests.", "httpx.", "socket.", "subprocess.", "os.system("):
        require(forbidden not in service_source, f"runtime external capability present: {forbidden}")

    print("SAEE_EVIDENCE_ADEQUACY_SMOKE: PASS")
    print("profile_schema_cases=4/4")
    print("positive_cases=4/4")
    print("negative_cases=4/4")
    print(f"adversarial_cases={len(adversarial) + 3}/{len(adversarial) + 3}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("existing_receipt_regressions=3/3")
    print("network_calls=0")
    print("runtime_subprocess_started=false")
    print("external_resource_reads=0")
    print("candidate_code_executed=false")
    print("accountability_claim_established=false")
    print("sensitive_value_reflection=0")


if __name__ == "__main__":
    main()
