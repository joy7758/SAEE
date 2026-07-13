#!/usr/bin/env python3
"""Offline schema, CLI, semantic, and regression smoke for resource receipts."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)
from jsonschema import Draft202012Validator, FormatChecker, RefResolver


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.resource_resolution_receipt import (
    RESOURCE_DIGEST_INVALID,
    RESOURCE_EXECUTION_EFFECT_UNBOUND,
    RESOURCE_POLICY_DECISION_REQUIRED,
    RESOURCE_PUBLISHER_IDENTITY_REQUIRED,
    RESOURCE_RECEIPT_DIGEST_MISMATCH,
    RESOURCE_RESOLVED_URI_INVALID,
    RESOURCE_SCHEMA_INVALID,
    validate_resource_resolution_receipt,
)


SCHEMA = ROOT / "agent-interface/schemas/resource-resolution-receipt.schema.json"
POSITIVE = ROOT / "agent-interface/examples/verified-resource-resolution.json"
FIXTURE_DIR = ROOT / "agent-interface/fixtures/resource-resolution"
CLI = ROOT / "scripts/saee_agent_cli.py"
NEGATIVE_EXPECTATIONS = {
    "resource_missing_publisher_identity.json": RESOURCE_PUBLISHER_IDENTITY_REQUIRED,
    "resource_digest_mismatch_or_invalid.json": RESOURCE_DIGEST_INVALID,
    "resource_missing_policy_decision.json": RESOURCE_POLICY_DECISION_REQUIRED,
    "resource_unbound_execution_effect.json": RESOURCE_EXECUTION_EFFECT_UNBOUND,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_RESOURCE_RESOLUTION_RECEIPT_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.name} must contain an object")
    return value


def run_cli(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "validate-resource-resolution", "--input", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def schema_errors(validator: Draft202012Validator, value: object) -> list:
    return sorted(validator.iter_errors(value), key=lambda item: (list(item.absolute_path), item.message))


def main() -> None:
    schema = read_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    positive = read_json(POSITIVE)
    require(not schema_errors(validator, positive), "positive schema validation")

    outputs = [run_cli(POSITIVE) for _ in range(10)]
    require(all(result.returncode == 0 for result in outputs), "positive CLI exit code")
    require(len({result.stdout for result in outputs}) == 1, "positive CLI determinism")
    accepted = json.loads(outputs[0].stdout)
    require(accepted["valid"] is True and accepted["reason_codes"] == [], "positive acceptance")
    require(accepted["network_accessed"] is False, "positive network boundary")
    require(accepted["candidate_code_executed"] is False, "positive execution boundary")

    for name, expected_reason in NEGATIVE_EXPECTATIONS.items():
        path = FIXTURE_DIR / name
        fixture = read_json(path)
        if name == "resource_unbound_execution_effect.json":
            require(not schema_errors(validator, fixture), "semantic negative must pass structure")
        else:
            require(bool(schema_errors(validator, fixture)), f"{name} must fail schema")
        rejected = run_cli(path)
        require(rejected.returncode == 2, f"{name} CLI exit code")
        payload = json.loads(rejected.stdout)
        require(payload["valid"] is False, f"{name} valid false")
        require(payload["reason_codes"] == [expected_reason], f"{name} stable reason")
        require(payload["network_accessed"] is False, f"{name} network false")
        require(payload["candidate_code_executed"] is False, f"{name} execution false")

    adversarial: list[tuple[dict, str]] = []
    dangerous_uri = copy.deepcopy(positive)
    dangerous_uri["resolved_uri"] = "file:///tmp/synthetic-resource"
    adversarial.append((dangerous_uri, RESOURCE_RESOLVED_URI_INVALID))
    digest_mismatch = copy.deepcopy(positive)
    digest_mismatch["content_digest"] = "0" * 64
    adversarial.append((digest_mismatch, RESOURCE_DIGEST_INVALID))
    receipt_tamper = copy.deepcopy(positive)
    receipt_tamper["requested_resource"] = "repository:synthetic-publisher/other-resource@v0.1.0"
    adversarial.append((receipt_tamper, RESOURCE_RECEIPT_DIGEST_MISMATCH))
    execution_claim = copy.deepcopy(positive)
    execution_claim["authorization_boundary"]["execute"] = True
    adversarial.append((execution_claim, RESOURCE_SCHEMA_INVALID))
    extra_field = copy.deepcopy(positive)
    extra_field["undeclared"] = True
    adversarial.append((extra_field, RESOURCE_SCHEMA_INVALID))
    host_mismatch = copy.deepcopy(positive)
    host_mismatch["registry_or_host"] = "other.example.invalid"
    adversarial.append((host_mismatch, RESOURCE_RESOLVED_URI_INVALID))
    path_traversal = copy.deepcopy(positive)
    path_traversal["resolved_uri"] = "https://code.example.invalid/synthetic-publisher/../synthetic-resource.git"
    adversarial.append((path_traversal, RESOURCE_RESOLVED_URI_INVALID))

    for uri in (
        "data:text/plain,synthetic",
        "ssh://code.example.invalid/synthetic-resource.git",
        "git+ssh://code.example.invalid/synthetic-resource.git",
        "https://user:secret@code.example.invalid/synthetic-resource.git",
        "https://code.example.invalid/synthetic-resource.git?token=synthetic",
        "https://code.example.invalid/synthetic-resource.git#fragment",
        "https://code.example.invalid/%2e%2e/synthetic-resource.git",
        "https://code.example.invalid/synthetic\\resource.git",
        "https://例子.invalid/synthetic-resource.git",
        "https://code.example.invalid/./synthetic-resource.git",
        "https://code.example.invalid//synthetic-resource.git",
        "https://code.example.invalid:443/synthetic-resource.git",
    ):
        value = copy.deepcopy(positive)
        value["resolved_uri"] = uri
        adversarial.append((value, RESOURCE_RESOLVED_URI_INVALID))

    invalid_padding = copy.deepcopy(positive)
    invalid_padding["content_binding"]["inline_base64"] += "="
    adversarial.append((invalid_padding, RESOURCE_DIGEST_INVALID))
    wrong_length = copy.deepcopy(positive)
    wrong_length["content_binding"]["byte_length"] = 46
    adversarial.append((wrong_length, RESOURCE_DIGEST_INVALID))
    bad_timestamp = copy.deepcopy(positive)
    bad_timestamp["created_at"] = "not-a-timestamp"
    adversarial.append((bad_timestamp, RESOURCE_SCHEMA_INVALID))
    for flag in ("install", "import", "network", "permission_expansion"):
        value = copy.deepcopy(positive)
        value["authorization_boundary"][flag] = True
        adversarial.append((value, RESOURCE_SCHEMA_INVALID))
    for flag in positive["truth_boundary"]:
        value = copy.deepcopy(positive)
        value["truth_boundary"][flag] = True
        adversarial.append((value, RESOURCE_SCHEMA_INVALID))
    verified_publisher = copy.deepcopy(positive)
    verified_publisher["publisher_identity"]["claim_status"] = "verified"
    adversarial.append((verified_publisher, RESOURCE_SCHEMA_INVALID))
    executed_effect = copy.deepcopy(positive)
    executed_effect["external_effect"]["status"] = "executed"
    adversarial.append((executed_effect, RESOURCE_SCHEMA_INVALID))
    for index, (value, expected_reason) in enumerate(adversarial, 1):
        result = validate_resource_resolution_receipt(value)
        require(
            result["reason_codes"] == [expected_reason],
            f"adversarial case {index} expected {expected_reason} got {result['reason_codes']}",
        )

    with tempfile.TemporaryDirectory() as tmp:
        duplicate = Path(tmp) / "duplicate.json"
        duplicate.write_text('{"publisher_identity":{},"publisher_identity":{}}\n', encoding="utf-8")
        duplicate_result = run_cli(duplicate)
        require(duplicate_result.returncode == 2, "duplicate key exit code")
        require(json.loads(duplicate_result.stdout)["reason_codes"] == [RESOURCE_SCHEMA_INVALID], "duplicate key reason")

        sensitive = copy.deepcopy(positive)
        sentinel = "bearer-sensitive-synthetic-sentinel"
        sensitive["requested_resource"] = sentinel
        sensitive["content_digest"] = "invalid"
        sensitive_path = Path(tmp) / "sensitive.json"
        sensitive_path.write_text(json.dumps(sensitive), encoding="utf-8")
        sensitive_result = run_cli(sensitive_path)
        require(sensitive_result.returncode == 2, "sensitive invalid exit code")
        require(sentinel not in sensitive_result.stdout + sensitive_result.stderr, "sensitive value reflected")

    for receipt_name, schema_name in [
        ("evaluation-receipt.json", "evaluation-receipt.schema.json"),
        ("observed-trace-receipt.json", "observed-trace-receipt.schema.json"),
    ]:
        receipt_path = ROOT / "agent-interface/examples" / receipt_name
        old_schema_path = ROOT / "agent-interface/schemas" / schema_name
        old_schema = read_json(old_schema_path)
        resolver = RefResolver(base_uri=old_schema_path.as_uri(), referrer=old_schema)
        old_errors = sorted(
            Draft202012Validator(old_schema, resolver=resolver).iter_errors(read_json(receipt_path)),
            key=lambda item: list(item.absolute_path),
        )
        require(not old_errors, f"existing receipt regression: {receipt_name}")

    service_source = (ROOT / "saee_backend/services/resource_resolution_receipt.py").read_text(encoding="utf-8")
    for forbidden in ("urlopen(", "requests.", "httpx.", "socket.", "subprocess.", "os.system("):
        require(forbidden not in service_source, f"runtime external capability present: {forbidden}")

    print("SAEE_RESOURCE_RESOLUTION_RECEIPT_SMOKE: PASS")
    print("positive_cases=1/1")
    print("negative_cases=4/4")
    print(f"adversarial_cases={len(adversarial)}/{len(adversarial)}")
    print("deterministic_runs=10/10")
    print("existing_receipt_regressions=2/2")
    print("network_calls=0")
    print("runtime_subprocess_started=false")
    print("external_resource_reads=0")
    print("candidate_code_executed=false")
    print("sensitive_value_reflection=0")


if __name__ == "__main__":
    main()
