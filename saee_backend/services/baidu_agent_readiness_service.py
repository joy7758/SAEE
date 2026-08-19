"""Deterministic public product projection for Baidu Agent readiness review.

This module evaluates declared trace metadata and file-shaped evidence coverage.
It does not execute an Agent, verify trace authenticity, contact Baidu, or make
a deployment decision. Scores are coverage percentages, never reliability or
safety probabilities.
"""

from __future__ import annotations

import functools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
QIANFAN = ROOT / "agent-interface/qianfan"
EVIDENCE_ITEM_SCHEMA = QIANFAN / "saee-readiness-evidence-item.schema.v0.1.json"
RUN_REQUEST_SCHEMA = QIANFAN / "saee-evaluate-agent-run-request.schema.v0.1.json"
RUN_RESPONSE_SCHEMA = QIANFAN / "saee-evaluate-agent-run-response.schema.v0.1.json"
EVIDENCE_REQUEST_SCHEMA = QIANFAN / "saee-evaluate-evidence-request.schema.v0.1.json"
EVIDENCE_RESPONSE_SCHEMA = QIANFAN / "saee-evaluate-evidence-response.schema.v0.1.json"

BASE_REQUIRED = ("TEST_RESULT",)
HIGH_IMPACT_REQUIRED = ("TEST_RESULT", "ROLLBACK_PLAN", "PERMISSION_BOUNDARY", "HUMAN_APPROVAL")
RISK_BY_MISSING = {
    "TEST_RESULT": "insufficient_test_evidence",
    "ROLLBACK_PLAN": "missing_recovery_plan",
    "PERMISSION_BOUNDARY": "unbounded_external_api_permission",
    "HUMAN_APPROVAL": "missing_human_approval_checkpoint",
}
LIMITATIONS = [
    "The score is required-evidence coverage, not a probability of reliability or safety.",
    "SAEE does not authenticate the supplied trace or evidence references.",
    "The result is not security certification, compliance determination, or legal advice.",
    "The result does not authorize deployment, permission expansion, payment, or another external action.",
    "This local Alpha accepts no customer data and performs no external-world execution.",
]
TRUTH_BOUNDARY = {
    "local_alpha": True,
    "agent_executed_by_saee": False,
    "trace_authenticity_verified": False,
    "customer_data_used": False,
    "deployment_authorized": False,
    "security_certified": False,
    "customer_validated": False,
    "production_ready": False,
}


