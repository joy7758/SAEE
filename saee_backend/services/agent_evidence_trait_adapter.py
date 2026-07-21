"""Clean-room adapter for frozen Agent Evidence contract traits.

This module is SAEE-owned migration infrastructure, not a public capability.
It accepts only the bounded synthetic contract defined in
``agent-interface/schemas/saee-agent-evidence-trait-adapter-input.v0.1.json``.
It never imports or executes the historical source repository, never accesses
the network, and never turns upstream integrity status into evidence adequacy,
event authenticity, identity, authorization, or permission to act.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.agent_evidence_integrity import (
    IntegritySubsetError,
    build_event_chain,
    merkle_root,
    verify_ed25519_signature,
)


ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA_PATH = ROOT / "agent-interface/schemas/saee-agent-evidence-trait-adapter-input.v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "agent-interface/schemas/saee-agent-evidence-trait-adapter-result.v0.1.json"
SOURCE_COMMIT = "e5f3ab67dfc3f0d86c1d83c2fee8d3014a5c6219"
ADAPTER_ID = "saee.agent-evidence-trait-adapter.clean-room.v0.1"
MAX_PAYLOAD_CANONICAL_BYTES = 4096

INPUT_SCHEMA_INVALID = "AE_ADAPTER_INPUT_SCHEMA_INVALID"
SOURCE_COMPLETENESS_COUNT_MISMATCH = "AE_ADAPTER_SOURCE_COMPLETENESS_COUNT_MISMATCH"
NORMALIZED_EVENT_COUNT_MISMATCH = "AE_ADAPTER_NORMALIZED_EVENT_COUNT_MISMATCH"
EVENT_SEQUENCE_INVALID = "AE_ADAPTER_EVENT_SEQUENCE_INVALID"
EVENT_ID_DUPLICATE = "AE_ADAPTER_EVENT_ID_DUPLICATE"
PAYLOAD_NOT_JSON_SAFE = "AE_ADAPTER_PAYLOAD_NOT_JSON_SAFE"
PAYLOAD_TOO_LARGE = "AE_ADAPTER_PAYLOAD_TOO_LARGE"
ED25519_VERIFICATION_FAILED = "AE_ADAPTER_ED25519_VERIFICATION_FAILED"

TRUTH_BOUNDARY = {
    "source_text_copied": False,
    "local_crypto_subprocess_started": False,
    "external_code_executed": False,
    "network_accessed": False,
    "source_event_authenticity_verified": False,
    "actor_identity_verified": False,
    "authorization_verified": False,
    "evidence_adequacy_established": False,
    "action_authorized": False,
    "runtime_integrated": False,
    "production_ready": False,
}


def canonical_json(value: Any) -> str:
    """Return the bounded SAEE canonical JSON form; this is not a JCS claim."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_valid(document: Any, path: Path) -> bool:
    validator = Draft202012Validator(_schema(path), format_checker=FormatChecker())
    return not list(validator.iter_errors(document))


def _rejected(reason_codes: list[str]) -> dict[str, Any]:
    result = {
        "saee_agent_evidence_trait_adapter_result_v0_1": True,
        "schema_version": "0.1.0",
        "adapter_id": ADAPTER_ID,
        "source_commit": SOURCE_COMMIT,
        "adapter_status": "REJECTED",
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "candidate_evidence": [],
        "truth_boundary": dict(TRUTH_BOUNDARY),
    }
    Draft202012Validator(
        _schema(RESULT_SCHEMA_PATH), format_checker=FormatChecker()
    ).validate(result)
    return result


def _preflight(document: Any) -> list[str]:
    if not _schema_valid(document, INPUT_SCHEMA_PATH):
        return [INPUT_SCHEMA_INVALID]

    errors: list[str] = []
    counts = document["source_completeness"]
    if counts["source_event_count"] != (
        counts["normalized_event_count"] + counts["dropped_event_count"]
    ):
        errors.append(SOURCE_COMPLETENESS_COUNT_MISMATCH)
    if counts["normalized_event_count"] != len(document["events"]):
        errors.append(NORMALIZED_EVENT_COUNT_MISMATCH)

    indices = [event["event_index"] for event in document["events"]]
    if indices != list(range(len(indices))):
        errors.append(EVENT_SEQUENCE_INVALID)
    event_ids = [event["event_id"] for event in document["events"]]
    if len(event_ids) != len(set(event_ids)):
        errors.append(EVENT_ID_DUPLICATE)

    for event in document["events"]:
        try:
            payload_bytes = canonical_json(event["payload"]).encode("utf-8")
        except (TypeError, ValueError):
            errors.append(PAYLOAD_NOT_JSON_SAFE)
            continue
        if len(payload_bytes) > MAX_PAYLOAD_CANONICAL_BYTES:
            errors.append(PAYLOAD_TOO_LARGE)
    return list(dict.fromkeys(errors))


