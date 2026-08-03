"""Offline SAEE Evidence Adequacy Profile v0.1 evaluator.

The evaluator checks whether a closed synthetic evidence package satisfies a
file-backed claim profile. A PASS means only that profile requirements were
met. It never asserts that an event occurred, an identity was verified, an
authorization was genuine, or a legal finding was established.
"""

from __future__ import annotations

import functools
import json
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.resource_resolution_receipt import (
    validate_resource_resolution_receipt,
)

_TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})"
)

ROOT = Path(__file__).resolve().parents[2]
PROFILE_SCHEMA_PATH = ROOT / "agent-interface/schemas/evidence-adequacy-profile.schema.json"
PROFILE_DIRECTORY = ROOT / "agent-interface/profiles/evidence-adequacy"
SCHEMA_VERSION = "0.1.0"

PROFILE_FILES = {
    "RESOURCE_AUTHENTICITY": "resource-authenticity.v0.1.json",
    "AUTHORIZED_AGENT_ACTION": "authorized-agent-action.v0.1.json",
    "HUMAN_OVERSIGHT": "human-oversight.v0.1.json",
    "EXECUTION_BOUNDARY": "execution-boundary.v0.1.json",
}

INPUT_SCHEMA_INVALID = "EVIDENCE_INPUT_SCHEMA_INVALID"
PROFILE_UNKNOWN = "EVIDENCE_PROFILE_UNKNOWN"
PROFILE_SCHEMA_INVALID = "EVIDENCE_PROFILE_SCHEMA_INVALID"

FIELD_REASON_CODES = {
    "/resource_receipt/requested_resource": "EVIDENCE_REQUESTED_RESOURCE_MISSING",
    "/resource_receipt/resolved_uri": "EVIDENCE_RESOLVED_URI_MISSING",
    "/resource_receipt/publisher_identity": "EVIDENCE_PUBLISHER_IDENTITY_MISSING",
    "/resource_receipt/content_digest": "EVIDENCE_DIGEST_MISSING",
    "/resource_receipt/policy_decision_ref": "EVIDENCE_POLICY_DECISION_MISSING",
    "/action/action_id": "EVIDENCE_ACTION_ID_MISSING",
    "/action/agent_id": "EVIDENCE_AGENT_ID_MISSING",
    "/action/requested_scope": "EVIDENCE_ACTION_SCOPE_MISSING",
    "/action/timestamp": "EVIDENCE_ACTION_TIMESTAMP_MISSING",
    "/approval/human_identity": "EVIDENCE_HUMAN_IDENTITY_MISSING",
    "/approval/approved_scope": "EVIDENCE_APPROVED_SCOPE_MISSING",
    "/approval/approval_timestamp": "EVIDENCE_APPROVAL_TIMESTAMP_MISSING",
    "/execution_effect/effect_id": "EVIDENCE_EXECUTION_EFFECT_REF_MISSING",
    "/resource_binding/receipt_id": "EVIDENCE_RESOURCE_RECEIPT_REF_MISSING",
}

CLAIM_EVIDENCE_KEYS = {
    "RESOURCE_AUTHENTICITY": {"resource_receipt"},
    "AUTHORIZED_AGENT_ACTION": {"action", "policy_decision"},
    "HUMAN_OVERSIGHT": {"action", "approval"},
    "EXECUTION_BOUNDARY": {"resource_binding", "execution_effect", "causal_link"},
}

NESTED_ALLOWED_KEYS = {
    "AUTHORIZED_AGENT_ACTION": {
        "action": {"action_id", "agent_id", "requested_scope", "timestamp"},
        "policy_decision": {
            "decision_id",
            "decision",
            "agent_id",
            "action_id",
            "authority_scope",
            "valid_from",
            "valid_until",
        },
    },
    "HUMAN_OVERSIGHT": {
        "action": {"action_id", "requested_scope", "timestamp"},
        "approval": {
            "human_identity",
            "approval_context",
            "approved_scope",
            "approval_timestamp",
            "action_id",
            "decision",
        },
    },
    "EXECUTION_BOUNDARY": {
        "resource_binding": {"receipt_id", "content_digest", "resolved_uri"},
        "execution_effect": {
            "effect_id",
            "resource_receipt_ref",
            "content_digest",
            "resolved_uri",
            "sandbox_ref",
        },
        "causal_link": {
            "relation_type",
            "source_receipt_ref",
            "target_effect_ref",
            "content_digest",
        },
    },
}

TRUTH_BOUNDARY = {
    "event_occurrence_proven": False,
    "identity_independently_verified": False,
    "authorization_externally_verified": False,
    "legal_finding_established": False,
    "production_ready": False,
}


class _DuplicateKeyError(ValueError):
    pass


def _closed_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError("duplicate JSON key")
        result[key] = value
    return result


