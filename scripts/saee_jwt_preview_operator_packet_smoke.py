#!/usr/bin/env python3
"""Smoke check for the SAEE JWT preview operator packet."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.jwt_preview_auth import validate_authorization_header


ISSUER = "https://preview-idp.example.invalid/"
AUDIENCE = "saee-controlled-preview"
SECRET = "operator-packet-smoke-secret"
TENANT_ID = "tenant-alpha"
CLI = ROOT / "scripts/saee_jwt_preview_token.py"
DOC = ROOT / "phase_b_product/commercial_readiness/JWT_PREVIEW_OPERATOR_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_JWT_PREVIEW_OPERATOR_PACKET_RECOMMENDATION_GATE.md"


@contextmanager
def patched_env(values: dict[str, str]):
    previous = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_JWT_PREVIEW_OPERATOR_PACKET_SMOKE: FAIL: " + message)


def run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    merged = dict(os.environ)
    merged.update(env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(ROOT),
        env=merged,
        check=False,
        text=True,
        capture_output=True,
    )


def main() -> None:
    require(CLI.is_file(), "token CLI missing")
    require(DOC.is_file(), "operator packet doc missing")
    require(GATE.is_file(), "operator packet gate missing")

    env = {
        "SAEE_SYNTHETIC_DATA_ONLY": "true",
        "SAEE_REQUIRE_JWT_PREVIEW_AUTH": "true",
        "SAEE_PREVIEW_JWT_ISSUER": ISSUER,
        "SAEE_PREVIEW_JWT_AUDIENCE": AUDIENCE,
        "SAEE_PREVIEW_JWT_HS256_SECRET": SECRET,
        "SAEE_REQUIRE_TENANT_ID": "true",
        "SAEE_ALLOWED_TENANT_IDS": TENANT_ID,
        "SAEE_REQUIRE_RBAC_ROLE": "true",
        "SAEE_RBAC_POLICY_PATH": "phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json",
    }
    args = [
        "--subject",
        "preview-user-001",
        "--tenant-id",
        TENANT_ID,
        "--roles",
        "evaluator_operator,viewer",
        "--ttl-seconds",
        "900",
        "--json",
    ]
    completed = run_cli(args, env)
    require(completed.returncode == 0, completed.stderr.strip() or "CLI failed")
    require(SECRET not in completed.stdout, "secret leaked in CLI stdout")
    payload = json.loads(completed.stdout)
    token = payload["token"]
    require(payload["claims"]["tenant_id"] == TENANT_ID, "tenant claim mismatch")
    require(payload["claims"]["roles"] == ["evaluator_operator", "viewer"], "roles mismatch")
    for flag in [
        "external_identity_provider_contacted",
        "jwks_fetched",
        "tokens_validated_in_production",
        "jwt_preview_production_oidc",
        "production_auth_ready",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(payload["boundary"][flag] is False, f"boundary {flag} must be false")

    with patched_env(env):
        settings = load_settings()
        claims = validate_authorization_header("Bearer " + token, settings)
        require(claims.subject == "preview-user-001", "generated token did not validate")
        require("evaluator_operator" in claims.roles, "evaluator role missing")

    missing_secret = dict(env)
    missing_secret.pop("SAEE_PREVIEW_JWT_HS256_SECRET")
    failed = run_cli(args, missing_secret)
    require(failed.returncode != 0, "CLI should fail without secret")
    require("SAEE_PREVIEW_JWT_HS256_SECRET is required" in failed.stderr, "missing secret error absent")

    doc = DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for token_text in [
        "jwt_preview_operator_packet_v0_1: true",
        "controlled_preview_token_generator_available: true",
        "production_auth_ready: false",
        "tokens_validated_in_production: false",
        "private_core_exposed: false",
        "blockers_closed_by_operator_packet: 0",
    ]:
        require(token_text in doc, "doc missing token: " + token_text)
    for token_text in [
        "answer: conditional",
        "recommend_for_controlled_preview_token_generation: true",
        "recommend_for_production_auth: false",
        "production_auth_ready: false",
    ]:
        require(token_text in gate, "gate missing token: " + token_text)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("jwt_preview_operator_packet_v0_1", {})
    expected = {
        "status": "controlled_preview_token_generator_available",
        "jwt_preview_operator_packet_v0_1": True,
        "controlled_preview_token_generator_available": True,
        "external_identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated_in_production": False,
        "jwt_preview_production_oidc": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "blockers_closed_by_operator_packet": 0,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_JWT_PREVIEW_OPERATOR_PACKET_SMOKE: PASS "
        "token_generated=true production_auth_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
