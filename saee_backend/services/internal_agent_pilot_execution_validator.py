"""Offline validator for SAEE Internal Agent Pilot Execution v1.0.

The validator recomputes evidence adequacy with the canonical evaluator. It
also invokes evaluate_agent_run only on its supported fixed internal rehearsal
projection; it never relabels a Codex observation as a fixed synthetic Agent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .agent_rehearsal_runtime import run_task
from .agent_run_capability import evaluate_agent_run
from .evidence_adequacy import evaluate_evidence_adequacy


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "agent-interface/pilot/saee-internal-agent-pilot-execution-manifest.v1.0.json"
RESULT_PATH = ROOT / "agent-interface/pilot/saee-internal-agent-pilot-execution-result.v1.0.json"
OBSERVATION_DIR = ROOT / "agent-interface/pilot/pilot-observations"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/saee-internal-agent-pilot-execution-manifest.schema.v1.0.json"
OBSERVATION_SCHEMA_PATH = ROOT / "schemas/saee-internal-agent-pilot-observation.schema.v1.0.json"
RESULT_SCHEMA_PATH = ROOT / "schemas/saee-internal-agent-pilot-execution-result.schema.v1.0.json"
PROJECTION_SCENARIO = ROOT / "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json"
REPORT_DIR = ROOT / "docs/pilot/results"
EXPECTED_REPORTS = {
    "SAEE_INTERNAL_PILOT_CODING_REPORT.md",
    "SAEE_INTERNAL_PILOT_RESEARCH_REPORT.md",
    "SAEE_INTERNAL_PILOT_AUTOMATION_REPORT.md",
}
EXPECTED_MAPPING = {
    "saee:internal-pilot-run:001": ("coding_agent", "CODE_CHANGE_WORKFLOW"),
    "saee:internal-pilot-run:002": ("research_agent", "RESEARCH_WORKFLOW"),
    "saee:internal-pilot-run:003": ("automation_agent", "AUTOMATION_WORKFLOW"),
}
FORBIDDEN_STORED_KEYS = {"chain_of_thought", "private_reasoning", "hidden_reasoning", "secret", "secrets", "credential", "credentials", "private_model_state"}
FORBIDDEN_TRUE_KEYS = {"external_validation", "customer_data", "production_execution", "external_world_actions", "adoption_validated", "production_ready", "external_validation_claim", "customer_claim", "production_claim"}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _forbidden_content(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_STORED_KEYS:
                return True
            if key in FORBIDDEN_TRUE_KEYS and child is True:
                return True
            if _forbidden_content(child):
                return True
    elif isinstance(value, list):
        return any(_forbidden_content(child) for child in value)
    return False


def _authorization_package(observation: dict[str, Any]) -> dict[str, Any]:
    binding = observation["authorization_evidence"]
    return {
        "saee_evidence_adequacy_input_v0_1": True,
        "schema_version": "0.1.0",
        "claim_type": "AUTHORIZED_AGENT_ACTION",
        "evidence": {
            "action": {
                "action_id": binding["action_id"], "agent_id": binding["agent_id"],
                "requested_scope": binding["requested_scope"], "timestamp": binding["timestamp"],
            },
            "policy_decision": {
                "decision_id": binding["decision_id"], "decision": binding["decision"],
                "agent_id": binding["agent_id"], "action_id": binding["action_id"],
                "authority_scope": binding["authority_scope"], "valid_from": binding["valid_from"],
                "valid_until": binding["valid_until"],
            },
        },
        "truth_boundary": {
            "event_occurrence_proven": False, "identity_independently_verified": False,
            "authorization_externally_verified": False, "legal_finding_established": False,
            "production_ready": False,
        },
    }


def validate_execution_artifacts(manifest: Any, result: Any, observations: list[Any], *, require_reports: bool = True) -> dict[str, Any]:
    reasons: list[str] = []
    pairs = ((manifest, MANIFEST_SCHEMA_PATH, "INTERNAL_PILOT_EXECUTION_MANIFEST_INVALID"), (result, RESULT_SCHEMA_PATH, "INTERNAL_PILOT_EXECUTION_RESULT_INVALID"))
    for value, schema_path, code in pairs:
        if not isinstance(value, dict) or list(Draft202012Validator(_load(schema_path), format_checker=FormatChecker()).iter_errors(value)):
            reasons.append(code)
    observation_validator = Draft202012Validator(_load(OBSERVATION_SCHEMA_PATH), format_checker=FormatChecker())
    if len(observations) != 3 or any(not isinstance(item, dict) or list(observation_validator.iter_errors(item)) for item in observations):
        reasons.append("INTERNAL_PILOT_OBSERVATION_INVALID")
    if _forbidden_content({"manifest": manifest, "result": result, "observations": observations}):
        reasons.append("INTERNAL_PILOT_EXECUTION_FORBIDDEN_CONTENT")

    run_ids = {item.get("run_id") for item in observations if isinstance(item, dict)}
    if run_ids != set(EXPECTED_MAPPING):
        reasons.append("INTERNAL_PILOT_RUN_SET_INVALID")
    else:
        for item in observations:
            if (item.get("agent_type"), item.get("scenario")) != EXPECTED_MAPPING[item["run_id"]]:
                reasons.append("INTERNAL_PILOT_RUN_BINDING_INVALID")
                break

    evidence_pass = 0
    for item in observations:
        if not isinstance(item, dict) or "authorization_evidence" not in item:
            continue
        evaluated = evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", _authorization_package(item))
        stored = item.get("evidence_findings", {})
        if evaluated["result"] != stored.get("result") or evaluated["missing_requirements"] != stored.get("missing_requirements") or stored.get("accountability_claim_established") is not False:
            reasons.append("INTERNAL_PILOT_EVIDENCE_EVALUATION_MISMATCH")
            break
        evidence_pass += evaluated["result"] == "PASS"

    projection = evaluate_agent_run(run_task(PROJECTION_SCENARIO))
    if projection.get("assessment") != "SUPPORTED" or projection.get("truth_boundary", {}).get("task_success_established") is not False:
        reasons.append("INTERNAL_PILOT_RELIABILITY_PROJECTION_INVALID")
    if any(item.get("reliability_findings", {}).get("evaluation_mode") != "FIXED_INTERNAL_PROJECTION_NOT_DIRECT_CODEX_ASSESSMENT" for item in observations if isinstance(item, dict)):
        reasons.append("INTERNAL_PILOT_DIRECT_EVALUATION_OVERCLAIM")

    if isinstance(result, dict):
        expected_refs = {str(path.relative_to(ROOT)) for path in OBSERVATION_DIR.glob("*.json")}
        if set(result.get("observations", [])) != expected_refs or result.get("runs_completed") != 3:
            reasons.append("INTERNAL_PILOT_RESULT_BINDING_INVALID")
        summary = result.get("evidence_summary", {})
        if summary.get("pass") != evidence_pass or summary.get("accountability_claims_established") != 0:
            reasons.append("INTERNAL_PILOT_RESULT_SUMMARY_INVALID")

    if require_reports and {path.name for path in REPORT_DIR.glob("*.md")} != EXPECTED_REPORTS:
        reasons.append("INTERNAL_PILOT_REPORT_SET_INVALID")

    return {
        "valid": not reasons,
        "reason_codes": list(dict.fromkeys(reasons)),
        "real_internal_execution": not reasons,
        "observation_exists": len(observations) == 3,
        "evaluation_completed": evidence_pass == 3 and "INTERNAL_PILOT_RELIABILITY_PROJECTION_INVALID" not in reasons,
        "evidence_boundary": "INTERNAL_PILOT_EXECUTION_FORBIDDEN_CONTENT" not in reasons,
        "runs_completed": 3 if not reasons else 0,
        "external_validation": False,
        "customer_data": False,
        "production_execution": False,
        "external_world_actions": False,
        "adoption_validated": False,
        "production_ready": False,
    }


def validate_execution_repository() -> dict[str, Any]:
    for schema_path in (MANIFEST_SCHEMA_PATH, OBSERVATION_SCHEMA_PATH, RESULT_SCHEMA_PATH):
        Draft202012Validator.check_schema(_load(schema_path))
    observations = [_load(path) for path in sorted(OBSERVATION_DIR.glob("*.json"))]
    return validate_execution_artifacts(_load(MANIFEST_PATH), _load(RESULT_PATH), observations)