def _result(
    claim_type: str,
    passed: bool,
    *,
    missing_requirements: list[str] | None = None,
    failed_relationships: list[str] | None = None,
    evaluated_fields: list[str] | None = None,
    reason_codes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "saee_evidence_adequacy_result_v0_1": True,
        "schema_version": SCHEMA_VERSION,
        "claim_type": claim_type,
        "result": "PASS" if passed else "FAIL",
        "profile_requirements_satisfied": passed,
        "accountability_claim_established": False,
        "missing_requirements": missing_requirements or [],
        "failed_relationships": failed_relationships or [],
        "evaluated_fields": evaluated_fields or [],
        "reason_codes": reason_codes or [],
        "message": "evidence profile requirements satisfied" if passed else "evidence profile requirements not satisfied",
        "network_accessed": False,
        "external_resource_read": False,
        "subprocess_started": False,
        "candidate_code_executed": False,
        "event_occurrence_proven": False,
        "identity_independently_verified": False,
        "authorization_externally_verified": False,
        "legal_finding_established": False,
        "production_ready": False,
    }


@functools.lru_cache
def _load_profile(claim_type: str) -> dict[str, Any] | None:
    filename = PROFILE_FILES.get(claim_type)
    if filename is None:
        return None
    return json.loads((PROFILE_DIRECTORY / filename).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _get_profile_validator() -> Draft202012Validator:
    schema = json.loads(PROFILE_SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _profile_valid(profile: dict[str, Any]) -> bool:
    validator = _get_profile_validator()
    return not list(validator.iter_errors(profile))


def _resolve(document: Any, pointer: str) -> tuple[bool, Any]:
    current = document
    for segment in pointer.split("/")[1:]:
        if not isinstance(current, dict) or segment not in current:
            return False, None
        current = current[segment]
    if current is None or current == "" or current == [] or current == {}:
        return False, None
    return True, current


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or _TIMESTAMP_PATTERN.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _missing_requirements(profile: dict[str, Any], evidence: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    missing: list[str] = []
    evaluated: list[str] = []
    reasons: list[str] = []

    collapsed_groups = [
        ("/policy_decision", "EVIDENCE_POLICY_DECISION_MISSING"),
        ("/approval/approval_context", "EVIDENCE_APPROVAL_CONTEXT_MISSING"),
        ("/causal_link", "EVIDENCE_CAUSAL_LINK_MISSING"),
    ]
    collapsed_prefixes: set[str] = set()
    for prefix, reason in collapsed_groups:
        exists, _ = _resolve(evidence, prefix)
        if not exists and any(path.startswith(prefix + "/") for path in profile["required_evidence_fields"]):
            missing.append(prefix)
            reasons.append(reason)
            collapsed_prefixes.add(prefix)

    for path in profile["required_evidence_fields"]:
        if any(path.startswith(prefix + "/") for prefix in collapsed_prefixes):
            continue
        exists, _ = _resolve(evidence, path)
        if exists:
            evaluated.append(path)
        else:
            missing.append(path)
            reason = FIELD_REASON_CODES.get(path, "EVIDENCE_REQUIRED_FIELD_MISSING")
            if reason not in reasons:
                reasons.append(reason)
    return missing, evaluated, reasons


def _check_resource_receipt_valid(source_ok: bool, source: Any, target_ok: bool, target: Any, evidence: dict[str, Any]) -> bool:
    return source_ok and validate_resource_resolution_receipt(source)["valid"] is True


def _check_reference_equals(source_ok: bool, source: Any, target_ok: bool, target: Any, evidence: dict[str, Any]) -> bool:
    return source_ok and target_ok and source == target


def _check_scope_covers(source_ok: bool, source: Any, target_ok: bool, target: Any, evidence: dict[str, Any]) -> bool:
    return source_ok and target_ok and isinstance(source, str) and source == target


def _check_timestamp_within_authority_window(source_ok: bool, source: Any, target_ok: bool, target: Any, evidence: dict[str, Any]) -> bool:
    if not source_ok or not target_ok or not isinstance(target, dict) or target.get("decision") != "allow":
        return False
    action_time = _parse_timestamp(source)
    valid_from = _parse_timestamp(target.get("valid_from"))
    valid_until = _parse_timestamp(target.get("valid_until"))
    return bool(action_time and valid_from and valid_until and valid_from <= action_time <= valid_until)


def _check_approval_precedes_action(source_ok: bool, source: Any, target_ok: bool, target: Any, evidence: dict[str, Any]) -> bool:
    approval_time = _parse_timestamp(source) if source_ok else None
    action_time = _parse_timestamp(target) if target_ok else None
    return bool(approval_time and action_time and approval_time <= action_time)


def _check_causal_binding_complete(source_ok: bool, source: Any, target_ok: bool, target: Any, evidence: dict[str, Any]) -> bool:
    link_ok, link = _resolve(evidence, "/causal_link")
    if not source_ok or not target_ok or not link_ok:
        return False
    if not isinstance(source, dict) or not isinstance(target, dict) or not isinstance(link, dict):
        return False
    digest = source.get("content_digest")
    resolved_uri = source.get("resolved_uri")
    return (
        link.get("relation_type") == "resource_to_execution_effect"
        and source.get("receipt_id") == target.get("resource_receipt_ref") == link.get("source_receipt_ref")
        and target.get("effect_id") == link.get("target_effect_ref")
        and source.get("content_digest") == target.get("content_digest") == link.get("content_digest")
        and source.get("resolved_uri") == target.get("resolved_uri")
        and isinstance(digest, str)
        and re.fullmatch(r"[0-9a-f]{64}", digest) is not None
        and isinstance(resolved_uri, str)
        and re.fullmatch(r"https://[a-z0-9.-]+/[A-Za-z0-9._~/-]+", resolved_uri) is not None
        and isinstance(target.get("sandbox_ref"), str)
        and bool(target.get("sandbox_ref"))
    )


_RELATIONSHIP_DISPATCHER: dict[str, Callable[[bool, Any, bool, Any, dict[str, Any]], bool]] = {
    "resource_receipt_valid": _check_resource_receipt_valid,
    "reference_equals": _check_reference_equals,
    "scope_covers": _check_scope_covers,
    "timestamp_within_authority_window": _check_timestamp_within_authority_window,
    "approval_precedes_action": _check_approval_precedes_action,
    "causal_binding_complete": _check_causal_binding_complete,
}


def _relationship_passes(relationship: dict[str, Any], evidence: dict[str, Any]) -> bool:
    relationship_type = relationship["relationship_type"]
    source_ok, source = _resolve(evidence, relationship.get("source_path", "/missing"))
    target_ok, target = _resolve(evidence, relationship.get("target_path", "/missing"))

    handler = _RELATIONSHIP_DISPATCHER.get(relationship_type)
    if handler:
        return handler(source_ok, source, target_ok, target, evidence)
    return False


def _input_valid(claim_type: str, package: Any) -> bool:
    if not isinstance(package, dict) or set(package) != {
        "saee_evidence_adequacy_input_v0_1",
        "schema_version",
        "claim_type",
        "evidence",
        "truth_boundary",
    }:
        return False
    if (
        package.get("saee_evidence_adequacy_input_v0_1") is not True
        or package.get("schema_version") != SCHEMA_VERSION
        or package.get("claim_type") != claim_type
        or package.get("truth_boundary") != TRUTH_BOUNDARY
        or not isinstance(package.get("evidence"), dict)
        or set(package["evidence"]) != CLAIM_EVIDENCE_KEYS.get(claim_type, set())
    ):
        return False
    evidence = package["evidence"]
    if claim_type == "RESOURCE_AUTHENTICITY":
        return isinstance(evidence.get("resource_receipt"), dict)
    for object_name, allowed_keys in NESTED_ALLOWED_KEYS.get(claim_type, {}).items():
        value = evidence.get(object_name)
        if not isinstance(value, dict) or not set(value).issubset(allowed_keys):
            return False
    if claim_type == "HUMAN_OVERSIGHT":
        context = evidence["approval"].get("approval_context")
        if context is not None and (
            not isinstance(context, dict)
            or not set(context).issubset({"risk_summary", "evidence_refs"})
        ):
            return False
    return True


def evaluate_evidence_adequacy(claim_type: str, package: Any) -> dict[str, Any]:
    """Evaluate a closed evidence package against one canonical v0.1 profile."""

    profile = _load_profile(claim_type)
    if profile is None:
        return _result(claim_type, False, reason_codes=[PROFILE_UNKNOWN])
    if not _profile_valid(profile):
        return _result(claim_type, False, reason_codes=[PROFILE_SCHEMA_INVALID])
    if not _input_valid(claim_type, package):
        return _result(claim_type, False, reason_codes=[INPUT_SCHEMA_INVALID])

    evidence = package["evidence"]
    missing, evaluated, reasons = _missing_requirements(profile, evidence)
    if missing:
        return _result(
            claim_type,
            False,
            missing_requirements=missing,
            evaluated_fields=evaluated,
            reason_codes=reasons,
        )

    if claim_type == "AUTHORIZED_AGENT_ACTION" and evidence["policy_decision"].get("decision") != "allow":
        reasons.append("EVIDENCE_POLICY_DECISION_NOT_ALLOW")
    if claim_type == "HUMAN_OVERSIGHT" and evidence["approval"].get("decision") != "approved":
        reasons.append("EVIDENCE_APPROVAL_DECISION_NOT_APPROVED")

    failed_relationships: list[str] = []
    for relationship in profile["required_relationships"]:
        if not _relationship_passes(relationship, evidence):
            failed_relationships.append(relationship["relationship_id"])
            if relationship["reason_code"] not in reasons:
                reasons.append(relationship["reason_code"])

    passed = not reasons
    return _result(
        claim_type,
        passed,
        failed_relationships=failed_relationships,
        evaluated_fields=evaluated,
        reason_codes=reasons,
    )


def evaluate_evidence_adequacy_json(claim_type: str, text: str) -> dict[str, Any]:
    """Parse closed JSON and evaluate without reflecting evidence values."""

    try:
        package = json.loads(text, object_pairs_hook=_closed_object)
    except (json.JSONDecodeError, UnicodeError, _DuplicateKeyError, ValueError):
        return _result(claim_type, False, reason_codes=[INPUT_SCHEMA_INVALID])
    return evaluate_evidence_adequacy(claim_type, package)
