"""Route adapted Agent Evidence candidates into existing SAEE Evaluation.

Integrity and evidence adequacy are evaluated as separate contexts. A local
adequacy PASS never authorizes action and cannot overcome declared-only source
binding or unverified event authenticity. The strongest possible decision in
v0.1 is therefore ``HUMAN_REVIEW``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy


ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA = ROOT / "agent-interface/schemas/saee-agent-evidence-evaluation-bridge-input.v0.1.json"
RESULT_SCHEMA = ROOT / "agent-interface/schemas/saee-agent-evidence-evaluation-bridge-result.v0.1.json"
ADAPTER_RESULT_SCHEMA = ROOT / "agent-interface/schemas/saee-agent-evidence-trait-adapter-result.v0.1.json"
BRIDGE_ID = "saee.agent-evidence-evaluation-bridge.v0.1"

INPUT_SCHEMA_INVALID = "AE_BRIDGE_INPUT_SCHEMA_INVALID"
ADAPTER_RESULT_INVALID = "AE_BRIDGE_ADAPTER_RESULT_INVALID"
ADAPTER_REJECTED = "AE_BRIDGE_ADAPTER_REJECTED"
BINDING_DIGEST_MISMATCH = "AE_BRIDGE_BINDING_DIGEST_MISMATCH"
BINDING_EVENT_UNKNOWN = "AE_BRIDGE_BINDING_EVENT_UNKNOWN"
UPSTREAM_NOT_PASS = "AE_BRIDGE_UPSTREAM_NOT_PASS"
LOCAL_INTEGRITY_INCOMPLETE = "AE_BRIDGE_LOCAL_INTEGRITY_INCOMPLETE"
ED25519_NOT_VERIFIED = "AE_BRIDGE_ED25519_NOT_VERIFIED"
ADEQUACY_NOT_SATISFIED = "AE_BRIDGE_ADEQUACY_NOT_SATISFIED"
DECLARED_BINDING_REQUIRES_REVIEW = "AE_BRIDGE_DECLARED_BINDING_REQUIRES_REVIEW"
SOURCE_AUTHENTICITY_UNVERIFIED = "AE_BRIDGE_SOURCE_AUTHENTICITY_UNVERIFIED"

TRUTH_BOUNDARY = {
    "source_event_authenticity_verified": False,
    "binding_independently_verified": False,
    "identity_verified": False,
    "authorization_verified": False,
    "adequacy_authorizes_action": False,
    "action_authorized": False,
    "external_action_performed": False,
    "runtime_integrated": False,
    "production_ready": False,
}


def _read_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _valid(document: Any, schema_path: Path) -> bool:
    validator = Draft202012Validator(
        _read_schema(schema_path), format_checker=FormatChecker()
    )
    return not list(validator.iter_errors(document))


def _digest(document: dict[str, Any]) -> str:
    payload = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _summary(adapter_result: Any) -> dict[str, Any]:
    if not isinstance(adapter_result, dict):
        return {
            "upstream_result": None,
            "event_chain_check": None,
            "merkle_root_check": None,
            "ed25519_signature_check": None,
            "full_bundle_integrity_established": False,
        }
    context = adapter_result.get("integrity_context")
    if not isinstance(context, dict):
        return {
            "upstream_result": None,
            "event_chain_check": None,
            "merkle_root_check": None,
            "ed25519_signature_check": None,
            "full_bundle_integrity_established": False,
        }
    return {
        "upstream_result": context.get("upstream_verification_result"),
        "event_chain_check": context.get("local_event_chain_check"),
        "merkle_root_check": context.get("local_merkle_root_check"),
        "ed25519_signature_check": context.get("local_ed25519_signature_check"),
        "full_bundle_integrity_established": False,
    }


def _result(
    *,
    status: str,
    decision: str,
    reason_codes: list[str],
    adapter_digest: str | None,
    claim_type: str | None,
    integrity_summary: dict[str, Any],
    adequacy_result: dict[str, Any] | None,
    evaluator_called: bool,
) -> dict[str, Any]:
    result = {
        "saee_agent_evidence_evaluation_bridge_result_v0_1": True,
        "schema_version": "0.1.0",
        "bridge_id": BRIDGE_ID,
        "bridge_status": status,
        "decision": decision,
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "adapter_receipt_digest": adapter_digest,
        "claim_type": claim_type,
        "integrity_summary": integrity_summary,
        "adequacy_result": adequacy_result,
        "saee_evaluator_called": evaluator_called,
        "binding_assessment": "DECLARED_ONLY_NOT_INDEPENDENTLY_VERIFIED",
        "truth_boundary": dict(TRUTH_BOUNDARY),
    }
    result["bridge_receipt_digest"] = _digest(result)
    Draft202012Validator(
        _read_schema(RESULT_SCHEMA), format_checker=FormatChecker()
    ).validate(result)
    return result


def route_agent_evidence_to_evaluation(document: Any) -> dict[str, Any]:
    """Route a closed adapter result and separate adequacy package."""

    if not _valid(document, INPUT_SCHEMA):
        return _result(
            status="REJECTED",
            decision="REPLAN",
            reason_codes=[INPUT_SCHEMA_INVALID],
            adapter_digest=None,
            claim_type=None,
            integrity_summary=_summary(None),
            adequacy_result=None,
            evaluator_called=False,
        )

    adapter = document["adapter_result"]
    adapter_digest = adapter.get("adapter_receipt_digest") if isinstance(adapter, dict) else None
    claim_type = document["claim_type"]
    if not _valid(adapter, ADAPTER_RESULT_SCHEMA):
        return _result(
            status="REJECTED",
            decision="REPLAN",
            reason_codes=[ADAPTER_RESULT_INVALID],
            adapter_digest=adapter_digest if isinstance(adapter_digest, str) else None,
            claim_type=claim_type,
            integrity_summary=_summary(adapter),
            adequacy_result=None,
            evaluator_called=False,
        )
    if adapter["adapter_status"] != "ADAPTED_WITH_SEMANTIC_LOSS":
        return _result(
            status="REJECTED",
            decision="REPLAN",
            reason_codes=[ADAPTER_REJECTED],
            adapter_digest=adapter_digest,
            claim_type=claim_type,
            integrity_summary=_summary(adapter),
            adequacy_result=None,
            evaluator_called=False,
        )

    binding = document["binding"]
    known_event_ids = {item["event_id"] for item in adapter["candidate_evidence"]}
    binding_errors: list[str] = []
    if binding["adapter_receipt_digest"] != adapter_digest:
        binding_errors.append(BINDING_DIGEST_MISMATCH)
    if not set(binding["event_ids"]).issubset(known_event_ids):
        binding_errors.append(BINDING_EVENT_UNKNOWN)
    if binding_errors:
        return _result(
            status="REJECTED",
            decision="REPLAN",
            reason_codes=binding_errors,
            adapter_digest=adapter_digest,
            claim_type=claim_type,
            integrity_summary=_summary(adapter),
            adequacy_result=None,
            evaluator_called=False,
        )

    adequacy = evaluate_evidence_adequacy(claim_type, document["adequacy_package"])
    context = adapter["integrity_context"]
    reasons: list[str] = []
    if context["upstream_verification_result"] != "PASS":
        reasons.append(UPSTREAM_NOT_PASS)
    if (
        context["local_event_chain_check"] != "PASS"
        or context["local_merkle_root_check"] != "PASS"
    ):
        reasons.append(LOCAL_INTEGRITY_INCOMPLETE)
    if context["local_ed25519_signature_check"] != "PASS":
        reasons.append(ED25519_NOT_VERIFIED)
    if adequacy["result"] != "PASS":
        reasons.append(ADEQUACY_NOT_SATISFIED)

    if reasons:
        decision = "REPLAN"
    else:
        decision = "HUMAN_REVIEW"
        reasons.extend(
            [DECLARED_BINDING_REQUIRES_REVIEW, SOURCE_AUTHENTICITY_UNVERIFIED]
        )
    return _result(
        status="ROUTED",
        decision=decision,
        reason_codes=reasons,
        adapter_digest=adapter_digest,
        claim_type=claim_type,
        integrity_summary=_summary(adapter),
        adequacy_result=adequacy,
        evaluator_called=True,
    )
