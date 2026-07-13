#!/usr/bin/env python3
"""Generate local public-shell auth evidence.

This runner converts existing auth readiness, identity-provider configuration,
and RBAC-template checks into a partial production-auth evidence JSON file for
human review. It does not contact identity providers, fetch JWKS, validate
production tokens, enable production authentication, enforce RBAC, modify
backend behavior, modify API schema, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.auth_readiness import evaluate_auth_readiness
from saee_backend.services.identity_provider_readiness import (
    evaluate_identity_provider_readiness,
)
from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    FORBIDDEN_TRUE_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
    evaluate_production_auth_evidence,
)
from scripts.saee_auth_oidc_rbac_fixture_dry_run import (
    build_results as build_fixture_dry_run_results,
)
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"
OUTPUT_PATH = OUTPUT_DIR / "auth_evidence.local.json"
README_PATH = OUTPUT_DIR / "README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_local_auth_evidence() -> dict[str, Any]:
    local_auth = evaluate_auth_readiness(load_settings({}))
    preview_auth = evaluate_auth_readiness(
        load_settings(
            {
                "SAEE_ENV": "preview",
                "SAEE_REQUIRE_API_KEY": "true",
                "SAEE_API_KEY": "local-preview-key",
            }
        )
    )
    generate_template()
    idp_config = evaluate_identity_provider_readiness(
        load_settings(
            {
                "SAEE_PRODUCTION_OIDC_ISSUER": "https://idp.example.invalid/",
                "SAEE_PRODUCTION_OIDC_AUDIENCE": "saee-controlled-preview",
                "SAEE_PRODUCTION_OIDC_JWKS_URL": (
                    "https://idp.example.invalid/.well-known/jwks.json"
                ),
                "SAEE_PRODUCTION_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
            }
        )
    )

    require(
        local_auth["auth_readiness_type"] == "public_shell_auth_readiness",
        "wrong local auth readiness type",
    )
    require(local_auth["status"] == "hold", "default local auth must hold")
    require(
        local_auth["preview_auth_available"] is False,
        "default preview auth must remain false",
    )
    require(
        preview_auth["preview_auth_available"] is True,
        "preview API key auth should be available under controlled config",
    )
    require(
        preview_auth["production_auth_ready"] is False,
        "preview API key auth must not imply production auth",
    )
    require(
        idp_config["status"] == "pass",
        "local IdP configuration review packet should be complete",
    )
    require(
        idp_config["production_identity_provider_available"] is False,
        "IdP config readiness must not claim production IdP availability",
    )
    require(
        idp_config["oauth_oidc_available"] is False,
        "IdP config readiness must not claim OAuth/OIDC availability",
    )
    require(
        idp_config["rbac_available"] is False,
        "RBAC template readiness must not claim production RBAC",
    )
    require(
        idp_config["external_identity_provider_contacted"] is False,
        "runner must not contact an identity provider",
    )
    require(idp_config["jwks_fetched"] is False, "runner must not fetch JWKS")
    require(
        idp_config["tokens_validated"] is False,
        "runner must not validate production tokens",
    )
    require(idp_config["rbac_enforced"] is False, "runner must not enforce RBAC")
    return {
        "local_auth_readiness": local_auth,
        "preview_auth_readiness": preview_auth,
        "identity_provider_config_readiness": idp_config,
    }


def build_evidence() -> dict[str, Any]:
    local_results = run_local_auth_evidence()
    fixture_results = build_fixture_dry_run_results()

    evidence: dict[str, Any] = {
        "auth_evidence_type": "production_auth_evidence",
        "evidence_scope": "local_public_shell_auth_review_packet",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_auth_evidence_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_auth_helper": "saee_backend/services/auth_readiness.py",
        "source_identity_provider_helper": (
            "saee_backend/services/identity_provider_readiness.py"
        ),
        "source_rbac_template_generator": "scripts/generate_rbac_policy_template.py",
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
        "role_matrix_reviewed": True,
        "tenant_role_boundary_reviewed": True,
        "least_privilege_reviewed": False,
        "admin_recovery_policy_reviewed": False,
        "local_public_shell_results": {
            "local_auth_status": local_results["local_auth_readiness"]["status"],
            "auth_boundary_available": True,
            "preview_api_key_auth_available": local_results[
                "preview_auth_readiness"
            ]["preview_auth_available"],
            "identity_provider_config_status": local_results[
                "identity_provider_config_readiness"
            ]["status"],
            "oidc_configuration_present": local_results[
                "identity_provider_config_readiness"
            ]["oidc_configuration_present"],
            "rbac_policy_template_available": local_results[
                "identity_provider_config_readiness"
            ]["rbac_policy_file_exists"],
            "rbac_policy_parseable": local_results[
                "identity_provider_config_readiness"
            ]["rbac_policy_parseable"],
            "required_rbac_roles_present": local_results[
                "identity_provider_config_readiness"
            ]["required_rbac_roles_present"],
            "required_rbac_permissions_present": local_results[
                "identity_provider_config_readiness"
            ]["required_rbac_permissions_present"],
            "required_rbac_route_scopes_present": local_results[
                "identity_provider_config_readiness"
            ]["required_rbac_route_scopes_present"],
            "rbac_route_scope_matrix_parseable": local_results[
                "identity_provider_config_readiness"
            ]["rbac_route_scope_matrix_parseable"],
            "auth_oidc_rbac_fixture_dry_run_status": fixture_results["status"],
            "local_fixture_token_validation_test_recorded": fixture_results[
                "local_fixture_token_validation_test_recorded"
            ],
            "local_fixture_claims_mapping_reviewed": fixture_results[
                "local_fixture_claims_mapping_reviewed"
            ],
            "local_fixture_negative_auth_cases_rejected": fixture_results[
                "local_fixture_negative_auth_cases_rejected"
            ],
            "local_fixture_rbac_route_matrix_tested": fixture_results[
                "local_fixture_rbac_route_matrix_tested"
            ],
            "local_fixture_rbac_route_matrix_passed": fixture_results[
                "local_fixture_rbac_route_matrix_passed"
            ],
            "local_fixture_claim_cases_passed": fixture_results["counts"][
                "fixture_claim_cases_passed"
            ],
            "local_fixture_rbac_cases_passed": fixture_results["counts"][
                "fixture_rbac_cases_passed"
            ],
            "blockers_closed_by_fixture_dry_run": fixture_results[
                "blockers_closed_by_fixture_dry_run"
            ],
            "production_identity_provider_available": False,
            "oauth_oidc_available": False,
            "rbac_available": False,
            "production_auth_ready": False,
            "external_calls_made": False,
            "identity_provider_contacted": False,
            "jwks_fetched": False,
            "tokens_validated_in_production": False,
            "production_auth_enabled": False,
            "rbac_enforced_in_production": False,
        },
        "limitations": [
            "No production identity provider has been selected.",
            "No identity-provider admin owner has been named for production.",
            "No issuer, audience, or JWKS rotation policy has been verified.",
            "No OAuth/OIDC flow has been approved.",
            "No production token validation test has been recorded.",
            "Local fixture-only OIDC/RBAC dry-run checks pass, but they are not production token validation or production RBAC approval.",
            "No claims mapping, session-expiry policy, or auth failure handling has been approved.",
            "The RBAC role matrix and tenant-role boundary are locally reviewable, but no RBAC policy is approved or enforced.",
            "No least-privilege review or admin recovery policy is complete.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    missing_expected = [
        key
        for key in AUTH_IDP_KEYS + OAUTH_OIDC_KEYS + RBAC_KEYS + FORBIDDEN_TRUE_KEYS
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Auth Evidence

Status: local public-shell auth review evidence, not production auth readiness.

This directory contains a generated local evidence JSON file for future
identity-provider, OAuth/OIDC, and RBAC production-auth review. It records only
what the local runner can prove from existing public-shell readiness materials.

It does not select or contact an identity provider, fetch JWKS, validate
production tokens, approve OAuth/OIDC flow, approve production RBAC, enforce
RBAC, enable production authentication, contact customers, modify runtime
behavior, modify backend behavior, modify API schema, or expose private core.

Primary file:

```text
auth_evidence.local.json
production_auth_evidence_path.local.json
production_auth_evidence_path_report.md
production_identity_provider_decision_packet.local.json
production_identity_provider_decision_packet.md
production_identity_provider_decision_input.template.json
production_identity_provider_decision_packet_boundary_audit.md
production_identity_provider_approval_input_validation.local.json
production_identity_provider_approval_input_validation.md
rbac_approval_input_validation.local.json
rbac_approval_input_validation.md
```

Generate it with:

```bash
python3 scripts/saee_auth_evidence_runner.py
python3 scripts/saee_production_auth_evidence_path.py
python3 scripts/saee_production_identity_provider_decision_packet.py
python3 scripts/saee_production_identity_provider_approval_input_validator.py
python3 scripts/saee_oauth_oidc_approval_input_validator.py
python3 scripts/saee_rbac_approval_input_validator.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_auth_review_packet
production_auth_evidence_path_available: true
production_auth_evidence_path_status: local_fixture_only_path_proof
production_auth_evidence_path_type: local_fixture_only_production_auth_evidence_path
production_auth_evidence_path_fixture_only: true
production_auth_evidence_path_real_identity_provider_selected: false
production_auth_evidence_path_real_oauth_oidc_flow_approved: false
production_auth_evidence_path_real_rbac_policy_approved: false
production_auth_evidence_path_real_production_tokens_validated: false
production_auth_evidence_path_blocker_path_proven: true
production_auth_evidence_path_auth_identity_provider_path_available: true
production_auth_evidence_path_auth_oauth_oidc_path_available: true
production_auth_evidence_path_auth_rbac_path_available: true
production_auth_evidence_path_auth_ready_path_available: true
production_auth_evidence_path_target_blockers_satisfied_count: 3
production_auth_evidence_path_production_blocker_count: 21
production_auth_evidence_path_closes_blockers: false
preview_api_key_auth_available: true
rbac_policy_template_available: true
role_matrix_reviewed: true
tenant_role_boundary_reviewed: true
production_identity_provider_selected: false
oauth_oidc_flow_approved: false
token_validation_test_recorded: false
rbac_policy_approved: false
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
```

The production identity-provider decision packet is a focused human-review
surface for the `production_identity_provider` blocker. It maps the identity
provider fields that would later be required by Phase 1 identity/tenant
evidence, but it does not select or contact an identity provider, fetch JWKS,
validate production tokens, enable production authentication, close blockers,
or claim production readiness.

The production-auth evidence path is a fixture-only path proof. It proves that
complete production identity-provider, OAuth/OIDC, and RBAC evidence can flow
through the existing production-auth evidence readiness and commercial go/no-go
checks. It does not select or contact an identity provider, fetch JWKS,
validate production tokens, enable production authentication, enforce
production RBAC, close blockers by itself, launch product, contact customers,
or claim production readiness.

The production identity-provider approval input validator checks human-filled
identity-provider decision input before evidence-builder use. It writes
`production_identity_provider_approval_input_validation.local.json` and
`production_identity_provider_approval_input_validation.md`, remains `hold` by
default, and closes zero blockers.

```yaml
production_identity_provider_approval_input_validator_status: hold
production_identity_provider_approval_input_validator_builder_ready: false
production_identity_provider_approval_input_validator_closes_blockers: 0
```

The OAuth/OIDC approval input validator checks the five OAuth/OIDC evidence
fields in the Phase 1 identity/tenant evidence template. It writes
`phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/oauth_oidc_approval_input_validation.local.json`,
remains `hold` by default, and does not validate production tokens or enable
production auth.

```yaml
oauth_oidc_approval_input_validator_status: hold
oauth_oidc_approval_input_validator_builder_ready: false
oauth_oidc_approval_input_validator_closes_blockers: 0
```

The RBAC approval input validator checks the five RBAC evidence fields in the
Phase 1 identity/tenant evidence template. It writes
`phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_validation.local.json`,
remains `hold` by default, and does not enforce production RBAC or enable
production auth.

```yaml
rbac_approval_input_validator_status: hold
rbac_approval_input_validator_builder_ready: false
rbac_approval_input_validator_closes_blockers: 0
```
""",
        encoding="utf-8",
    )


def write_outputs() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readme()
    return evidence


def main() -> None:
    write_outputs()
    readiness = evaluate_production_auth_evidence(
        load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    require(readiness["status"] == "hold", "partial local auth evidence must hold")
    require(
        readiness["production_auth_ready"] is False,
        "partial local auth evidence must not claim production auth",
    )
    print(
        "SAEE_AUTH_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH.relative_to(ROOT)} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_auth_ready=false"
    )


if __name__ == "__main__":
    main()
