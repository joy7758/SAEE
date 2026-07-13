#!/usr/bin/env python3
"""Run local fixture-only OIDC claims and RBAC dry-run checks.

This script exercises deterministic token-like fixtures and the local RBAC
policy template so production-auth review has a concrete test surface. It does
not contact an identity provider, fetch JWKS, validate signed production
tokens, enable production authentication, enforce production RBAC, modify API
schema, modify backend behavior, or claim production readiness.
"""

from __future__ import annotations

import base64
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rbac_policy import evaluate_rbac_route
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run"
RESULTS_PATH = OUTPUT_DIR / "auth_oidc_rbac_fixture_dry_run.local.json"
REPORT_PATH = OUTPUT_DIR / "auth_oidc_rbac_fixture_dry_run.md"
README_PATH = OUTPUT_DIR / "README.md"

EXPECTED_ISSUER = "https://idp.example.invalid/"
EXPECTED_AUDIENCE = "saee-controlled-preview"
FIXTURE_NOW = 1_893_456_000
REQUIRED_CLAIMS = (
    "iss",
    "sub",
    "aud",
    "exp",
    "iat",
    "tenant_id",
    "roles",
)
OPTIONAL_CLAIMS = ("nbf", "jti")
FORBIDDEN_IDENTITY_CLAIMS = ("email", "email_verified", "phone", "name", "address")
KNOWN_ROLES = (
    "owner",
    "admin",
    "evaluator_operator",
    "viewer",
    "support_operator",
)
FORBIDDEN_TRUE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "customer_contacted",
    "identity_provider_contacted",
    "jwks_fetched",
    "tokens_validated_in_production",
    "production_auth_enabled",
    "rbac_enforced_in_production",
    "production_identity_provider_available",
    "oauth_oidc_available",
    "rbac_available",
    "production_auth_ready",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _b64url_json(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_b64url_json(value: str) -> dict[str, Any]:
    padding = "=" * (-len(value) % 4)
    decoded = base64.urlsafe_b64decode((value + padding).encode("ascii"))
    data = json.loads(decoded.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("fixture segment must decode to an object")
    return data


def _fixture_token(claims: dict[str, Any]) -> str:
    header = {"alg": "none", "typ": "JWT", "fixture_only": True}
    return ".".join([_b64url_json(header), _b64url_json(claims), "fixture"])


def _base_claims() -> dict[str, Any]:
    return {
        "iss": EXPECTED_ISSUER,
        "sub": "fixture-user-001",
        "aud": EXPECTED_AUDIENCE,
        "exp": 4_102_444_800,
        "iat": FIXTURE_NOW - 600,
        "tenant_id": "tenant_alpha",
        "roles": ["evaluator_operator"],
    }


def _claim_fixtures() -> list[dict[str, Any]]:
    valid = _base_claims()
    missing_tenant = dict(valid)
    missing_tenant.pop("tenant_id")
    wrong_audience = dict(valid, aud="wrong-audience")
    expired = dict(valid, exp=1_000)
    missing_roles = dict(valid)
    missing_roles.pop("roles")
    return [
        {
            "case_id": "OIDC-FIX-001",
            "description": "valid local fixture claims",
            "token": _fixture_token(valid),
            "expected_accept": True,
        },
        {
            "case_id": "OIDC-FIX-002",
            "description": "missing tenant_id claim",
            "token": _fixture_token(missing_tenant),
            "expected_accept": False,
        },
        {
            "case_id": "OIDC-FIX-003",
            "description": "wrong audience claim",
            "token": _fixture_token(wrong_audience),
            "expected_accept": False,
        },
        {
            "case_id": "OIDC-FIX-004",
            "description": "expired fixture token",
            "token": _fixture_token(expired),
            "expected_accept": False,
        },
        {
            "case_id": "OIDC-FIX-005",
            "description": "missing roles claim",
            "token": _fixture_token(missing_roles),
            "expected_accept": False,
        },
    ]


def _evaluate_fixture_claims(token: str) -> tuple[bool, list[str], dict[str, Any]]:
    problems: list[str] = []
    parts = token.split(".")
    if len(parts) != 3:
        return False, ["wrong_segment_count"], {}
    try:
        header = _decode_b64url_json(parts[0])
        claims = _decode_b64url_json(parts[1])
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return False, [f"decode_failed:{exc.__class__.__name__}"], {}

    if header.get("fixture_only") is not True:
        problems.append("header_not_fixture_only")
    missing = [claim for claim in REQUIRED_CLAIMS if claim not in claims]
    problems.extend(f"missing_claim:{claim}" for claim in missing)
    if claims.get("iss") != EXPECTED_ISSUER:
        problems.append("issuer_mismatch")
    if claims.get("aud") != EXPECTED_AUDIENCE:
        problems.append("audience_mismatch")
    exp = claims.get("exp")
    if not isinstance(exp, int) or exp <= FIXTURE_NOW:
        problems.append("expired_or_invalid_exp")
    roles = claims.get("roles")
    if not isinstance(roles, list) or not roles:
        problems.append("roles_missing_or_empty")
    elif not all(str(role) in KNOWN_ROLES for role in roles):
        problems.append("unknown_role")
    if not isinstance(claims.get("tenant_id"), str) or not claims.get("tenant_id"):
        problems.append("tenant_id_missing_or_empty")
    if any(claim in claims for claim in FORBIDDEN_IDENTITY_CLAIMS):
        problems.append("personal_identity_claim_forbidden")
    return not problems, problems, claims


def _run_claim_checks() -> list[dict[str, Any]]:
    cases = []
    for item in _claim_fixtures():
        accepted, problems, claims = _evaluate_fixture_claims(str(item["token"]))
        expected_accept = bool(item["expected_accept"])
        cases.append(
            {
                "case_id": item["case_id"],
                "description": item["description"],
                "expected_accept": expected_accept,
                "actual_accept": accepted,
                "passed": accepted == expected_accept,
                "problems": problems,
                "claim_keys_seen": sorted(claims.keys()),
            }
        )
    return cases


def _rbac_cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "RBAC-FIX-001",
            "route": "GET /operations/telemetry",
            "role": "owner",
            "expected_allowed": True,
        },
        {
            "case_id": "RBAC-FIX-002",
            "route": "GET /operations/alerts",
            "role": "support_operator",
            "expected_allowed": True,
        },
        {
            "case_id": "RBAC-FIX-003",
            "route": "POST /experiment/run",
            "role": "evaluator_operator",
            "expected_allowed": True,
        },
        {
            "case_id": "RBAC-FIX-004",
            "route": "POST /experiment/create",
            "role": "viewer",
            "expected_allowed": False,
        },
        {
            "case_id": "RBAC-FIX-005",
            "route": "POST /experiment/run",
            "role": "support_operator",
            "expected_allowed": False,
        },
        {
            "case_id": "RBAC-FIX-006",
            "route": "GET /health",
            "role": "",
            "expected_allowed": False,
        },
    ]