class ReadinessInputError(ValueError):
    """A typed fail-closed error for invalid public-product input."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass
class RunEvaluationContext:
    """Context object holding evaluation results for an agent run."""

    request_id: str
    readiness: str
    score: int
    required: tuple[str, ...] | list[str]
    available: list[str]
    missing: list[str]
    risks: list[str]
    recommendation: str


@functools.lru_cache(maxsize=None)
def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"schema must be an object: {path.name}")
    return value


@functools.lru_cache(maxsize=None)
def _registry() -> Registry:
    item = _load(EVIDENCE_ITEM_SCHEMA)
    return Registry().with_resource(item["$id"], Resource.from_contents(item))


@functools.lru_cache(maxsize=None)
def _validator(path: Path) -> Draft202012Validator:
    return Draft202012Validator(_load(path), registry=_registry())


def _validate(path: Path, value: Any, code: str) -> None:
    errors = sorted(
        _validator(path).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        first = errors[0]
        pointer = "/" + "/".join(str(part) for part in first.absolute_path)
        raise ReadinessInputError(code, f"{pointer}: {first.message}")


def _evidence_state(items: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    seen: set[str] = set()
    present: set[str] = set()
    ids: set[str] = set()
    for item in items:
        evidence_id = item["evidence_id"]
        evidence_type = item["evidence_type"]
        if evidence_id in ids:
            raise ReadinessInputError("READINESS_EVIDENCE_ID_DUPLICATE", evidence_id)
        if evidence_type in seen:
            raise ReadinessInputError("READINESS_EVIDENCE_TYPE_DUPLICATE", evidence_type)
        ids.add(evidence_id)
        seen.add(evidence_type)
        if item["present"]:
            present.add(evidence_type)
    return seen, present


def _coverage(required: tuple[str, ...] | list[str], present: set[str]) -> tuple[int, list[str], list[str]]:
    ordered = list(dict.fromkeys(required))
    available = [item for item in ordered if item in present]
    missing = [item for item in ordered if item not in present]
    score = round(100 * len(available) / len(ordered))
    return score, available, missing


def evaluate_evidence(request: dict[str, Any]) -> dict[str, Any]:
    """Evaluate declared evidence coverage against an explicit required set."""

    _validate(EVIDENCE_REQUEST_SCHEMA, request, "READINESS_EVIDENCE_REQUEST_INVALID")
    _, present = _evidence_state(request["evidence_bundle"]["items"])
    required = request["required_evidence_types"]
    score, available, missing = _coverage(required, present)
    quality = "SUFFICIENT" if score == 100 else ("PARTIAL" if score >= 50 else "INSUFFICIENT")
    response = {
        "response_version": "0.1.0",
        "request_id": request["request_id"],
        "capability_id": "saee.agent-readiness",
        "operation": "saee.evaluate_evidence",
        "evidence_quality": quality,
        "coverage_score": score,
        "score_semantics": "required_evidence_coverage_percent_not_reliability_probability",
        "required_evidence": list(required),
        "present_evidence": available,
        "missing_evidence": missing,
        "reason_codes": [f"READINESS_{item}_MISSING" for item in missing],
        "limitations": list(LIMITATIONS),
        "truth_boundary": dict(TRUTH_BOUNDARY),
    }
    _validate(EVIDENCE_RESPONSE_SCHEMA, response, "READINESS_EVIDENCE_RESPONSE_INVALID")
    return response


def _determine_run_required_evidence(events: list[dict[str, Any]]) -> tuple[str, ...] | list[str]:
    high_impact = any(item["high_impact"] or item["external_effect"] for item in events)
    return HIGH_IMPACT_REQUIRED if high_impact else BASE_REQUIRED


def _determine_run_readiness(score: int) -> tuple[str, str]:
    if score == 100:
        return "continue", "CONTINUE"
    if score >= 75:
        return "conditional", "HUMAN_REVIEW_REQUIRED"
    if score >= 50:
        return "replan", "REPLAN"
    return "stop", "STOP"


def _build_run_response(context: RunEvaluationContext) -> dict[str, Any]:
    return {
        "response_version": "0.1.0",
        "request_id": context.request_id,
        "capability_id": "saee.agent-readiness",
        "operation": "saee.evaluate_agent_run",
        "readiness": context.readiness,
        "score": context.score,
        "score_semantics": "required_evidence_coverage_percent_not_reliability_probability",
        "required_evidence": list(context.required),
        "present_evidence": context.available,
        "missing_evidence": context.missing,
        "risks": context.risks,
        "recommendation": context.recommendation,
        "limitations": list(LIMITATIONS),
        "truth_boundary": dict(TRUTH_BOUNDARY),
    }


def evaluate_agent_run(request: dict[str, Any]) -> dict[str, Any]:
    """Assess one declared Agent run without executing it or authorizing action."""

    _validate(RUN_REQUEST_SCHEMA, request, "READINESS_AGENT_RUN_REQUEST_INVALID")
    required = _determine_run_required_evidence(request["trace"]["events"])
    _, present = _evidence_state(request["evidence"])
    score, available, missing = _coverage(required, present)
    risks = [RISK_BY_MISSING[item] for item in missing]
    readiness, recommendation = _determine_run_readiness(score)
    context = RunEvaluationContext(
        request_id=request["request_id"],
        readiness=readiness,
        score=score,
        required=required,
        available=available,
        missing=missing,
        risks=risks,
        recommendation=recommendation,
    )
    response = _build_run_response(context)
    _validate(RUN_RESPONSE_SCHEMA, response, "READINESS_AGENT_RUN_RESPONSE_INVALID")
    return response
