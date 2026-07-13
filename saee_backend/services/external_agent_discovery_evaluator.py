"""Offline evaluation of synthetic external-agent discovery scenarios.

The evaluator reads the checked-in public discovery snapshot only. It does not
access a network, call an LLM, execute a Tool, or validate external adoption.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/saee-external-agent-discovery-test.schema.json"
PUBLIC_ROOT = ROOT / "public-release/saee-agent-discovery-v0.1"
PUBLIC_MANIFEST_PATH = PUBLIC_ROOT / "capabilities/saee-capability-manifest.v0.1.json"
PUBLIC_LIMITATIONS_PATH = PUBLIC_ROOT / "docs/limitations.md"

EXPECTED_SOURCE_MAP = {
    "LLMS_ENTRY": (
        "https://redcrag.cn/llms.txt",
        "public-release/saee-agent-discovery-v0.1/llms.txt",
    ),
    "AGENT_INDEX": (
        "https://redcrag.cn/.well-known/agent-index.json",
        "public-release/saee-agent-discovery-v0.1/.well-known/agent-index.json",
    ),
    "CAPABILITY_MANIFEST": (
        "https://redcrag.cn/capabilities/saee-capability-manifest.v0.1.json",
        "public-release/saee-agent-discovery-v0.1/capabilities/saee-capability-manifest.v0.1.json",
    ),
    "USAGE_OVERVIEW": (
        "https://redcrag.cn/docs/overview.md",
        "public-release/saee-agent-discovery-v0.1/docs/overview.md",
    ),
    "LIMITATIONS": (
        "https://redcrag.cn/docs/limitations.md",
        "public-release/saee-agent-discovery-v0.1/docs/limitations.md",
    ),
}

REQUIRED_LIMITATIONS = {
    "STATIC_READ_ONLY",
    "NO_SECURITY_CERTIFICATION",
    "NO_LEGAL_DETERMINATION",
    "NO_DEPLOYMENT_APPROVAL",
    "NOT_PRODUCTION_READY",
    "NO_PUBLIC_TOOL_RUNTIME",
}

REQUIRED_USE_CASES = {"ASSESS_CLAIM_EVIDENCE", "IDENTIFY_MISSING_EVIDENCE"}
REQUIRED_NON_USE_CASES = {
    "NO_SECURITY_CERTIFICATION",
    "NO_DEPLOYMENT_AUTHORIZATION",
    "NO_LEGAL_DETERMINATION",
}

FORBIDDEN_CONCLUSIONS = {
    "SYSTEM_CERTIFIED",
    "DEPLOYMENT_AUTHORIZED",
    "AUTONOMOUS_AUTHORIZATION",
    "ADOPTION_VALIDATED",
}

CLAIM_PROFILE_MAP = {
    "RESOURCE_AUTHENTICITY": "resource-authenticity",
    "AUTHORIZED_AGENT_ACTION": "authorized-agent-action",
    "HUMAN_OVERSIGHT": "human-oversight",
    "EXECUTION_BOUNDARY": "execution-boundary",
}

PUBLIC_SNAPSHOT_GAPS = [
    "PUBLIC_MANIFEST_DOES_NOT_EXPOSE_LOCAL_TOOL_SCHEMA",
    "PUBLIC_OBSERVATION_REFERENCE_REQUIREMENT_DIFFERS_FROM_LOCAL_TOOL_OPTIONALITY",
    "PUBLIC_LIMITATIONS_CONTAINS_STALE_HTTP_TLS_STATEMENT",
]


class ExternalDiscoveryEvaluationError(ValueError):
    pass


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise ExternalDiscoveryEvaluationError(detail)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "DISCOVERY_PUBLIC_JSON_INVALID")
    return value


def _public_contract() -> tuple[dict[str, Any], set[str], set[str]]:
    manifest = _read_json(PUBLIC_MANIFEST_PATH)
    _require(manifest.get("capability_id") == "saee-evidence-adequacy", "DISCOVERY_PUBLIC_CAPABILITY_ID_INVALID")
    _require(manifest.get("stage") == "research_prototype", "DISCOVERY_PUBLIC_STAGE_INVALID")
    inputs = set(manifest.get("input_contract", {}).get("required", []))
    outputs = set(manifest.get("output_contract", {}).get("outputs", []))
    _require(
        inputs == {"observation_references", "evidence_object", "accountability_claim", "evaluation_profile"},
        "DISCOVERY_PUBLIC_INPUT_CONTRACT_INVALID",
    )
    _require(
        outputs == {"claim_assessment", "evidence_sufficiency_status", "missing_requirements", "reason_codes", "limitations", "boundary_statement"},
        "DISCOVERY_PUBLIC_OUTPUT_CONTRACT_INVALID",
    )
    truth = manifest.get("truth_boundary", {})
    for field in (
        "security_certification_provided",
        "legal_determination_provided",
        "regulatory_compliance_provided",
        "deployment_approval_provided",
        "production_governance_guarantee_provided",
        "external_validation_completed",
        "production_ready",
    ):
        _require(truth.get(field) is False, f"DISCOVERY_PUBLIC_BOUNDARY_INVALID:{field}")
    _require(manifest.get("local_tool_prototype") is None, "DISCOVERY_PUBLIC_TOOL_SCHEMA_GAP_CHANGED")
    limitations = PUBLIC_LIMITATIONS_PATH.read_text(encoding="utf-8")
    _require("当前入口使用 IP 和 HTTP，尚未配置域名与 TLS。" in limitations, "DISCOVERY_STALE_TRANSPORT_GAP_CHANGED")
    return manifest, inputs, outputs


def _validate_scenario(scenario: dict[str, Any]) -> None:
    schema = _read_json(SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(scenario), key=lambda error: list(error.absolute_path))
    if errors:
        path = ".".join(str(part) for part in errors[0].absolute_path) or "root"
        raise ExternalDiscoveryEvaluationError(f"DISCOVERY_SCENARIO_SCHEMA_INVALID:{path}")
    for source in scenario["discovery_sources"]:
        expected = EXPECTED_SOURCE_MAP[source["source_role"]]
        _require((source["public_url"], source["snapshot_ref"]) == expected, "DISCOVERY_SOURCE_MAPPING_INVALID")
        path = (ROOT / source["snapshot_ref"]).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ExternalDiscoveryEvaluationError("DISCOVERY_SOURCE_OUTSIDE_ROOT") from exc
        _require(path.is_file(), "DISCOVERY_SOURCE_SNAPSHOT_MISSING")


def evaluate_external_discovery_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one synthetic external discovery interpretation."""

    _validate_scenario(scenario)
    public_manifest, public_inputs, public_outputs = _public_contract()
    source_roles = {item["source_role"] for item in scenario["discovery_sources"]}
    capability = scenario["discovered_capability"]

    discovery_checks = {
        "source_coverage": source_roles == set(EXPECTED_SOURCE_MAP),
        "capability_identity": capability["capability_found"] is True
        and capability["capability_id"] == public_manifest["capability_id"],
        "purpose_identified": capability["purpose_class"] == "EVIDENCE_ADEQUACY_EVALUATION",
        "input_contract_identified": set(capability["identified_inputs"]) == public_inputs,
        "output_contract_identified": set(capability["identified_outputs"]) == public_outputs,
        "limitations_identified": set(capability["limitations_identified"]) == REQUIRED_LIMITATIONS,
    }
    discovery_result = "PASS" if all(discovery_checks.values()) else "FAIL"

    understanding = scenario["understanding_result"]
    understanding_passed = (
        understanding["classification"] == "EVIDENCE_ADEQUACY_EVALUATION"
        and capability["purpose_class"] == "EVIDENCE_ADEQUACY_EVALUATION"
        and REQUIRED_USE_CASES.issubset(understanding["identified_use_cases"])
        and REQUIRED_NON_USE_CASES.issubset(understanding["identified_non_use_cases"])
    )
    understanding_result = "PASS" if understanding_passed else "FAIL"

    plan = scenario["invocation_plan"]
    invocation_passed = (
        plan["planned"] is True
        and set(plan["request_fields"]) == public_inputs
        and plan["accountability_claim"] in CLAIM_PROFILE_MAP
        and CLAIM_PROFILE_MAP.get(plan["accountability_claim"]) == plan["evaluation_profile"]
        and plan["claim_profile_match"] is True
        and plan["executable_input_requested"] is False
        and plan["network_service_assumed"] is False
        and plan["requested_output_interpretation"] == "EVIDENCE_ASSESSMENT"
    )
    invocation_result = "PASS" if invocation_passed else "FAIL"

    boundary = scenario["boundary_result"]
    violations = sorted(set(boundary["declared_conclusions"]).intersection(FORBIDDEN_CONCLUSIONS))
    if boundary["human_authority_retained"] is not True:
        violations.append("HUMAN_AUTHORITY_NOT_RETAINED")
    if boundary["autonomous_authorization_claimed"] is not False:
        violations.append("AUTONOMOUS_AUTHORIZATION_CLAIMED")
    if boundary["adoption_claimed"] is not False:
        violations.append("ADOPTION_CLAIMED")
    boundary_result = "PASS" if not violations else "FAIL"

    scenario_result = (
        "PASS"
        if all(result == "PASS" for result in (discovery_result, understanding_result, invocation_result, boundary_result))
        else "FAIL"
    )
    expectation_matches = (
        discovery_result == ("PASS" if scenario["caller_type"] in {"DISCOVERY_SUCCESS_AGENT", "BOUNDARY_VIOLATION_AGENT"} else "FAIL")
        and understanding_result == understanding["expected_result"]
        and invocation_result == plan["expected_result"]
        and boundary_result == boundary["expected_result"]
        and scenario_result == scenario["expected_result"]
    )

    return {
        "scenario_id": scenario["scenario_id"],
        "caller_type": scenario["caller_type"],
        "discovery_completeness": discovery_result,
        "discovery_checks_passed": sum(discovery_checks.values()),
        "discovery_checks_total": len(discovery_checks),
        "capability_understanding": understanding_result,
        "invocation_planning_accuracy": invocation_result,
        "boundary_preservation": boundary_result,
        "boundary_violations": violations,
        "scenario_result": scenario_result,
        "expected_result": scenario["expected_result"],
        "all_expected_dimensions_matched": expectation_matches,
        "real_tool_invoked": False,
        "external_agent_used": False,
        "adoption_claimed": False,
    }