def _run_rbac_checks() -> list[dict[str, Any]]:
    generate_template()
    cases = []
    for item in _rbac_cases():
        decision = evaluate_rbac_route(
            str(TEMPLATE_PATH),
            str(item["route"]),
            str(item["role"]),
        )
        expected_allowed = bool(item["expected_allowed"])
        cases.append(
            {
                "case_id": item["case_id"],
                "route": decision.route,
                "role": decision.role,
                "expected_allowed": expected_allowed,
                "actual_allowed": decision.allowed,
                "passed": decision.allowed == expected_allowed,
                "required_permission": decision.required_permission,
                "allowed_roles": list(decision.allowed_roles),
                "reason": decision.reason,
            }
        )
    return cases


def build_results() -> dict[str, Any]:
    claim_cases = _run_claim_checks()
    rbac_cases = _run_rbac_checks()
    claim_passed = sum(1 for case in claim_cases if case["passed"])
    rbac_passed = sum(1 for case in rbac_cases if case["passed"])
    all_passed = claim_passed == len(claim_cases) and rbac_passed == len(rbac_cases)
    negative_claims_rejected = all(
        (case["expected_accept"] or not case["actual_accept"])
        for case in claim_cases
    )
    status = "pass" if all_passed and negative_claims_rejected else "hold"

    results: dict[str, Any] = {
        "auth_oidc_rbac_fixture_dry_run_v0_1": True,
        "fixture_dry_run_type": "local_auth_oidc_rbac_fixture_dry_run",
        "status": status,
        "evidence_scope": "local_fixture_only_no_external_idp",
        "generated_by": "scripts/saee_auth_oidc_rbac_fixture_dry_run.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "expected_issuer": EXPECTED_ISSUER,
        "expected_audience": EXPECTED_AUDIENCE,
        "required_claims": list(REQUIRED_CLAIMS),
        "optional_claims": list(OPTIONAL_CLAIMS),
        "forbidden_identity_claims": list(FORBIDDEN_IDENTITY_CLAIMS),
        "known_roles": list(KNOWN_ROLES),
        "fixture_claim_cases": claim_cases,
        "fixture_rbac_cases": rbac_cases,
        "local_fixture_token_validation_test_recorded": True,
        "local_fixture_claims_mapping_reviewed": True,
        "local_fixture_negative_auth_cases_rejected": negative_claims_rejected,
        "local_fixture_rbac_route_matrix_tested": True,
        "local_fixture_rbac_route_matrix_passed": rbac_passed == len(rbac_cases),
        "counts": {
            "fixture_claim_cases": len(claim_cases),
            "fixture_claim_cases_passed": claim_passed,
            "fixture_rbac_cases": len(rbac_cases),
            "fixture_rbac_cases_passed": rbac_passed,
        },
        "production_identity_provider_selected": False,
        "identity_provider_admin_owner_named": False,
        "oidc_issuer_verified": False,
        "oidc_audience_approved": False,
        "jwks_rotation_policy_reviewed": False,
        "oauth_oidc_flow_approved": False,
        "token_validation_test_recorded": False,
        "claims_mapping_reviewed": False,
        "session_expiry_policy_approved": False,
        "auth_failure_handling_reviewed": False,
        "rbac_policy_approved": False,
        "least_privilege_reviewed": False,
        "admin_recovery_policy_reviewed": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated_in_production": False,
        "production_auth_enabled": False,
        "rbac_enforced_in_production": False,
        "blockers_closed_by_fixture_dry_run": 0,
        "next_action": (
            "Use these fixture results as local review support only; production "
            "auth blockers still require a real IdP, approved OAuth/OIDC flow, "
            "signed-token validation, and independently reviewed RBAC policy."
        ),
    }
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if results.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))
    return results


