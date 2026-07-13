"""Local, offline adapter around the canonical SAEE evidence adequacy evaluator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.evidence_adequacy import (
    INPUT_SCHEMA_INVALID,
    evaluate_evidence_adequacy,
)
from saee_backend.services.local_tool_guard import LocalToolInputError, validate_local_tool_request


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_SCHEMA_PATH = ROOT / "agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json"

BOUNDARY_STATEMENT = (
    "SAEE tool capability evaluates evidence adequacy. It does not authorize actions, "
    "approve deployment, certify safety or compliance, or establish a legal conclusion."
)
LIMITATIONS = [
    "The result evaluates one repository-fixed profile and does not prove that a real-world event occurred.",
    "Declared evidence authenticity, identity, and authorization are not independently verified by this tool.",
    "Observation references are inert provenance references and are not used as evidence.",
    "The result is decision support and cannot approve, reject, authorize, deploy, certify, or establish a legal conclusion.",
    "This is a local offline research prototype with no MCP, API, persistence, network, or production runtime.",
]
TRUTH_BOUNDARY = {
    "local_tool_prototype": True,
    "network_accessed": False,
    "subprocess_started": False,
    "external_execution": False,
    "persistence_performed": False,
    "mcp_available": False,
    "api_available": False,
    "authorization_performed": False,
    "deployment_authorized": False,
    "safety_certified": False,
    "legal_determination_made": False,
    "production_ready": False,
}


def _result(
    *,
    tool_result: str,
    claim_assessment: str,
    evidence_sufficiency_status: str,
    reason_codes: list[str],
    observation_reference_count: int = 0,
    missing_requirements: list[str] | None = None,
    failed_relationships: list[str] | None = None,
    evaluated_fields: list[str] | None = None,
) -> dict[str, Any]:
    result = {
        "saee_local_evidence_tool_result_v0_1": True,
        "tool_contract_version": "0.1",
        "tool_result": tool_result,
        "claim_assessment": claim_assessment,
        "evidence_sufficiency_status": evidence_sufficiency_status,
        "missing_requirements": sorted(set(missing_requirements or [])),
        "failed_relationships": sorted(set(failed_relationships or [])),
        "evaluated_fields": sorted(set(evaluated_fields or [])),
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "limitations": list(LIMITATIONS),
        "boundary_statement": BOUNDARY_STATEMENT,
        "observation_reference_count": observation_reference_count,
        "observation_not_used_as_evidence": True,
        "truth_boundary": dict(TRUTH_BOUNDARY),
    }
    schema = json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(result), key=lambda error: list(error.absolute_path))
    if errors:
        raise RuntimeError("SAEE local tool produced an invalid bounded output")
    return result


def _rejected(code: str) -> dict[str, Any]:
    return _result(
        tool_result="REJECTED_INPUT",
        claim_assessment="UNKNOWN",
        evidence_sufficiency_status="UNKNOWN",
        reason_codes=[code],
    )


def evaluate_evidence_tool(request: bytes | str | dict[str, Any]) -> dict[str, Any]:
    """Evaluate one guarded local request using the existing canonical evaluator."""

    try:
        validated = validate_local_tool_request(request)
    except LocalToolInputError as exc:
        return _rejected(exc.code)

    observation_count = len(validated.get("observation_references", []))
    evaluation = evaluate_evidence_adequacy(
        validated["accountability_claim"],
        validated["evidence_object"],
    )
    if INPUT_SCHEMA_INVALID in evaluation.get("reason_codes", []):
        return _result(
            tool_result="REJECTED_INPUT",
            claim_assessment="UNKNOWN",
            evidence_sufficiency_status="UNKNOWN",
            reason_codes=[INPUT_SCHEMA_INVALID],
            observation_reference_count=observation_count,
        )

    passed = evaluation.get("result") == "PASS"
    return _result(
        tool_result="SUCCESS",
        claim_assessment="SUPPORTED" if passed else "INSUFFICIENT_EVIDENCE",
        evidence_sufficiency_status="SUFFICIENT" if passed else "INSUFFICIENT",
        missing_requirements=evaluation.get("missing_requirements", []),
        failed_relationships=evaluation.get("failed_relationships", []),
        evaluated_fields=evaluation.get("evaluated_fields", []),
        reason_codes=evaluation.get("reason_codes", []),
        observation_reference_count=observation_count,
    )
