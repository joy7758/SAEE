"""Bounded clean-room integrity traits for SAEE Agent Evidence migration.

The canonicalization function intentionally supports only an ASCII, integer,
boolean, null, array and object subset whose output is compatible with JCS
ordering and scalar rules. It rejects floats, non-ASCII strings and integers
outside the interoperable JSON range instead of claiming full RFC 8785 support.

Event chains and Merkle roots provide tamper-evident local bindings only. They
do not authenticate event origin, identity, authorization or completeness.
"""

from __future__ import annotations

import copy
import base64
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


MAX_SAFE_INTEGER = 9_007_199_254_740_991


class IntegritySubsetError(ValueError):
    """Raised when a value falls outside the declared canonical subset."""


def _validate_subset(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if not -MAX_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
            raise IntegritySubsetError(f"integer outside safe range at {path}")
        return
    if isinstance(value, float):
        raise IntegritySubsetError(f"floats are outside the bounded subset at {path}")
    if isinstance(value, str):
        if not value.isascii():
            raise IntegritySubsetError(f"non-ASCII string outside bounded subset at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_subset(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise IntegritySubsetError(f"non-ASCII object key outside bounded subset at {path}")
            _validate_subset(item, f"{path}.{key}")
        return
    raise IntegritySubsetError(f"unsupported JSON value at {path}: {type(value).__name__}")


def canonical_jcs_safe_subset(value: Any) -> bytes:
    """Serialize the declared JCS-safe subset deterministically as UTF-8."""

    _validate_subset(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def event_digest(event: dict[str, Any]) -> str:
    return _sha256_bytes(canonical_jcs_safe_subset(event))


def build_event_chain(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Bind ordered events by digest and previous-chain digest."""

    if not events:
        raise IntegritySubsetError("event chain requires at least one event")
    indices = [event.get("event_index") for event in events]
    if indices != list(range(len(events))):
        raise IntegritySubsetError("event indices must be contiguous from zero")
    event_ids = [event.get("event_id") for event in events]
    if any(not isinstance(value, str) or not value for value in event_ids):
        raise IntegritySubsetError("event_id is required")
    if len(event_ids) != len(set(event_ids)):
        raise IntegritySubsetError("event_id values must be unique")

    chain: list[dict[str, Any]] = []
    previous: str | None = None
    for event in copy.deepcopy(events):
        basis = {
            "event_index": event["event_index"],
            "event_id": event["event_id"],
            "event_digest": event_digest(event),
            "previous_chain_digest": previous,
        }
        entry = {**basis, "chain_digest": _sha256_bytes(canonical_jcs_safe_subset(basis))}
        chain.append(entry)
        previous = entry["chain_digest"]
    return chain


def verify_event_chain(events: list[dict[str, Any]], chain: Any) -> bool:
    if not isinstance(chain, list):
        return False
    try:
        expected = build_event_chain(events)
    except (IntegritySubsetError, TypeError, ValueError):
        return False
    return expected == chain


def merkle_root(digests: list[str]) -> str:
    """Compute a SHA-256 binary Merkle root, duplicating an odd final node."""

    if not digests:
        raise IntegritySubsetError("Merkle root requires at least one digest")
    nodes: list[bytes] = []
    for digest in digests:
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            raise IntegritySubsetError("Merkle leaf must be a sha256-prefixed digest")
        try:
            raw = bytes.fromhex(digest.removeprefix("sha256:"))
        except ValueError as exc:
            raise IntegritySubsetError("Merkle leaf contains invalid hex") from exc
        if len(raw) != 32:
            raise IntegritySubsetError("Merkle leaf must contain 32 digest bytes")
        nodes.append(raw)

    while len(nodes) > 1:
        if len(nodes) % 2:
            nodes.append(nodes[-1])
        nodes = [
            hashlib.sha256(nodes[index] + nodes[index + 1]).digest()
            for index in range(0, len(nodes), 2)
        ]
    return "sha256:" + nodes[0].hex()


def verify_merkle_root(digests: list[str], expected_root: Any) -> bool:
    try:
        return merkle_root(digests) == expected_root
    except (IntegritySubsetError, TypeError, ValueError):
        return False


def verify_ed25519_signature(
    message: bytes,
    public_key_pem: str,
    signature_base64: str,
    *,
    openssl_path: str | None = None,
) -> dict[str, Any]:
    """Verify one bounded Ed25519 signature with an existing system OpenSSL.

    No shell or network is used and no dependency is installed. Only public
    verification material is written to a temporary directory.
    """

    base = {
        "check": "NOT_RUN",
        "reason": "openssl_unavailable",
        "local_crypto_subprocess_started": False,
        "openssl_path": None,
        "openssl_version": None,
    }
    if (
        not isinstance(message, bytes)
        or not 1 <= len(message) <= 1024
        or not isinstance(public_key_pem, str)
        or not public_key_pem.isascii()
        or len(public_key_pem) > 4096
        or not public_key_pem.startswith("-----BEGIN PUBLIC KEY-----\n")
        or not public_key_pem.endswith("-----END PUBLIC KEY-----\n")
        or not isinstance(signature_base64, str)
        or len(signature_base64) > 128
    ):
        return {**base, "check": "FAIL", "reason": "signature_input_invalid"}
    try:
        signature = base64.b64decode(signature_base64, validate=True)
    except (ValueError, TypeError):
        return {**base, "check": "FAIL", "reason": "signature_input_invalid"}
    if len(signature) != 64:
        return {**base, "check": "FAIL", "reason": "signature_input_invalid"}

    executable = openssl_path or shutil.which("openssl")
    if not executable or not Path(executable).is_file():
        return base
    try:
        version_run = subprocess.run(
            [executable, "version"], check=False, capture_output=True, timeout=5
        )
    except (OSError, subprocess.TimeoutExpired):
        return {**base, "reason": "openssl_execution_failed"}
    version = version_run.stdout.decode("ascii", errors="replace").strip()
    if version_run.returncode != 0 or not version.startswith("OpenSSL 3."):
        return {
            **base,
            "check": "FAIL",
            "reason": "openssl_version_not_allowed",
            "local_crypto_subprocess_started": True,
            "openssl_path": executable,
            "openssl_version": version or None,
        }

    with tempfile.TemporaryDirectory(prefix="saee-ed25519-verify-") as temp:
        root = Path(temp)
        key_path = root / "public.pem"
        message_path = root / "message.bin"
        signature_path = root / "signature.bin"
        key_path.write_text(public_key_pem, encoding="ascii")
        message_path.write_bytes(message)
        signature_path.write_bytes(signature)
        try:
            verify_run = subprocess.run(
                [
                    executable,
                    "pkeyutl",
                    "-verify",
                    "-pubin",
                    "-inkey",
                    str(key_path),
                    "-rawin",
                    "-in",
                    str(message_path),
                    "-sigfile",
                    str(signature_path),
                ],
                check=False,
                capture_output=True,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            return {
                **base,
                "reason": "openssl_execution_failed",
                "local_crypto_subprocess_started": True,
                "openssl_path": executable,
                "openssl_version": version,
            }
    return {
        "check": "PASS" if verify_run.returncode == 0 else "FAIL",
        "reason": (
            "verified_by_system_openssl"
            if verify_run.returncode == 0
            else "signature_verification_failed"
        ),
        "local_crypto_subprocess_started": True,
        "openssl_path": executable,
        "openssl_version": version,
    }