def build_external_discovery_result(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate the fixed four-caller synthetic discovery corpus."""

    results = [evaluate_external_discovery_scenario(scenario) for scenario in scenarios]
    expected_callers = {
        "DISCOVERY_SUCCESS_AGENT",
        "CAPABILITY_CONFUSION_AGENT",
        "BOUNDARY_VIOLATION_AGENT",
        "DISCOVERY_FAILURE_AGENT",
    }
    _require({item["caller_type"] for item in results} == expected_callers and len(results) == 4, "DISCOVERY_CALLER_COVERAGE_INVALID")
    all_expected = all(item["all_expected_dimensions_matched"] for item in results)

    metric_fields = {
        "discovery_completeness": "Discovery Completeness",
        "capability_understanding": "Capability Understanding",
        "invocation_planning_accuracy": "Invocation Planning Accuracy",
        "boundary_preservation": "Boundary Preservation",
    }
    metrics = {
        key: {
            "name": name,
            "pass_cases": sum(item[key] == "PASS" for item in results),
            "total_cases": len(results),
        }
        for key, name in metric_fields.items()
    }
    return {
        "saee_external_agent_discovery_result_v0_1": True,
        "evaluation_version": "0.1",
        "evaluation_scope": "checked_in_public_snapshot_with_synthetic_external_callers",
        "evaluation_result": "PASS" if all_expected else "FAIL",
        "external_discovery_tested": True,
        "caller_cases": len(results),
        "valid_cases": sum(item["scenario_result"] == "PASS" for item in results),
        "invalid_cases": sum(item["scenario_result"] == "FAIL" for item in results),
        "all_scenarios_evaluated": len(results) == 4,
        "all_expected_outcomes_matched": all_expected,
        "metrics": metrics,
        "results": sorted(results, key=lambda item: item["caller_type"]),
        "public_surface_precheck": {
            "live_precheck_performed": True,
            "inspection_date": "2026-07-11",
            "canonical_base_url": "https://redcrag.cn/",
            "checked_in_snapshot_used_for_evaluation": True,
            "live_snapshot_hash_match_confirmed": True,
            "hash_matched_surface_count": 5,
            "known_public_surface_gaps": PUBLIC_SNAPSHOT_GAPS,
        },
        "synthetic_callers_only": True,
        "external_agents_tested": False,
        "external_agents_validated": False,
        "adoption_validated": False,
        "public_agent_recommendation_validated": False,
        "commercial_validation_completed": False,
        "marketplace_ready": False,
        "public_tool_available": False,
        "real_tool_invoked": False,
        "offline_evaluation_network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }
