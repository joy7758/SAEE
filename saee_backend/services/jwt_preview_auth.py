"""Local signed JWT preview authentication for the public SAEE API shell.

This module validates HS256-signed preview tokens with standard-library
cryptography only. It is a controlled-preview hardening layer, not production
OIDC, not SSO, not JWKS validation, and not a production-auth readiness claim.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

from saee_backend.config import SaeeBackendSettings
from saee_backend.services.public_input_contract import (
    PublicInputBoundaryError,
    validate_public_identifier,
    validate_public_text_no_sensitive,
)


REQUIRED_PREVIEW_CLAIMS = (
    "iss",
    "sub",
    "aud",
    "exp",
    "iat",
    "tenant_id",
    "roles",
)
ALLOWED_PREVIEW_CLAIMS = frozenset(REQUIRED_PREVIEW_CLAIMS)
ALLOWED_PREVIEW_HEADER_KEYS = frozenset({"alg", "typ"})


class JwtPreviewAuthError(ValueError):
    """Raised when a preview JWT is missing, malformed, or invalid."""


@dataclass(frozen=True)
class JwtPreviewClaims:
    subject: str
    issuer: str
    audience: str
    tenant_id: str
    roles: tuple[str, ...]
    expires_at: int
    issued_at: int
    raw_claims: dict[str, Any]


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode((value + padding).encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise JwtPreviewAuthError("JWT segment is not valid base64url.") from exc


def _b64url_json(value: str) -> dict[str, Any]:
    try:
        decoded = json.loads(_b64url_decode(value).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JwtPreviewAuthError("JWT segment is not valid JSON.") from exc
    if not isinstance(decoded, dict):
        raise JwtPreviewAuthError("JWT segment must be a JSON object.")
    return decoded


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _secret_from_settings(settings: SaeeBackendSettings) -> str:
    # The dataclass intentionally stores only configured/not-configured status.
    # The secret itself stays in process environment and is read by config load.
    import os

    return os.environ.get("SAEE_PREVIEW_JWT_HS256_SECRET", "").strip()


def sign_preview_jwt(
    claims: dict[str, Any],
    secret: str,
    *,
    header: dict[str, Any] | None = None,
) -> str:
    """Return an HS256 preview JWT for local tests and controlled previews."""

    if not secret:
        raise JwtPreviewAuthError("Preview JWT secret is not configured.")
    jwt_header = {"alg": "HS256", "typ": "JWT"}
    if header:
        jwt_header.update(header)
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(jwt_header, sort_keys=True, separators=(",", ":")).encode("utf-8")),
            _b64url_encode(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return signing_input + "." + _b64url_encode(signature)


def validate_preview_jwt(
    token: str,
    settings: SaeeBackendSettings,
    *,
    now: int | None = None,
) -> JwtPreviewClaims:
    """Validate a controlled-preview HS256 JWT and return normalized claims."""

    if not settings.require_jwt_preview_auth:
        raise JwtPreviewAuthError("Preview JWT auth is not enabled.")
    secret = _secret_from_settings(settings)
    if not secret:
        raise JwtPreviewAuthError("Preview JWT secret is not configured.")
    if not settings.preview_jwt_issuer or not settings.preview_jwt_audience:
        raise JwtPreviewAuthError("Preview JWT issuer and audience must be configured.")

    parts = token.split(".")
    if len(parts) != 3:
        raise JwtPreviewAuthError("JWT must have three segments.")
    header = _b64url_json(parts[0])
    claims = _b64url_json(parts[1])
    if header.get("alg") != "HS256":
        raise JwtPreviewAuthError("Preview JWT must use HS256.")
    if header.get("typ") not in {None, "JWT"}:
        raise JwtPreviewAuthError("Preview JWT typ must be JWT when present.")
    if not set(header).issubset(ALLOWED_PREVIEW_HEADER_KEYS):
        raise JwtPreviewAuthError("Preview JWT header contains unsupported fields.")

    signing_input = ".".join(parts[:2])
    expected_signature = hmac.new(
        secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256
    ).digest()
    actual_signature = _b64url_decode(parts[2])
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise JwtPreviewAuthError("JWT signature is invalid.")

    missing = [claim for claim in REQUIRED_PREVIEW_CLAIMS if claim not in claims]
    if missing:
        raise JwtPreviewAuthError("JWT missing required claims: " + ", ".join(missing))
    if set(claims) != ALLOWED_PREVIEW_CLAIMS:
        raise JwtPreviewAuthError("JWT claims must match the closed synthetic-preview contract.")
    if claims.get("iss") != settings.preview_jwt_issuer:
        raise JwtPreviewAuthError("JWT issuer is invalid.")
    if claims.get("aud") != settings.preview_jwt_audience:
        raise JwtPreviewAuthError("JWT audience is invalid.")

    current_time = int(time.time()) if now is None else now
    exp = claims.get("exp")
    iat = claims.get("iat")
    if not isinstance(exp, int) or exp <= current_time:
        raise JwtPreviewAuthError("JWT is expired or exp is invalid.")
    if not isinstance(iat, int) or iat > current_time + 60:
        raise JwtPreviewAuthError("JWT iat is invalid.")

    roles_raw = claims.get("roles")
    if not isinstance(roles_raw, list) or not roles_raw:
        raise JwtPreviewAuthError("JWT roles must be a non-empty list.")
    try:
        roles = tuple(
            validate_public_identifier(role, field_name="JWT role")
            for role in roles_raw
            if isinstance(role, str) and role.strip()
        )
    except PublicInputBoundaryError as exc:
        raise JwtPreviewAuthError(str(exc)) from exc
    if not roles or len(roles) != len(roles_raw):
        raise JwtPreviewAuthError("JWT roles must include only public-safe role identifiers.")

    tenant_id = claims.get("tenant_id")
    subject = claims.get("sub")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise JwtPreviewAuthError("JWT tenant_id must be a non-empty string.")
    if not isinstance(subject, str) or not subject.strip():
        raise JwtPreviewAuthError("JWT sub must be a non-empty string.")
    try:
        tenant_id = validate_public_identifier(tenant_id, field_name="JWT tenant_id")
        subject = validate_public_identifier(subject, field_name="JWT sub")
        validate_public_text_no_sensitive(str(claims["iss"]), field_name="JWT iss", max_length=256)
        validate_public_text_no_sensitive(str(claims["aud"]), field_name="JWT aud", max_length=256)
    except PublicInputBoundaryError as exc:
        raise JwtPreviewAuthError(str(exc)) from exc

    return JwtPreviewClaims(
        subject=subject.strip(),
        issuer=str(claims["iss"]),
        audience=str(claims["aud"]),
        tenant_id=tenant_id,
        roles=roles,
        expires_at=exp,
        issued_at=iat,
        raw_claims=claims,
    )


def validate_authorization_header(
    authorization: str | None,
    settings: SaeeBackendSettings,
    *,
    now: int | None = None,
) -> JwtPreviewClaims:
    """Validate `Authorization: Bearer <token>` for preview JWT auth."""

    if not authorization:
        raise JwtPreviewAuthError("Missing Authorization bearer token.")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise JwtPreviewAuthError("Authorization header must use Bearer scheme.")
    return validate_preview_jwt(authorization[len(prefix) :].strip(), settings, now=now)
