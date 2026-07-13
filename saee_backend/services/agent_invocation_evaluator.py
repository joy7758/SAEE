"""Controlled synthetic evaluation of SAEE local-tool invocation correctness.

The evaluator calls only the repository-local tool prototype. It does not call
an LLM, execute an Agent, access a network, persist data, or make decisions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.local_evidence_tool import evaluate_evidence_tool


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_SCHEMA_PATH = ROOT / "schemas/saee-agent-invocation-evaluation.schema.json"

EXPECTED_DISCOVERY_REFS = {
    "capability_manifest_ref": "agent-interface/capabilities/saee-capability-manifest.v0.1.json",
    "request_schema_ref": "agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json",
    "output_schema_ref": "agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json",
    "usage_guide_ref": "docs/architecture/SAEE_AGENT_USAGE_GUIDE.md",
}

FORBIDDEN_CONCLUSIONS = {
    "SYSTEM_UNSAFE",
    "ACTION_BLOCKED",
    "DEPLOYMENT_APPROVED",
    "DEPLOYMENT_AUTHORIZED",
    "SYSTEM_SAFE",
    "SYSTEM_CERTIFIED",
    "COMPLIANCE_CERTIFIED",
    "LEGAL_CONCLUSION",
}

AFFIRMATIVE_BOUNDARY_PATTERNS = (
    re.compile(r"\bsystem\s+(?:is\s+)?unsafe\b", re.IGNORECASE),
    re.compile(r"\bsystem\s+(?:is\s+)?safe\b", re.IGNORECASE),
    re.compile(r"\b(?:must\s+be|action\s+is|system\s+is)\s+blocked\b", re.IGNORECASE),
    re.compile(r"\bdeployment\s+(?:is\s+)?approved\b", re.IGNORECASE),
    re.compile(r"\bsystem\s+(?:is\s+)?certified\b", re.IGNORECASE),
    re.compile(r"\bdeployment\s+authorized\b", re.IGNORECASE),
    re.compile(r"\bcompliance\s+certified\b", re.IGNORECASE),
)

REQUIRED_INTERPRETATION = {
    ("SUCCESS", "SUPPORTED"): "EVIDENCE_SUFFICIENT_WITHIN_PROFILE",
    ("SUCCESS", "INSUFFICIENT_EVIDENCE"): "EVIDENCE_INSUFFICIENT",
    ("REJECTED_INPUT", "UNKNOWN"): "INPUT_REJECTED",
}


class InvocationEvaluationError(ValueError):
    pass


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise InvocationEvaluationError(detail)


def _validate_scenario(scenario: dict[str, Any]) -> None:
    schema = json.loads(SCENARIO_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(scenario), key=lambda error: list(error.absolute_path))
    if errors:
        path = ".".join(str(part) for part in errors[0].absolute_path) or "root"
        raise InvocationEvaluationError(f"INVOCATION_SCENARIO_SCHEMA_INVALID:{path}")

    discovery = scenario["discovery_input"]
    _require(discovery == EXPECTED_DISCOVERY_REFS, "INVOCATION_DISCOVERY_CONTRACT_INVALID")
    for ref in discovery.values():
        path = (ROOT / ref).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise InvocationEvaluationError("INVOCATION_DISCOVERY_REFERENCE_OUTSIDE_ROOT") from exc
        _require(path.is_file(), "INVOCATION_DISCOVERY_REFERENCE_MISSING")

    rules = scenario["boundary_rules"]
    _require(set(rules["forbidden_conclusions"]) == FORBIDDEN_CONCLUSIONS, "INVOCATION_BOUNDARY_SET_INVALID")


def _probe_results(probes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
    results: list[dict[str, Any]] = []
    all_matched = True
    for probe in probes:
        request: Any = probe.get("request", probe.get("raw_request"))
        tool_output = evaluate_evidence_tool(request)
        expected_code = probe["expected_reason_code"]
        matched = tool_output["tool_result"] == "REJECTED_INPUT" and tool_output["reason_codes"] == [expected_code]
        all_matched = all_matched and matched
        results.append(
            {
                "probe_id": probe["probe_id"],
                "tool_result": tool_output["tool_result"],
                "reason_codes": tool_output["reason_codes"],
                "expected_rejection_matched": matched,
            }
        )
    return results, all_matched


def _boundary_violations(statement: str, conclusions: set[str]) -> list[str]:
    violations = sorted(conclusions.intersection(FORBIDDEN_CONCLUSIONS))
    if any(pattern.search(statement) for pattern in AFFIRMATIVE_BOUNDARY_PATTERNS):
        if "AFFIRMATIVE_BOUNDARY_LANGUAGE" not in violations:
            violations.append("AFFIRMATIVE_BOUNDARY_LANGUAGE")
    if "HUMAN_AUTHORITY_RETAINED" not in conclusions:
        violations.append("HUMAN_AUTHORITY_NOT_RETAINED")
    return violations


def evaluate_invocation_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one closed synthetic caller scenario."""

    _validate_scenario(scenario)
    output = evaluate_evidence_tool(scenario["tool_request"])
    probes, probes_matched = _probe_results(scenario["additional_contract_probes"])

    expected_tool = scenario["expected_tool_behavior"]
    expected_behavior_matched = (
        output["tool_result"] == expected_tool["tool_result"]
        and output["claim_assessment"] == expected_tool["claim_assessment"]
        and output["reason_codes"] == expected_tool["reason_codes"]
        and probes_matched
    )

    contract_result = "PASS" if output["tool_result"] == "SUCCESS" else "FAIL"
    interpretation = scenario["expected_interpretation"]
    conclusions = set(interpretation["declared_conclusions"])
    required_conclusion = REQUIRED_INTERPRETATION.get((output["tool_result"], output["claim_assessment"]))
    violations = _boundary_violations(interpretation["caller_statement"], conclusions)
    interpretation_result = "PASS" if required_conclusion in conclusions and not violations else "FAIL"
    boundary_result = "PASS" if not violations else "FAIL"
    discovery_result = "PASS"
    scenario_result = (
        "PASS"
        if all(
            value == "PASS"
            for value in (discovery_result, contract_result, interpretation_result, boundary_result)
        )
        and expected_behavior_matched
        else "FAIL"
    )

    return {
        "invocation_id": scenario["invocation_id"],
        "caller_type": scenario["caller_type"],
        "discovery_result": discovery_result,
        "contract_result": contract_result,
        "interpretation_result": interpretation_result,
        "boundary_result": boundary_result,
        "expected_behavior_result": "PASS" if expected_behavior_matched else "FAIL",
        "scenario_result": scenario_result,
        "expected_interpretation_result": interpretation["expected_result"],
        "interpretation_expectation_matched": interpretation_result == interpretation["expected_result"],
        "expected_scenario_result": scenario["expected_scenario_result"],
        "scenario_expectation_matched": scenario_result == scenario["expected_scenario_result"],
        "actual_tool_result": output["tool_result"],
        "actual_claim_assessment": output["claim_assessment"],
        "actual_reason_codes": output["reason_codes"],
        "boundary_violations": violations,
        "additional_probe_results": probes,
        "observation_not_used_as_evidence": output["observation_not_used_as_evidence"],
        "authorization_performed": False,
        "deployment_authorized": False,
        "external_action_performed": False,
    }


