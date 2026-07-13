"""Local synthetic SAEE Evidence Case Object vertical slice.

This module connects a bounded task contract, synthetic environment
observations, the existing Evidence Adequacy evaluator, a declared risk
estimate, and scenario-scoped decision support. It does not execute an Agent,
measure production risk, or authorize deployment.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples"


class EvidenceCaseError(ValueError):
    """Stable semantic or input-boundary failure for an evidence case."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise EvidenceCaseError(code, detail)


def _load_schema() -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def _validate_schema(document: Any) -> dict[str, Any]:
    _require(isinstance(document, dict), "EVIDENCE_CASE_INPUT_INVALID", "root must be an object")
    validator = Draft202012Validator(_load_schema(), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        location = "/" + "/".join(str(part) for part in first.absolute_path)
        raise EvidenceCaseError("EVIDENCE_CASE_SCHEMA_INVALID", f"{location}: {first.message}")
    return document


def _validate_semantics(document: dict[str, Any]) -> None:
    candidates = document["candidates"]
    candidate_refs = [item["candidate_ref"] for item in candidates]
    _require(
        len(candidate_refs) == len(set(candidate_refs)),
        "EVIDENCE_CASE_CANDIDATE_DUPLICATE",
        "candidate_ref values must be unique",
    )
    _require(
        document["task_contract"]["candidate_refs"] == candidate_refs,
        "EVIDENCE_CASE_CANDIDATE_SET_MISMATCH",
        "task candidate_refs must match candidates in declared order",
    )

    scenarios = document["environment_contract"]["scenarios"]
    scenario_refs = [item["scenario_id"] for item in scenarios]
    _require(
        len(scenario_refs) == len(set(scenario_refs)),
        "EVIDENCE_CASE_SCENARIO_DUPLICATE",
        "scenario_id values must be unique",
    )
    _require(
        abs(sum(float(item["weight"]) for item in scenarios) - 1.0) <= 1e-9,
        "EVIDENCE_CASE_SCENARIO_WEIGHTS_INVALID",
        "scenario weights must sum to 1",
    )

    policy = document["risk_policy"]
    _require(
        policy["deploy_limited_threshold"] < policy["retest_threshold"],
        "EVIDENCE_CASE_THRESHOLDS_INVALID",
        "deploy_limited_threshold must be lower than retest_threshold",
    )

    packages = document["evidence_packages"]
    package_refs = [item["candidate_ref"] for item in packages]
    _require(
        package_refs == candidate_refs,
        "EVIDENCE_CASE_EVIDENCE_SET_MISMATCH",
        "one ordered evidence package is required for each candidate",
    )
    evidence_ref_by_candidate = {
        item["candidate_ref"]: item["evidence_contract_ref"] for item in packages
    }
    _require(
        len(set(evidence_ref_by_candidate.values())) == len(candidate_refs),
        "EVIDENCE_CASE_EVIDENCE_REF_DUPLICATE",
        "evidence_contract_ref values must be unique",
    )

    expected_pairs = {(candidate_ref, scenario_ref) for candidate_ref in candidate_refs for scenario_ref in scenario_refs}
    observations = document["observations"]
    actual_pairs = [(item["candidate_ref"], item["scenario_ref"]) for item in observations]
    _require(
        len(actual_pairs) == len(set(actual_pairs)),
        "EVIDENCE_CASE_OBSERVATION_DUPLICATE",
        "candidate/scenario observation pairs must be unique",
    )
    _require(
        set(actual_pairs) == expected_pairs,
        "EVIDENCE_CASE_OBSERVATION_MATRIX_INCOMPLETE",
        "exactly one observation is required for every candidate/scenario pair",
    )
    for observation in observations:
        candidate_ref = observation["candidate_ref"]
        _require(
            observation["evidence_ref"] == evidence_ref_by_candidate[candidate_ref],
            "EVIDENCE_CASE_OBSERVATION_EVIDENCE_UNBOUND",
            observation["observation_ref"],
        )


def _decision_support(aggregate_risk: float, adequacy_passed: bool, policy: dict[str, Any]) -> str:
    if not adequacy_passed:
        return "RETEST"
    if aggregate_risk <= policy["deploy_limited_threshold"]:
        return "DEPLOY_LIMITED"
    if aggregate_risk <= policy["retest_threshold"]:
        return "RETEST"
    return "HOLD"


def evaluate_assurance_case(document: Any) -> dict[str, Any]:
    """Evaluate one strict, closed, local synthetic Evidence Case Object."""

    case = _validate_schema(document)
    _validate_semantics(case)

    scenario_by_ref = {
        item["scenario_id"]: item for item in case["environment_contract"]["scenarios"]
    }
    observations_by_candidate: dict[str, list[dict[str, Any]]] = {
        item["candidate_ref"]: [] for item in case["candidates"]
    }
    for observation in case["observations"]:
        observations_by_candidate[observation["candidate_ref"]].append(observation)

    package_by_candidate = {
        item["candidate_ref"]: item for item in case["evidence_packages"]
    }
    policy = case["risk_policy"]
    candidate_results: list[dict[str, Any]] = []
    for candidate in case["candidates"]:
        candidate_ref = candidate["candidate_ref"]
        package = package_by_candidate[candidate_ref]
        claim = package["claim_evidence"]
        adequacy = evaluate_evidence_adequacy(claim["claim_type"], claim)

        evaluation_results: list[dict[str, Any]] = []
        scenario_risks: list[dict[str, Any]] = []
        aggregate_risk = 0.0
        for observation in observations_by_candidate[candidate_ref]:
            scenario = scenario_by_ref[observation["scenario_ref"]]
            score = round(1.0 - float(observation["failure_estimate"]), 6)
            scenario_risk = round(
                float(observation["failure_estimate"])
                * float(scenario["business_impact"])
                * float(scenario["exposure"])
                * (1.0 - float(scenario["control_effectiveness"]))
                + float(scenario["uncertainty_penalty"]),
                6,
            )
            weighted_risk = round(float(scenario["weight"]) * scenario_risk, 6)
            aggregate_risk += weighted_risk
            evaluation_results.append(
                {
                    "observation_ref": observation["observation_ref"],
                    "scenario_ref": observation["scenario_ref"],
                    "score": score,
                    "score_interpretation": "one_minus_declared_synthetic_failure_estimate",
                    "reason": observation["reason"],
                    "failure_class": observation["failure_class"],
                    "evidence_ref": observation["evidence_ref"],
                    "observation_is_evidence": False,
                }
            )
            scenario_risks.append(
                {
                    "scenario_ref": observation["scenario_ref"],
                    "failure_estimate": observation["failure_estimate"],
                    "business_impact": scenario["business_impact"],
                    "exposure": scenario["exposure"],
                    "control_effectiveness": scenario["control_effectiveness"],
                    "uncertainty_penalty": scenario["uncertainty_penalty"],
                    "scenario_weight": scenario["weight"],
                    "scenario_risk_estimate": scenario_risk,
                    "weighted_risk_estimate": weighted_risk,
                    "risk_estimate_not_measurement": True,
                }
            )

        aggregate_risk = round(aggregate_risk, 6)
        adequacy_passed = adequacy["result"] == "PASS"
        recommendation = _decision_support(aggregate_risk, adequacy_passed, policy)
        candidate_results.append(
            {
                "candidate_ref": candidate_ref,
                "candidate_label": candidate["label"],
                "version_ref": candidate["version_ref"],
                "evaluation_results": evaluation_results,
                "evidence_adequacy": adequacy,
                "risk_estimate": {
                    "formula_version": policy["formula_version"],
                    "scenario_estimates": scenario_risks,
                    "aggregate_estimated_deployment_risk": aggregate_risk,
                    "risk_probability_measured": False,
                    "risk_estimate_not_measurement": True,
                },
                "decision_support": {
                    "recommendation": recommendation,
                    "scenario_scope": policy["threshold_scope"],
                    "reason": (
                        "Evidence adequacy failed; additional evidence is required."
                        if not adequacy_passed
                        else "Recommendation derived from declared synthetic thresholds and estimated risk."
                    ),
                    "allowed_use": ["Local synthetic comparison and architecture review."],
                    "prohibited_use": [
                        "Production deployment authorization.",
                        "Customer safety certification.",
                        "Measured failure-probability claim.",
                    ],
                    "evidence_ref": package["evidence_contract_ref"],
                    "customer_execution_authorized": False,
                    "automatic_decision": False,
                },
            }
        )

    ranked = sorted(
        candidate_results,
        key=lambda item: (item["risk_estimate"]["aggregate_estimated_deployment_risk"], item["candidate_ref"]),
    )
    lowest = ranked[0]
    evidence_case_object = {
        "identity": {
            "case_id": case["case_id"],
            "case_type": case["identity"]["case_type"],
            "owner_scope": case["identity"]["owner_scope"],
            "synthetic": True,
        },
        "task_contract": case["task_contract"],
        "environment": case["environment_contract"],
        "agent_reference": case["candidates"],
        "observation": case["observations"],
        "evaluation": [
            {
                "candidate_ref": item["candidate_ref"],
                "results": item["evaluation_results"],
            }
            for item in candidate_results
        ],
        "evidence": [
            {
                "candidate_ref": item["candidate_ref"],
                "evidence_ref": item["decision_support"]["evidence_ref"],
                "adequacy_result": item["evidence_adequacy"],
            }
            for item in candidate_results
        ],
        "risk": [
            {
                "candidate_ref": item["candidate_ref"],
                **item["risk_estimate"],
            }
            for item in candidate_results
        ],
        "decision": [
            {
                "candidate_ref": item["candidate_ref"],
                **item["decision_support"],
            }
            for item in candidate_results
        ],
    }
    return {
        "saee_phase1_synthetic_vertical_slice_result_v0_1": True,
        "result_type": "SAEE_PHASE1_SYNTHETIC_VERTICAL_SLICE_RESULT",
        "case_object_type": "SAEE_EVIDENCE_CASE_OBJECT",
        "schema_version": "0.1.0",
        "architecture_version": case["architecture_version"],
        "case_id": case["case_id"],
        "case_status": "LOCAL_SYNTHETIC_RESULT_ONLY",
        "candidate_count": len(case["candidates"]),
        "scenario_count": len(case["environment_contract"]["scenarios"]),
        "evaluation_record_count": len(case["observations"]),
        "evidence_case_object": evidence_case_object,
        "candidate_results": candidate_results,
        "lowest_estimated_risk_candidate_ref": lowest["candidate_ref"],
        "scenario_scoped_recommendation": lowest["decision_support"]["recommendation"],
        "limitations": [
            "All task, environment, observation, evidence, and risk inputs are synthetic declarations.",
            "Evidence Adequacy checks profile completeness and relationships; it does not prove event occurrence.",
            "The risk value is an estimate under this case policy, not an empirically measured probability.",
            "Decision Support does not authorize deployment or replace human and organizational approval.",
        ],
        "truth_boundary": {
            "existing_evidence_adequacy_reused": True,
            "real_agent_executed": False,
            "external_tool_executed": False,
            "production_trace_observed": False,
            "customer_data_used": False,
            "risk_probability_measured": False,
            "automatic_decision_made": False,
            "deployment_authorized": False,
            "external_validation_completed": False,
            "customer_validated": False,
            "production_ready": False,
            "network_calls": 0,
            "subprocess_started": False,
        },
    }


def run_assurance_case_path(path: Path) -> dict[str, Any]:
    """Run a canonical local fixture without expanding the input boundary."""

    resolved = path.resolve()
    try:
        relative = resolved.relative_to(EXAMPLE_DIRECTORY.resolve())
        inside_examples = bool(relative.parts)
    except ValueError:
        inside_examples = False
    _require(
        inside_examples and resolved.suffix == ".json",
        "EVIDENCE_CASE_PATH_OUTSIDE_CANONICAL_EXAMPLES",
        "input must be a JSON file inside agent-interface/architecture/examples",
    )
    try:
        document = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        raise EvidenceCaseError("EVIDENCE_CASE_INPUT_INVALID", str(exc)) from exc
    return evaluate_assurance_case(document)
