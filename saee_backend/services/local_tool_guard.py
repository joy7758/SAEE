"""Fail-closed input guard for the local SAEE evidence tool prototype.

This module parses inert JSON only. It never fetches references, imports caller
content, executes code, opens a network connection, or persists input.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA_PATH = ROOT / "agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json"
MAX_INPUT_BYTES = 1024 * 1024
MAX_NESTING_DEPTH = 32
MAX_NODE_COUNT = 50_000
MAX_KEY_LENGTH = 256

CLAIM_PROFILE_MAP = {
    "RESOURCE_AUTHENTICITY": "resource-authenticity",
    "AUTHORIZED_AGENT_ACTION": "authorized-agent-action",
    "HUMAN_OVERSIGHT": "human-oversight",
    "EXECUTION_BOUNDARY": "execution-boundary",
}


class LocalToolInputError(ValueError):
    """Stable fail-closed rejection with a machine-readable reason code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _reject_constant(_: str) -> None:
    raise LocalToolInputError("TOOL_INPUT_UNSUPPORTED_TYPE")


def _closed_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise LocalToolInputError("TOOL_INPUT_DUPLICATE_KEY")
        result[key] = value
    return result


def _validate_json_tree(value: Any) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    node_count = 0
    while stack:
        current, depth = stack.pop()
        node_count += 1
        if node_count > MAX_NODE_COUNT:
            raise LocalToolInputError("TOOL_INPUT_EXCESSIVE_COMPLEXITY")
        if depth > MAX_NESTING_DEPTH:
            raise LocalToolInputError("TOOL_INPUT_EXCESSIVE_NESTING")
        if isinstance(current, dict):
            for key, child in current.items():
                if not isinstance(key, str) or not key or len(key) > MAX_KEY_LENGTH:
                    raise LocalToolInputError("TOOL_INPUT_UNSUPPORTED_TYPE")
                stack.append((child, depth + 1))
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in current)
        elif current is None or isinstance(current, (str, bool, int)):
            continue
        elif isinstance(current, float):
            if not math.isfinite(current):
                raise LocalToolInputError("TOOL_INPUT_UNSUPPORTED_TYPE")
        else:
            raise LocalToolInputError("TOOL_INPUT_UNSUPPORTED_TYPE")


def _encoded_size(value: dict[str, Any]) -> int:
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise LocalToolInputError("TOOL_INPUT_UNSUPPORTED_TYPE") from exc
    return len(encoded)


def _normalize_request(request: bytes | str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(request, bytes):
        if len(request) > MAX_INPUT_BYTES:
            raise LocalToolInputError("TOOL_INPUT_TOO_LARGE")
        try:
            text = request.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise LocalToolInputError("TOOL_INPUT_INVALID_JSON") from exc
    elif isinstance(request, str):
        try:
            size = len(request.encode("utf-8"))
        except UnicodeEncodeError as exc:
            raise LocalToolInputError("TOOL_INPUT_INVALID_JSON") from exc
        if size > MAX_INPUT_BYTES:
            raise LocalToolInputError("TOOL_INPUT_TOO_LARGE")
        text = request
    elif isinstance(request, dict):
        _validate_json_tree(request)
        if _encoded_size(request) > MAX_INPUT_BYTES:
            raise LocalToolInputError("TOOL_INPUT_TOO_LARGE")
        return request
    else:
        raise LocalToolInputError("TOOL_INPUT_UNSUPPORTED_TYPE")

    try:
        parsed = json.loads(text, object_pairs_hook=_closed_object, parse_constant=_reject_constant)
    except LocalToolInputError:
        raise
    except RecursionError as exc:
        raise LocalToolInputError("TOOL_INPUT_EXCESSIVE_NESTING") from exc
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise LocalToolInputError("TOOL_INPUT_INVALID_JSON") from exc
    if not isinstance(parsed, dict):
        raise LocalToolInputError("TOOL_INPUT_UNSUPPORTED_TYPE")
    _validate_json_tree(parsed)
    return parsed


def _validate_semantics(request: dict[str, Any]) -> None:
    if "evidence_object" not in request or not isinstance(request.get("evidence_object"), dict) or not request["evidence_object"]:
        raise LocalToolInputError("TOOL_EVIDENCE_OBJECT_REQUIRED")
    claim = request.get("accountability_claim")
    if claim not in CLAIM_PROFILE_MAP:
        raise LocalToolInputError("TOOL_CLAIM_UNKNOWN")
    profile = request.get("evaluation_profile")
    if profile not in set(CLAIM_PROFILE_MAP.values()):
        raise LocalToolInputError("TOOL_PROFILE_UNKNOWN")
    if CLAIM_PROFILE_MAP[claim] != profile:
        raise LocalToolInputError("TOOL_CLAIM_PROFILE_MISMATCH")

    schema = json.loads(REQUEST_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(request), key=lambda error: list(error.absolute_path))
    if errors:
        raise LocalToolInputError("TOOL_INPUT_SCHEMA_INVALID")


def validate_local_tool_request(request: bytes | str | dict[str, Any]) -> dict[str, Any]:
    """Return a validated closed request or raise ``LocalToolInputError``."""

    normalized = _normalize_request(request)
    _validate_semantics(normalized)
    # JSON round-trip creates an isolated JSON-only copy without mutating input.
    return json.loads(json.dumps(normalized, ensure_ascii=False, allow_nan=False))
