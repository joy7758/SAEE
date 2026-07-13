#!/usr/bin/env python3
"""Generate a local HS256 JWT for SAEE controlled-preview API use.

This CLI is for local controlled-preview operation only. It does not contact an
identity provider, fetch JWKS, validate production tokens, implement OAuth/OIDC,
or make SAEE production-auth ready.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.jwt_preview_auth import (
    JwtPreviewAuthError,
    sign_preview_jwt,
    validate_authorization_header,
)


DEFAULT_TTL_SECONDS = 3600


def _split_roles(value: str) -> list[str]:
    roles = [item.strip() for item in value.split(",") if item.strip()]
    if not roles:
        raise argparse.ArgumentTypeError("roles must contain at least one role")
    return roles


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a local SAEE controlled-preview HS256 JWT. "
            "This is not production OAuth/OIDC."
        )
    )
    parser.add_argument("--subject", required=True, help="JWT subject claim.")
    parser.add_argument("--tenant-id", required=True, help="Preview tenant_id claim.")
    parser.add_argument(
        "--roles",
        required=True,
        type=_split_roles,
        help="Comma-separated preview roles, for example evaluator_operator,viewer.",
    )
    parser.add_argument(
        "--issuer",
        default=None,
        help="JWT issuer. Defaults to SAEE_PREVIEW_JWT_ISSUER.",
    )
    parser.add_argument(
        "--audience",
        default=None,
        help="JWT audience. Defaults to SAEE_PREVIEW_JWT_AUDIENCE.",
    )
    parser.add_argument(
        "--ttl-seconds",
        type=_positive_int,
        default=DEFAULT_TTL_SECONDS,
        help=f"Token lifetime in seconds. Default: {DEFAULT_TTL_SECONDS}.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON with token, authorization header, claim summary, and boundary flags.",
    )
    return parser


def _configured_value(name: str, explicit: str | None) -> str:
    value = explicit if explicit is not None else os.environ.get(name, "")
    return value.strip()


def build_claims(args: argparse.Namespace, *, now: int | None = None) -> dict[str, Any]:
    current_time = int(time.time()) if now is None else now
    issuer = _configured_value("SAEE_PREVIEW_JWT_ISSUER", args.issuer)
    audience = _configured_value("SAEE_PREVIEW_JWT_AUDIENCE", args.audience)
    if not issuer:
        raise JwtPreviewAuthError("SAEE_PREVIEW_JWT_ISSUER is required or pass --issuer.")
    if not audience:
        raise JwtPreviewAuthError("SAEE_PREVIEW_JWT_AUDIENCE is required or pass --audience.")
    return {
        "iss": issuer,
        "sub": args.subject.strip(),
        "aud": audience,
        "exp": current_time + args.ttl_seconds,
        "iat": current_time,
        "tenant_id": args.tenant_id.strip(),
        "roles": list(args.roles),
    }


def generate_preview_token(args: argparse.Namespace) -> dict[str, Any]:
    secret = os.environ.get("SAEE_PREVIEW_JWT_HS256_SECRET", "").strip()
    if not secret:
        raise JwtPreviewAuthError("SAEE_PREVIEW_JWT_HS256_SECRET is required.")

    claims = build_claims(args)
    token = sign_preview_jwt(claims, secret)

    settings_source = dict(os.environ)
    settings_source.update(
        {
            "SAEE_REQUIRE_JWT_PREVIEW_AUTH": "true",
            "SAEE_PREVIEW_JWT_ISSUER": str(claims["iss"]),
            "SAEE_PREVIEW_JWT_AUDIENCE": str(claims["aud"]),
            "SAEE_PREVIEW_JWT_HS256_SECRET": secret,
        }
    )
    settings = load_settings(settings_source)
    validated = validate_authorization_header("Bearer " + token, settings)
    return {
        "token": token,
        "authorization_header": "Bearer " + token,
        "claims": {
            "iss": validated.issuer,
            "sub": validated.subject,
            "aud": validated.audience,
            "exp": validated.expires_at,
            "iat": validated.issued_at,
            "tenant_id": validated.tenant_id,
            "roles": list(validated.roles),
        },
        "boundary": {
            "token_type": "controlled_preview_hs256_jwt",
            "external_identity_provider_contacted": False,
            "jwks_fetched": False,
            "tokens_validated_in_production": False,
            "jwt_preview_production_oidc": False,
            "production_auth_ready": False,
            "production_ready": False,
            "customer_validated": False,
            "product_launched": False,
            "private_core_exposed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = generate_preview_token(args)
    except JwtPreviewAuthError as exc:
        print("SAEE_JWT_PREVIEW_TOKEN: ERROR: " + str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["token"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
