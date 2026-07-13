"""Public-safe input contract for the SAEE API shell.

This boundary rejects high-confidence credential and personal-data shapes plus
closed sensitive field names. It is not general DLP and does not inspect
external systems.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any


PUBLIC_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
CREDENTIAL_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\bbce-v3/[A-Za-z0-9_+/=-]{12,}"),
)
PERSONAL_DATA_PATTERNS = (
    re.compile(r"(?i)(?<![A-Z0-9._%+-])[A-Z0-9._%+-]{1,64}@[A-Z0-9.-]{1,253}\.[A-Z]{2,24}(?![A-Z0-9.-])"),
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    re.compile(r"(?<!\d)\d{6}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[0-9Xx](?![A-Za-z0-9])"),
)
FORBIDDEN_CONFIG_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "credential",
    "credentials",
    "password",
    "secret",
    "token",
}
FORBIDDEN_PERSONAL_DATA_KEYS = {
    "address",
    "birth_date",
    "customer_email",
    "customer_id",
    "customer_name",
    "email",
    "full_name",
    "id_card",
    "identity_number",
    "mobile",
    "name",
    "personal_data",
    "phone",
    "real_name",
}
ALLOWED_AGENT_CONFIG_KEYS = {"policy", "workflow"}


class PublicInputBoundaryError(ValueError):
    """Raised without reflecting the rejected input value."""


def contains_high_confidence_credential(value: str) -> bool:
    return any(pattern.search(value) for pattern in CREDENTIAL_PATTERNS)


def contains_high_confidence_personal_data(value: str) -> bool:
    return any(pattern.search(value) for pattern in PERSONAL_DATA_PATTERNS)


def validate_public_identifier(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not PUBLIC_IDENTIFIER_PATTERN.fullmatch(value):
        raise PublicInputBoundaryError(f"{field_name} must be a public-safe identifier")
    if contains_high_confidence_credential(value):
        raise PublicInputBoundaryError(f"{field_name} must not contain credential material")
    if contains_high_confidence_personal_data(value):
        raise PublicInputBoundaryError(f"{field_name} must not contain personal data")
    return value


def validate_public_text_no_sensitive(
    value: str,
    *,
    field_name: str,
    max_length: int,
) -> str:
    """Validate bounded display text without claiming general DLP coverage."""
    if not isinstance(value, str) or not value.strip():
        raise PublicInputBoundaryError(f"{field_name} must be non-empty public text")
    if len(value) > max_length:
        raise PublicInputBoundaryError(f"{field_name} exceeds the public text limit")
    if CONTROL_CHARACTER_PATTERN.search(value):
        raise PublicInputBoundaryError(f"{field_name} must not contain control characters")
    if contains_high_confidence_credential(value):
        raise PublicInputBoundaryError(f"{field_name} must not contain credential material")
    if contains_high_confidence_personal_data(value):
        raise PublicInputBoundaryError(f"{field_name} must not contain personal data")
    return value


def validate_secret_free_config(value: Any, *, depth: int = 0) -> None:
    if depth > 16:
        raise PublicInputBoundaryError("agent config nesting exceeds the public boundary")
    if isinstance(value, str):
        normalized_value = unicodedata.normalize("NFKC", value)
        if normalized_value != value:
            raise PublicInputBoundaryError("agent config must already use normalized public identifiers")
        if CONTROL_CHARACTER_PATTERN.search(normalized_value):
            raise PublicInputBoundaryError("agent config contains control characters")
        if contains_high_confidence_credential(normalized_value):
            raise PublicInputBoundaryError("agent config must not contain credential material")
        if contains_high_confidence_personal_data(normalized_value):
            raise PublicInputBoundaryError("agent config must not contain personal data")
        if not PUBLIC_IDENTIFIER_PATTERN.fullmatch(normalized_value):
            raise PublicInputBoundaryError("agent config strings must be public-safe identifiers")
        return
    if isinstance(value, Mapping):
        if depth > 0:
            raise PublicInputBoundaryError("nested agent config objects are outside the closed contract")
        for key, nested in value.items():
            if not isinstance(key, str):
                raise PublicInputBoundaryError("agent config keys must be strings")
            normalized = unicodedata.normalize("NFKC", key).strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_CONFIG_KEYS:
                raise PublicInputBoundaryError("agent config contains a credential field")
            if normalized in FORBIDDEN_PERSONAL_DATA_KEYS:
                raise PublicInputBoundaryError("agent config contains a personal-data field")
            if normalized not in ALLOWED_AGENT_CONFIG_KEYS:
                raise PublicInputBoundaryError("agent config contains a field outside the closed contract")
            validate_secret_free_config(nested, depth=depth + 1)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        raise PublicInputBoundaryError("agent config arrays are outside the closed contract")
    if value is None or isinstance(value, (bool, int, float)):
        return
    raise PublicInputBoundaryError("agent config contains a value outside the closed JSON contract")


def validate_scenario_request(req: Any) -> None:
    if req.experiment_id is not None:
        validate_public_identifier(req.experiment_id, field_name="experiment_id")
    validate_public_identifier(req.environment.scenario_type, field_name="scenario_type")
    agent_ids: list[str] = []
    for agent in req.agents:
        agent_ids.append(validate_public_identifier(agent.agent_id, field_name="agent_id"))
        validate_secret_free_config(agent.config)
    if len(agent_ids) != len(set(agent_ids)):
        raise PublicInputBoundaryError("agent_id values must be unique")