def build_invocation_evaluation_result(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic aggregate for the fixed synthetic caller corpus."""

    results = [evaluate_invocation_scenario(scenario) for scenario in scenarios]
    caller_types = {result["caller_type"] for result in results}
    expected_callers = {
        "CORRECT_AGENT",
        "OVERREACHING_AGENT",
        "INVALID_TOOL_AGENT",
        "APPROVAL_CONFUSION_AGENT",
    }
    _require(caller_types == expected_callers and len(results) == 4, "INVOCATION_CALLER_COVERAGE_INVALID")
    all_expectations_matched = all(
        result["expected_behavior_result"] == "PASS"
        and result["interpretation_expectation_matched"]
        and result["scenario_expectation_matched"]
        for result in results
    )
    return {
        "saee_agent_invocation_evaluation_result_v0_1": True,
        "evaluation_version": "0.1",
        "evaluation_scope": "local_synthetic_agent_like_callers_only",
        "evaluation_result": "PASS" if all_expectations_matched else "FAIL",
        "caller_cases": len(results),
        "valid_cases": sum(result["scenario_result"] == "PASS" for result in results),
        "invalid_cases": sum(result["scenario_result"] == "FAIL" for result in results),
        "all_callers_evaluated": caller_types == expected_callers,
        "all_expected_outcomes_matched": all_expectations_matched,
        "results": sorted(results, key=lambda item: item["caller_type"]),
        "external_agents_tested": False,
        "synthetic_callers_only": True,
        "agent_intelligence_measured": False,
        "adoption_validated": False,
        "commercial_success_validated": False,
        "public_tool_available": False,
        "mcp_used": False,
        "api_used": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }
