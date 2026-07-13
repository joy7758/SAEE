"""Provider-neutral, offline-only signed OIDC/JWKS verifier core.

This module validates synthetic, public-safe identity fixtures against a
caller-supplied local JWKS document. It never discovers issuers, fetches keys,
opens a network connection, manages sessions, or claims production OIDC
availability. The deliberately closed contract keeps identity evidence
agent-readable and fails closed on algorithm confusion and personal data.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping
from urllib.parse import urlsplit, urlunsplit

from saee_backend.services.authorization_context import (
    AuthorizedPrincipalContext,
    issue_authorized_principal_context,
)
from saee_backend.services.public_input_contract import (
    PublicInputBoundaryError,
    validate_public_identifier,
)
from saee_backend.services.rbac_policy import RbacPolicyError, evaluate_rbac_route


ALGORITHM = "RS256"
AUTH_SOURCE = "oidc_jwks_offline_verified"
HEADER_KEYS = frozenset({"alg", "typ", "kid"})
REQUIRED_CLAIMS = frozenset({"iss", "sub", "aud", "exp", "iat", "tenant_id", "roles"})
OPTIONAL_CLAIMS = frozenset({"nbf", "jti"})
JWKS_KEYS = frozenset({"keys"})
JWK_KEYS = frozenset({"kty", "kid", "use", "alg", "n", "e"})
PRIVATE_JWK_KEYS = frozenset({"d", "p", "q", "dp", "dq", "qi", "oth"})
SHA256_DIGEST_INFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")
MAX_TOKEN_LIFETIME_SECONDS = 3600
DEFAULT_CLOCK_SKEW_SECONDS = 60
MAX_CLOCK_SKEW_SECONDS = 300
MAX_JWKS_KEYS = 8
ALLOWED_RSA_BITS = frozenset({2048, 3072, 4096})
RSA_PUBLIC_EXPONENT = 65537
BASE64URL_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
DNS_LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
ISSUER_PATH_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9._~-]+$")


class OfflineOidcVerificationError(ValueError):
    """Raised with a fixed, non-reflective message for rejected material."""


@dataclass(frozen=True)
class VerifiedOidcPrincipal:
    issuer: str
    subject: str
    audience: str
    tenant_id: str
    roles: tuple[str, ...]
    key_id: str
    token_sha256: str
    verified_at: int
    auth_source: str = AUTH_SOURCE
    verification_receipt: str = field(default="", repr=False)


def _fail(message: str) -> None:
    raise OfflineOidcVerificationError(message)


def _decode_segment(segment: str, *, label: str, max_length: int = 16384) -> bytes:
    if (
        not isinstance(segment, str)
        or not segment
        or len(segment) > max_length
        or BASE64URL_PATTERN.fullmatch(segment) is None
    ):
        _fail(f"OIDC {label} is malformed")
    try:
        padding = "=" * (-len(segment) % 4)
        decoded = base64.b64decode(segment + padding, altchars=b"-_", validate=True)
    except (ValueError, TypeError) as exc:
        raise OfflineOidcVerificationError(f"OIDC {label} is malformed") from exc
    canonical = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
    if not hmac.compare_digest(segment, canonical):
        _fail(f"OIDC {label} is malformed")
    return decoded


def _closed_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("OIDC JSON object contains duplicate keys")
        result[key] = value
    return result


def _decode_object(segment: str, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            _decode_segment(segment, label=label).decode("utf-8"),
            object_pairs_hook=_closed_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise OfflineOidcVerificationError(f"OIDC {label} is malformed") from exc
    if not isinstance(value, dict):
        _fail(f"OIDC {label} must be an object")
    return value


def _unsigned_integer(value: str, *, label: str, max_length: int) -> int:
    raw = _decode_segment(value, label=label, max_length=max_length)
    if not raw or (len(raw) > 1 and raw[0] == 0):
        _fail(f"OIDC {label} is not canonical")
    return int.from_bytes(raw, "big")


def validate_local_jwks(jwks: Mapping[str, Any]) -> dict[str, tuple[int, int]]:
    """Return unique local RSA public keys indexed by ``kid``."""

    if not isinstance(jwks, Mapping) or set(jwks) != JWKS_KEYS:
        _fail("OIDC local JWKS schema is invalid")
    keys = jwks.get("keys")
    if not isinstance(keys, list) or not keys or len(keys) > MAX_JWKS_KEYS:
        _fail("OIDC local JWKS keys are required")
    parsed: dict[str, tuple[int, int]] = {}
    for item in keys:
        if not isinstance(item, Mapping):
            _fail("OIDC local JWK entry is invalid")
        if PRIVATE_JWK_KEYS.intersection(item):
            _fail("OIDC local JWK must contain public material only")
        if set(item) != JWK_KEYS:
            _fail("OIDC local JWK schema is invalid")
        if item.get("kty") != "RSA" or item.get("use") != "sig" or item.get("alg") != ALGORITHM:
            _fail("OIDC local JWK parameters are invalid")
        try:
            kid = validate_public_identifier(item.get("kid"), field_name="kid")
        except (PublicInputBoundaryError, TypeError) as exc:
            raise OfflineOidcVerificationError("OIDC local JWK kid is invalid") from exc
        if kid in parsed:
            _fail("OIDC local JWKS contains duplicate kid")
        n = _unsigned_integer(item.get("n"), label="JWK modulus", max_length=683)
        e = _unsigned_integer(item.get("e"), label="JWK exponent", max_length=6)
        if n.bit_length() not in ALLOWED_RSA_BITS or n % 2 == 0 or e != RSA_PUBLIC_EXPONENT:
            _fail("OIDC local JWK strength is invalid")
        parsed[kid] = (n, e)
    return parsed


def _verify_rs256(signing_input: bytes, signature: bytes, *, n: int, e: int) -> None:
    length = (n.bit_length() + 7) // 8
    if len(signature) != length:
        _fail("OIDC token signature is invalid")
    signature_integer = int.from_bytes(signature, "big")
    if signature_integer >= n:
        _fail("OIDC token signature is invalid")
    encoded = pow(signature_integer, e, n).to_bytes(length, "big")
    digest_info = SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(signing_input).digest()
    padding_length = length - len(digest_info) - 3
    if padding_length < 8:
        _fail("OIDC token signature is invalid")
    expected = b"\x00\x01" + b"\xff" * padding_length + b"\x00" + digest_info
    if not hmac.compare_digest(encoded, expected):
        _fail("OIDC token signature is invalid")


def _public_identifier(value: Any, *, label: str) -> str:
    try:
        return validate_public_identifier(value, field_name=label)
    except (PublicInputBoundaryError, TypeError) as exc:
        raise OfflineOidcVerificationError(f"OIDC {label} is invalid") from exc


def _https_issuer(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 512
        or not value.isascii()
        or any(character.isspace() or ord(character) < 0x20 or ord(character) == 0x7F for character in value)
        or "\\" in value
        or "%" in value
    ):
        _fail("OIDC issuer is invalid")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or "//" in parsed.path
        or any(segment in {".", ".."} for segment in parsed.path.split("/"))
    ):
        _fail("OIDC issuer is invalid")
    host = parsed.hostname.lower()
    labels = host.split(".")
    if len(host) > 253 or any(DNS_LABEL_PATTERN.fullmatch(label) is None for label in labels):
        _fail("OIDC issuer host is invalid")
    path = parsed.path or "/"
    path_segments = path.split("/")[1:]
    if path_segments and path_segments[-1] == "":
        path_segments = path_segments[:-1]
    if any(ISSUER_PATH_SEGMENT_PATTERN.fullmatch(segment) is None for segment in path_segments):
        _fail("OIDC issuer path is invalid")
    try:
        port = parsed.port
    except ValueError as exc:
        raise OfflineOidcVerificationError("OIDC issuer is invalid") from exc
    netloc = f"{host}:{port}" if port is not None else host
    canonical = urlunsplit(("https", netloc, path, "", ""))
    if value != canonical:
        _fail("OIDC issuer is not canonical")
    return value


def _receipt_payload(principal: VerifiedOidcPrincipal) -> bytes:
    return json.dumps(
        {
            "audience": principal.audience,
            "auth_source": principal.auth_source,
            "issuer": principal.issuer,
            "key_id": principal.key_id,
            "roles": list(principal.roles),
            "subject": principal.subject,
            "tenant_id": principal.tenant_id,
            "token_sha256": principal.token_sha256,
            "verified_at": principal.verified_at,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _receipt(secret: str, principal: VerifiedOidcPrincipal) -> str:
    if not isinstance(secret, str) or len(secret) < 32:
        _fail("OIDC verification receipt secret is not configured securely")
    return hmac.new(secret.encode("utf-8"), b"saee-offline-oidc-receipt-v1\x00" + _receipt_payload(principal), hashlib.sha256).hexdigest()


def verify_offline_oidc_token(
    token: str,
    *,
    local_jwks: Mapping[str, Any],
    expected_issuer: str,
    expected_audience: str,
    now: int,
    verification_receipt_secret: str,
    clock_skew_seconds: int = DEFAULT_CLOCK_SKEW_SECONDS,
) -> VerifiedOidcPrincipal:
    """Verify a compact RS256 token without network access or value reflection."""

    if not isinstance(token, str) or len(token) > 16384:
        _fail("OIDC compact token is malformed")
    expected_issuer = _https_issuer(expected_issuer)
    expected_audience = _public_identifier(expected_audience, label="expected_audience")
    parts = token.split(".")
    if len(parts) != 3:
        _fail("OIDC compact token is malformed")
    header = _decode_object(parts[0], label="header")
    claims = _decode_object(parts[1], label="claims")
    if set(header) != HEADER_KEYS or header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
        _fail("OIDC token header is outside the closed contract")
    kid = _public_identifier(header.get("kid"), label="kid")
    keys = validate_local_jwks(local_jwks)
    key = keys.get(kid)
    if key is None:
        _fail("OIDC token key is not trusted")
    _verify_rs256(
        f"{parts[0]}.{parts[1]}".encode("ascii"),
        _decode_segment(parts[2], label="signature"),
        n=key[0],
        e=key[1],
    )
    if set(claims) - (REQUIRED_CLAIMS | OPTIONAL_CLAIMS) or REQUIRED_CLAIMS - set(claims):
        _fail("OIDC token claims are outside the closed contract")
    if claims.get("iss") != expected_issuer or claims.get("aud") != expected_audience:
        _fail("OIDC token trust binding is invalid")
    if (
        not isinstance(now, int)
        or isinstance(now, bool)
        or not isinstance(clock_skew_seconds, int)
        or isinstance(clock_skew_seconds, bool)
        or not 0 <= clock_skew_seconds <= MAX_CLOCK_SKEW_SECONDS
    ):
        _fail("OIDC verifier clock configuration is invalid")
    exp, iat, nbf = claims.get("exp"), claims.get("iat"), claims.get("nbf")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (exp, iat)):
        _fail("OIDC token time claims are invalid")
    if nbf is not None and (isinstance(nbf, bool) or not isinstance(nbf, int)):
        _fail("OIDC token time claims are invalid")
    if exp <= now - clock_skew_seconds or iat > now + clock_skew_seconds:
        _fail("OIDC token time window is invalid")
    if nbf is not None and nbf > now + clock_skew_seconds:
        _fail("OIDC token time window is invalid")
    if exp <= iat or exp - iat > MAX_TOKEN_LIFETIME_SECONDS:
        _fail("OIDC token lifetime is invalid")
    subject = _public_identifier(claims.get("sub"), label="subject")
    tenant_id = _public_identifier(claims.get("tenant_id"), label="tenant_id")
    issuer = _https_issuer(claims.get("iss"))
    audience = _public_identifier(claims.get("aud"), label="audience")
    roles_raw = claims.get("roles")
    if not isinstance(roles_raw, list) or not roles_raw:
        _fail("OIDC roles are invalid")
    roles = tuple(_public_identifier(role, label="role") for role in roles_raw)
    if len(set(roles)) != len(roles):
        _fail("OIDC roles are invalid")
    if "jti" in claims:
        _public_identifier(claims["jti"], label="jti")
    unsigned_principal = VerifiedOidcPrincipal(
        issuer=issuer,
        subject=subject,
        audience=audience,
        tenant_id=tenant_id,
        roles=roles,
        key_id=kid,
        token_sha256=hashlib.sha256(token.encode("ascii")).hexdigest(),
        verified_at=now,
    )
    return VerifiedOidcPrincipal(
        **{
            **unsigned_principal.__dict__,
            "verification_receipt": _receipt(verification_receipt_secret, unsigned_principal),
        }
    )


def _bind_verified_principal_to_rbac(
    principal: VerifiedOidcPrincipal,
    *,
    requested_tenant_id: str,
    route_scope: str,
    requested_role: str,
    policy_path: str,
    capability_secret: str,
    verification_receipt_secret: str,
) -> AuthorizedPrincipalContext:
    """Bind only verified identity fields to one exact local RBAC decision."""

    if principal.auth_source != AUTH_SOURCE:
        _fail("OIDC verified principal source is invalid")
    if not hmac.compare_digest(
        principal.verification_receipt,
        _receipt(verification_receipt_secret, principal),
    ):
        _fail("OIDC verified principal receipt is invalid")
    tenant_id = _public_identifier(requested_tenant_id, label="requested_tenant_id")
    role = _public_identifier(requested_role, label="requested_role")
    if tenant_id != principal.tenant_id or role not in principal.roles:
        _fail("OIDC principal tenant or role binding is invalid")
    try:
        decision = evaluate_rbac_route(policy_path, route_scope, role)
    except RbacPolicyError as exc:
        raise OfflineOidcVerificationError("OIDC RBAC route policy is invalid") from exc
    if not decision.allowed or not decision.required_permission:
        _fail("OIDC RBAC permission was not granted")
    return issue_authorized_principal_context(
        subject=principal.subject,
        tenant_id=principal.tenant_id,
        roles=principal.roles,
        auth_source=AUTH_SOURCE,
        route_scope=route_scope,
        granted_role=decision.role,
        granted_permission=decision.required_permission,
        capability_secret=capability_secret,
    )


def verify_and_bind_offline_oidc_token(
    token: str,
    *,
    local_jwks: Mapping[str, Any],
    expected_issuer: str,
    expected_audience: str,
    now: int,
    requested_tenant_id: str,
    route_scope: str,
    requested_role: str,
    policy_path: str,
    capability_secret: str,
    verification_receipt_secret: str,
    clock_skew_seconds: int = DEFAULT_CLOCK_SKEW_SECONDS,
) -> AuthorizedPrincipalContext:
    """Execute the closed verify-to-RBAC chain without an unverified gap."""

    principal = verify_offline_oidc_token(
        token,
        local_jwks=local_jwks,
        expected_issuer=expected_issuer,
        expected_audience=expected_audience,
        now=now,
        verification_receipt_secret=verification_receipt_secret,
        clock_skew_seconds=clock_skew_seconds,
    )
    return _bind_verified_principal_to_rbac(
        principal,
        requested_tenant_id=requested_tenant_id,
        route_scope=route_scope,
        requested_role=requested_role,
        policy_path=policy_path,
        capability_secret=capability_secret,
        verification_receipt_secret=verification_receipt_secret,
    )