def _write_report(results: dict[str, Any]) -> None:
    claim_rows = "\n".join(
        "| {case_id} | {description} | {expected_accept} | {actual_accept} | {passed} |".format(
            **case
        )
        for case in results["fixture_claim_cases"]
    )
    rbac_rows = "\n".join(
        "| {case_id} | {route} | {role} | {expected_allowed} | {actual_allowed} | {passed} |".format(
            **case
        )
        for case in results["fixture_rbac_cases"]
    )
    REPORT_PATH.write_text(
        f"""# SAEE Auth/OIDC/RBAC Fixture Dry Run v0.1

Status: local fixture dry-run only; production auth remains unavailable.

## Purpose

This dry-run records deterministic local checks for token-like OIDC claim
fixtures, negative auth cases, and the local RBAC route matrix. It is meant to
make future production-auth review more concrete without contacting an identity
provider or changing product behavior.

## What Was Checked

- Required claims: `{", ".join(REQUIRED_CLAIMS)}`
- Expected issuer: `{EXPECTED_ISSUER}`
- Expected audience: `{EXPECTED_AUDIENCE}`
- Local RBAC template: `phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json`
- Negative fixture cases for missing tenant ID, wrong audience, expiry, and missing roles.

## Fixture Claim Cases

| Case | Description | Expected Accept | Actual Accept | Passed |
| --- | --- | --- | --- | --- |
{claim_rows}

## RBAC Route Cases

| Case | Route | Role | Expected Allowed | Actual Allowed | Passed |
| --- | --- | --- | --- | --- | --- |
{rbac_rows}

## Boundary

```yaml
auth_oidc_rbac_fixture_dry_run_v0_1: true
evidence_scope: local_fixture_only_no_external_idp
local_fixture_token_validation_test_recorded: true
local_fixture_claims_mapping_reviewed: true
local_fixture_rbac_route_matrix_tested: true
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
identity_provider_contacted: false
jwks_fetched: false
tokens_validated_in_production: false
production_auth_enabled: false
rbac_enforced_in_production: false
blockers_closed_by_fixture_dry_run: 0
```

This dry-run does not validate signed production tokens and does not close the
production identity-provider, OAuth/OIDC, or RBAC blockers.
""",
        encoding="utf-8",
    )


def _write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Auth/OIDC/RBAC Fixture Dry Run

Status: local fixture-only evidence support, not production authentication.

This directory contains deterministic local dry-run output for OIDC-like claim
fixtures and RBAC route decisions. It is useful for human review of the future
production-auth implementation path.

Primary files:

- `auth_oidc_rbac_fixture_dry_run.local.json`
- `auth_oidc_rbac_fixture_dry_run.md`

Generate them with:

```bash
python3 scripts/saee_auth_oidc_rbac_fixture_dry_run.py
```

Boundary:

- No identity provider contacted.
- No JWKS fetched.
- No signed production token validated.
- No production authentication enabled.
- No production RBAC enforced.
- No backend route behavior changed.
- No API schema changed.
- No customer contacted.
- No production readiness claimed.
- No private core exposed.
""",
        encoding="utf-8",
    )


def write_outputs() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = build_results()
    RESULTS_PATH.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(results)
    _write_readme()
    return results


def main() -> None:
    results = write_outputs()
    require(results["status"] == "pass", "fixture dry-run should pass locally")
    require(
        results["production_auth_ready"] is False,
        "fixture dry-run must not claim production auth",
    )
    print(
        "SAEE_AUTH_OIDC_RBAC_FIXTURE_DRY_RUN: PASS "
        f"path={RESULTS_PATH.relative_to(ROOT)} "
        "local_fixture_only=true production_auth_ready=false "
        "blockers_closed_by_fixture_dry_run=0"
    )


if __name__ == "__main__":
    main()
