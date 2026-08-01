"""Offline validation for SAEE external resource-resolution receipts.

The validator never dereferences the declared URI, reads a referenced local
resource, installs a package, starts a subprocess, or executes candidate code.
It validates a closed receipt and recomputes digests only from bounded
synthetic inline bytes carried by the receipt itself.
"""

from __future__ import annotations

import base64
import functools
import hashlib
import hmac
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "agent-interface/schemas/resource-resolution-receipt.schema.json"
SCHEMA_VERSION = "0.1.0"
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
DNS_LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
PATH_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9._~-]+$")
RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$"
)

RESOURCE_PUBLISHER_IDENTITY_REQUIRED = "RESOURCE_PUBLISHER_IDENTITY_REQUIRED"
RESOURCE_DIGEST_INVALID = "RESOURCE_DIGEST_INVALID"
RESOURCE_POLICY_DECISION_REQUIRED = "RESOURCE_POLICY_DECISION_REQUIRED"
RESOURCE_EXECUTION_EFFECT_UNBOUND = "RESOURCE_EXECUTION_EFFECT_UNBOUND"
RESOURCE_RESOLVED_URI_INVALID = "RESOURCE_RESOLVED_URI_INVALID"
RESOURCE_RECEIPT_DIGEST_MISMATCH = "RESOURCE_RECEIPT_DIGEST_MISMATCH"
RESOURCE_SCHEMA_INVALID = "RESOURCE_SCHEMA_INVALID"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_receipt_digest(receipt: dict[str, Any]) -> str:
    covered = {key: value for key, value in receipt.items() if key != "integrity"}
    return hashlib.sha256(canonical_json(covered).encode("utf-8")).hexdigest()


def _result(valid: bool, reason_codes: list[str], receipt_digest: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "saee_resource_resolution_validation_v0_1": True,
        "schema_version": SCHEMA_VERSION,
        "valid": valid,
        "reason_codes": reason_codes,
        "message": "resource resolution receipt accepted" if valid else "resource resolution receipt rejected",
        "network_accessed": False,
        "uri_dereferenced": False,
        "external_resource_read": False,
        "subprocess_started": False,
        "candidate_code_executed": False,
        "publisher_identity_verified": False,
        "external_resource_authenticity_verified": False,
        "production_ready": False,
    }
    if receipt_digest is not None:
        payload["receipt_digest"] = receipt_digest
    return payload


def _canonical_https_uri(value: Any) -> tuple[bool, str | None]:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 1024
        or not value.isascii()
        or any(character.isspace() or ord(character) < 0x20 or ord(character) == 0x7F for character in value)
        or "\\" in value
        or "%" in value
    ):
        return False, None
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False, None
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.query
        or parsed.fragment
    ):
        return False, None
    host = parsed.hostname.lower()
    labels = host.split(".")
    if len(host) > 253 or any(DNS_LABEL_PATTERN.fullmatch(label) is None for label in labels):
        return False, None
    path = parsed.path or "/"
    segments = path.split("/")[1:]
    if segments and segments[-1] == "":
        segments = segments[:-1]
    if any(
        segment in {".", ".."} or PATH_SEGMENT_PATTERN.fullmatch(segment) is None
        for segment in segments
    ):
        return False, None
    canonical = urlunsplit(("https", host, path, "", ""))
    return hmac.compare_digest(value, canonical), host


@functools.lru_cache(maxsize=1)
def _get_schema_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_errors(receipt: dict[str, Any]) -> list[Any]:
    validator = _get_schema_validator()
    return sorted(validator.iter_errors(receipt), key=lambda item: (list(item.absolute_path), item.message))


def _rfc3339_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or RFC3339_PATTERN.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def validate_resource_resolution_receipt(receipt: Any) -> dict[str, Any]:
    """Return a stable, non-reflective validation result."""

    if not isinstance(receipt, dict):
        return _result(False, [RESOURCE_SCHEMA_INVALID])
    if "publisher_identity" not in receipt:
        return _result(False, [RESOURCE_PUBLISHER_IDENTITY_REQUIRED])
    digest = receipt.get("content_digest")
    if not isinstance(digest, str) or DIGEST_PATTERN.fullmatch(digest) is None:
        return _result(False, [RESOURCE_DIGEST_INVALID])
    if "policy_decision_ref" not in receipt:
        return _result(False, [RESOURCE_POLICY_DECISION_REQUIRED])
    if "execution_effect_ref" in receipt:
        return _result(False, [RESOURCE_EXECUTION_EFFECT_UNBOUND])
    if _schema_errors(receipt):
        return _result(False, [RESOURCE_SCHEMA_INVALID])

    created_at = _rfc3339_timestamp(receipt.get("created_at"))
    retrieval_timestamp = _rfc3339_timestamp(receipt.get("retrieval_timestamp"))
    if created_at is None or retrieval_timestamp is None or retrieval_timestamp > created_at:
        return _result(False, [RESOURCE_SCHEMA_INVALID])

    uri_valid, resolved_host = _canonical_https_uri(receipt.get("resolved_uri"))
    if not uri_valid or resolved_host != receipt.get("registry_or_host"):
        return _result(False, [RESOURCE_RESOLVED_URI_INVALID])

    content_binding = receipt["content_binding"]
    encoded = content_binding["inline_base64"]
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError):
        return _result(False, [RESOURCE_DIGEST_INVALID])
    if base64.b64encode(raw).decode("ascii") != encoded:
        return _result(False, [RESOURCE_DIGEST_INVALID])
    if len(raw) != content_binding["byte_length"]:
        return _result(False, [RESOURCE_DIGEST_INVALID])
    if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), digest):
        return _result(False, [RESOURCE_DIGEST_INVALID])

    expected_receipt_digest = compute_receipt_digest(receipt)
    declared_receipt_digest = receipt["integrity"]["receipt_digest"]
    if not hmac.compare_digest(expected_receipt_digest, declared_receipt_digest):
        return _result(False, [RESOURCE_RECEIPT_DIGEST_MISMATCH])
    return _result(True, [], expected_receipt_digest)