def adapt_agent_evidence_traits(document: Any) -> dict[str, Any]:
    """Adapt a bounded synthetic trait document into non-authoritative candidates."""

    source = copy.deepcopy(document)
    errors = _preflight(source)
    if errors:
        return _rejected(errors)

    candidates = []
    for event in source["events"]:
        candidates.append(
            {
                "event_index": event["event_index"],
                "event_id": event["event_id"],
                "observed_at": event["observed_at"],
                "event_type": event["event_type"],
                "actor_ref": f"{event['actor']['type']}:{event['actor']['id']}",
                "action_label": event["action"],
                "payload_digest": _sha256_json(event["payload"]),
                "payload_interpreted": False,
                "source_ref": copy.deepcopy(event["source_ref"]),
                "redaction": copy.deepcopy(event.get("redaction")),
            }
        )

    verification = source["verification"]
    try:
        event_chain = build_event_chain(candidates)
        local_merkle_root = merkle_root([item["event_digest"] for item in event_chain])
    except IntegritySubsetError:
        return _rejected([PAYLOAD_NOT_JSON_SAFE])

    signature = source.get("signature")
    if signature is None:
        ed25519 = {
            "check": "NOT_RUN",
            "reason": "signature_not_supplied",
            "local_crypto_subprocess_started": False,
            "openssl_path": None,
            "openssl_version": None,
        }
    else:
        ed25519 = verify_ed25519_signature(
            local_merkle_root.encode("ascii"),
            signature["public_key_pem"],
            signature["signature_base64"],
        )
    adapted_reason_codes = (
        [ED25519_VERIFICATION_FAILED] if ed25519["check"] == "FAIL" else []
    )
    output_truth = dict(TRUTH_BOUNDARY)
    output_truth["local_crypto_subprocess_started"] = ed25519[
        "local_crypto_subprocess_started"
    ]

    result = {
        "saee_agent_evidence_trait_adapter_result_v0_1": True,
        "schema_version": "0.1.0",
        "adapter_id": ADAPTER_ID,
        "source_commit": SOURCE_COMMIT,
        "adapter_status": "ADAPTED_WITH_SEMANTIC_LOSS",
        "reason_codes": adapted_reason_codes,
        "candidate_evidence": candidates,
        "source_completeness": copy.deepcopy(source["source_completeness"]),
        "integrity_context": {
            "upstream_verification_result": verification["result"],
            "upstream_checks": dict(sorted(verification["checks"].items())),
            "upstream_findings": copy.deepcopy(verification["findings"]),
            "warn_preserved": verification["result"] == "WARN",
            "cryptographic_verification_reperformed": False,
            "upstream_result_authorizes_action": False,
            "jcs_compatibility_scope": "ASCII_INTEGER_SAFE_SUBSET_ONLY",
            "local_canonicalization_check": "PASS",
            "local_event_chain_check": "PASS",
            "local_merkle_root_check": "PASS",
            "local_ed25519_signature_check": ed25519["check"],
            "local_ed25519_reason": ed25519["reason"],
            "local_ed25519_openssl_path": ed25519["openssl_path"],
            "local_ed25519_openssl_version": ed25519["openssl_version"],
            "event_chain": event_chain,
            "merkle_root": local_merkle_root,
            "full_bundle_integrity_established": False,
        },
        "evaluation_routing": {
            "eligible_for_evidence_adequacy": False,
            "reason": "trusted_conversion_contract_missing",
            "integrity_and_adequacy_separate": True,
        },
        "semantic_loss": [
            "payload_replaced_by_digest",
            "event_not_mapped_to_quality_or_risk_score",
            "identity_not_authenticated",
            "action_not_authorized",
        ],
        "canonicalization": {
            "method": "saee-canonical-json-v0.1",
            "jcs_compatible": False,
        },
        "truth_boundary": output_truth,
    }
    result["adapter_receipt_digest"] = _sha256_json(result)
    Draft202012Validator(
        _schema(RESULT_SCHEMA_PATH), format_checker=FormatChecker()
    ).validate(result)
    return result
