#!/usr/bin/env python3
"""Offline deterministic smoke for evaluate_agent_run Alpha."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services.agent_run_capability import AgentRunCapabilityError, evaluate_agent_run


SCENARIO_DIR = ROOT / "agent-interface/rehearsal/scenarios"
OUTPUT_SCHEMA = ROOT / "agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json"
CAPABILITY_MANIFEST = ROOT / "agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json"
SERVICE = ROOT / "saee_backend/services/agent_run_capability.py"
CLI = ROOT / "scripts/saee_evaluate_agent_run.py"
DOC = ROOT / "docs/architecture/SAEE_AGENT_CAPABILITY_ALPHA.md"
GATE = ROOT / "docs/strategy/SAEE_AGENT_CAPABILITY_ALPHA_RECOMMENDATION_GATE.md"

EXPECTED = {
    "baseline-metadata-inspection.json": "SUPPORTED",
    "tool-timeout-abstention.json": "SUPPORTED",
    "instruction-conflict-refusal.json": "INSUFFICIENT_EVIDENCE",
}


class AlphaSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AlphaSmokeError(detail)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def expect_capability_invalid(run: dict[str, Any], code: str) -> None:
    try:
        evaluate_agent_run(run)
    except AgentRunCapabilityError as exc:
        require(exc.code == code, f"reason code changed: {exc.code} != {code}")
        return
    raise AlphaSmokeError(f"invalid run accepted: {code}")


def main() -> None:
    for path in (OUTPUT_SCHEMA, CAPABILITY_MANIFEST, SERVICE, CLI, DOC, GATE):
        require(path.is_file(), f"required file missing: {path}")
    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(SERVICE).intersection(forbidden), "network or external execution module imported")

    output_validator = Draft202012Validator(load(OUTPUT_SCHEMA), format_checker=FormatChecker())
    capability = load(CAPABILITY_MANIFEST)
    require(capability["saee_evaluate_agent_run_capability_v0_1"] is True, "capability marker missing")
    require(capability["capability_id"] == "saee.evaluate_agent_run", "capability id invalid")
    require(capability["stage"] == "local_offline_alpha", "capability stage overclaimed")
    require(capability["input_contract"]["schema_ref"] == "agent-interface/rehearsal/saee-agent-rehearsal-run.v0.1.schema.json", "input contract drift")
    require(capability["output_contract"]["schema_ref"] == "agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json", "output contract drift")
    require(capability["output_contract"]["assessments"] == ["SUPPORTED", "INSUFFICIENT_EVIDENCE"], "assessment contract drift")
    require(capability["truth_boundary"]["local_alpha_available"] is True, "Alpha availability hidden")
    for field in ("public_api_available", "public_mcp_available", "real_external_agent_validated", "task_success_established", "agent_safety_established", "compliance_established", "deployment_authorized", "customer_validated", "production_ready"):
        require(capability["truth_boundary"][field] is False, f"capability truth overclaim: {field}")
    require(capability["recommended_next_pr"] == "No code PR - human review of the Design Partner protocol is required before external action", "next action drift")
    outputs: dict[str, dict[str, Any]] = {}
    runs: dict[str, dict[str, Any]] = {}
    for filename, expected in EXPECTED.items():
        run = run_task(SCENARIO_DIR / filename)
        result = evaluate_agent_run(run)
        output_validator.validate(result)
        require(result["assessment"] == expected, f"assessment mismatch: {filename}")
        require(result["profile_result"] == ("PASS" if expected == "SUPPORTED" else "FAIL"), f"profile result mismatch: {filename}")
        truth = result["truth_boundary"]
        require(truth["profile_requirements_evaluated"] is True, "evaluation truth missing")
        for field in ("accountability_claim_established", "task_success_established", "agent_safety_established", "compliance_established", "deployment_authorized", "real_external_agent_validated", "customer_validated", "production_ready"):
            require(truth[field] is False, f"authority truth promoted: {filename}:{field}")
        runs[filename] = run
        outputs[filename] = result

    denied = outputs["instruction-conflict-refusal.json"]
    require("EVIDENCE_POLICY_DECISION_NOT_ALLOW" in denied["reason_codes"], "denied policy reason missing")
    timeout = outputs["tool-timeout-abstention.json"]
    require(timeout["assessment"] == "SUPPORTED", "tool failure confused with evidence adequacy")
    require(timeout["truth_boundary"]["task_success_established"] is False, "tool failure promoted to task success")

    tampered = copy.deepcopy(runs["baseline-metadata-inspection.json"])
    tampered["trace"]["events"][0]["summary"] = "tampered"
    expect_capability_invalid(tampered, "AGENT_RUN_TRACE_DIGEST_INVALID")
    unbound_ref = copy.deepcopy(runs["baseline-metadata-inspection.json"])
    unbound_ref["evidence_export"]["trace_ref"] = "trace:other"
    expect_capability_invalid(unbound_ref, "AGENT_RUN_TRACE_REFERENCE_UNBOUND")
    unbound_digest = copy.deepcopy(runs["baseline-metadata-inspection.json"])
    unbound_digest["evidence_export"]["trace_digest"] = "0" * 64
    expect_capability_invalid(unbound_digest, "AGENT_RUN_EVIDENCE_EXPORT_UNBOUND")

    schema_invalid = copy.deepcopy(runs["baseline-metadata-inspection.json"])
    schema_invalid["truth_boundary"]["production_ready"] = True
    expect_capability_invalid(schema_invalid, "AGENT_RUN_SCHEMA_INVALID")

    overclaim = copy.deepcopy(outputs["baseline-metadata-inspection.json"])
    overclaim["truth_boundary"]["deployment_authorized"] = True
    try:
        output_validator.validate(overclaim)
    except ValidationError:
        pass
    else:
        raise AlphaSmokeError("deployment overclaim accepted")

    canonical = {name: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for name, value in outputs.items()}
    for _ in range(5):
        for filename in EXPECTED:
            repeated = evaluate_agent_run(run_task(SCENARIO_DIR / filename))
            require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical[filename], f"non-deterministic Alpha: {filename}")

    doc = DOC.read_text(encoding="utf-8")
    for marker in ("evaluate_agent_run", "task success", "public_api_available=false", "real_external_agent_validated=false"):
        require(marker in doc, f"documentation marker missing: {marker}")

    print("SAEE_AGENT_CAPABILITY_ALPHA_SMOKE: PASS")
    print("run_cases=3/3")
    print("supported_cases=2/2")
    print("insufficient_evidence_cases=1/1")
    print("invalid_cases=5/5")
    print("deterministic_runs=5/5")
    print("trace_binding_verified=3/3")
    print("existing_evidence_adequacy_reused=true")
    print("tool_failure_not_confused_with_task_success=true")
    print("evaluate_agent_run_available=true")
    print("public_api_available=false")
    print("public_mcp_available=false")
    print("real_external_agent_validated=false")
    print("deployment_authorized=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (AlphaSmokeError, AgentRunCapabilityError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(f"SAEE_AGENT_CAPABILITY_ALPHA_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
