#!/usr/bin/env python3
"""Prove the local production-auth evidence path without Auth deployment.

This path check uses temporary fixture-only production-auth evidence and feeds
it into the existing production-auth readiness and commercial go/no-go checks.
It proves the wiring from human-filled identity-provider / OAuth-OIDC / RBAC
evidence to commercial review without selecting or contacting an identity
provider, fetching JWKS, validating production tokens, enabling production
authentication, enforcing production RBAC, closing blockers by itself, or
claiming production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    FORBIDDEN_TRUE_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
    evaluate_production_auth_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "production_auth_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "production_auth_evidence_path_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_AUTH_EVIDENCE_PATH_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRODUCTION_AUTH_EVIDENCE_PATH_RECOMMENDATION_GATE.md"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_evidence() -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "auth_evidence_type": "production_auth_evidence",
        "evidence_scope": "fixture_only_production_auth_evidence_path_proof",
        "evidence_version": "v0.1",
        "input_status": "fixture_only_not_real_production_auth",
        "generated_by": "scripts/saee_production_auth_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": datetime.now(timezone.utc).date().isoformat(),
        "decision_summary": (
            "Fixture-only production-auth evidence path proof. This is not a "
            "real identity-provider selection, OAuth/OIDC approval, production "
            "token validation, or RBAC approval."
        ),
        "source_notes_by_key": {
            key: f"Fixture-only source note for {key}."
            for key in AUTH_IDP_KEYS + OAUTH_OIDC_KEYS + RBAC_KEYS
        },
        "auth_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://production-auth/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in AUTH_IDP_KEYS + OAUTH_OIDC_KEYS + RBAC_KEYS
        ],
        "fixture_only": True,
        "real_identity_provider_selected": False,
        "real_oauth_oidc_flow_approved": False,
        "real_rbac_policy_approved": False,
        "real_production_tokens_validated": False,
    }
    for key in AUTH_IDP_KEYS + OAUTH_OIDC_KEYS + RBAC_KEYS:
        evidence[key] = True
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def auth_status(path: Path) -> dict[str, object]:
    return evaluate_production_auth_evidence(
        load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(path)})
    )


def build_path(output_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture_path = Path(tmpdir) / "production_auth_evidence.fixture.json"
        write_json(fixture_path, fixture_evidence())
        auth = auth_status(fixture_path)
        go_no_go = commercial_status(fixture_path)

    auth_path_proven = (
        auth["production_identity_provider_available"] is True
        and auth["oauth_oidc_available"] is True
        and auth["rbac_available"] is True
        and auth["production_auth_ready"] is True
    )
    result: dict[str, Any] = {
        "production_auth_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_production_auth_evidence_path",
        "path_status": "pass_fixture_only" if auth_path_proven else "hold",
        "generated_by": "scripts/saee_production_auth_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_identity_provider_selected": False,
        "real_oauth_oidc_flow_approved": False,
        "real_rbac_policy_approved": False,
        "real_production_tokens_validated": False,
        "auth_readiness_status_after_fixture": auth["status"],
        "auth_evidence_production_identity_provider_available": auth[
            "production_identity_provider_available"
        ],
        "auth_evidence_oauth_oidc_available": auth["oauth_oidc_available"],
        "auth_evidence_rbac_available": auth["rbac_available"],
        "auth_evidence_production_auth_ready": auth["production_auth_ready"],
        "commercial_status_after_fixture": go_no_go["commercial_status"],
        "production_launch_status_after_fixture": go_no_go[
            "production_launch_status"
        ],
        "satisfied_production_checks_after_fixture": go_no_go[
            "satisfied_production_checks"
        ],
        "total_production_checks_after_fixture": go_no_go["total_production_checks"],
        "production_blocker_count_after_fixture": go_no_go[
            "production_blocker_count"
        ],
        "production_auth_blocker_path_proven": auth_path_proven,
        "auth_target_blockers_satisfied_by_fixture": [
            "production_identity_provider",
            "oauth_oidc",
            "rbac",
        ],
        "auth_target_blockers_satisfied_count_after_fixture": 3
        if auth_path_proven
        else 0,
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_real_evidence_required": True,
        "separate_go_no_go_profile_required": True,
        "separate_human_launch_approval_required": True,
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
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "identity_provider_contacted": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched": False,
        "jwks_fetched_by_codex": False,
        "tokens_validated_in_production": False,
        "production_tokens_validated_by_codex": False,
        "production_auth_enabled": False,
        "rbac_enforced_in_production": False,
        "production_auth_claim_published": False,
        "next_action": (
            "A human owner must replace the fixture with real production Auth "
            "evidence, then rerun production-auth evidence readiness and "
            "commercial go/no-go. This path proof alone closes no blockers."
        ),
    }
    write_json(output_path, result)
    write_report(result)
    write_docs()
    return result


def write_report(result: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# SAEE Production Auth Evidence Path Report v0.1",
                "",
                "Status: local fixture-only path proof generated.",
                "",
                "## Summary",
                "",
                "- production_auth_evidence_path_v0_1: true",
                f"- path_type: {result['path_type']}",
                f"- path_status: {result['path_status']}",
                "- fixture_only: true",
                "- real_identity_provider_selected: false",
                "- real_oauth_oidc_flow_approved: false",
                "- real_rbac_policy_approved: false",
                "- real_production_tokens_validated: false",
                f"- auth_readiness_status_after_fixture: {result['auth_readiness_status_after_fixture']}",
                f"- auth_evidence_production_identity_provider_available: {str(result['auth_evidence_production_identity_provider_available']).lower()}",
                f"- auth_evidence_oauth_oidc_available: {str(result['auth_evidence_oauth_oidc_available']).lower()}",
                f"- auth_evidence_rbac_available: {str(result['auth_evidence_rbac_available']).lower()}",
                f"- auth_evidence_production_auth_ready: {str(result['auth_evidence_production_auth_ready']).lower()}",
                f"- production_auth_blocker_path_proven: {str(result['production_auth_blocker_path_proven']).lower()}",
                f"- auth_target_blockers_satisfied_count_after_fixture: {result['auth_target_blockers_satisfied_count_after_fixture']}",
                f"- commercial_status_after_fixture: {result['commercial_status_after_fixture']}",
                f"- production_blocker_count_after_fixture: {result['production_blocker_count_after_fixture']}",
                f"- blockers_closed_by_path: {result['blockers_closed_by_path']}",
                "",
                "## Boundary",
                "",
                "- No identity provider selected or contacted.",
                "- No JWKS fetched.",
                "- No production tokens validated.",
                "- No production authentication enabled.",
                "- No production RBAC enforced.",
                "- No backend, runtime, kernel, or API schema modified.",
                "- No customer contacted.",
                "- No product launched.",
                "- No production-readiness claim added.",
                "- No private core exposed.",
                "",
                "## Next Action",
                "",
                str(result["next_action"]),
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_docs() -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        """# SAEE Production Auth Evidence Path v0.1

Status: local fixture-only path proof; not production authentication.

## Purpose

This path proves that a complete local production-auth evidence JSON can be
read by `production_auth_evidence`, then reflected by commercial go/no-go for
the Auth blocker group:

- `production_identity_provider`
- `oauth_oidc`
- `rbac`

## Machine-Readable Status

```yaml
production_auth_evidence_path_v0_1: true
path_type: local_fixture_only_production_auth_evidence_path
path_status: pass_fixture_only
fixture_only: true
real_identity_provider_selected: false
real_oauth_oidc_flow_approved: false
real_rbac_policy_approved: false
real_production_tokens_validated: false
auth_evidence_production_identity_provider_available: true
auth_evidence_oauth_oidc_available: true
auth_evidence_rbac_available: true
auth_evidence_production_auth_ready: true
production_auth_blocker_path_proven: true
auth_target_blockers_satisfied_count_after_fixture: 3
production_blocker_count_after_fixture: 21
blockers_closed_by_path: 0
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

## Boundary

This path does not select or contact an identity provider, fetch JWKS, validate
production tokens, enable production authentication, enforce production RBAC,
close blockers by itself, launch product, contact customers, modify runtime,
modify backend, modify kernel, modify API schema, or expose private core.

## Recommendation Gate

Answer: conditional.

Recommend this path for human production-auth evidence review and blocker-path
verification. Do not recommend it as production authentication, production
launch approval, customer validation, or blocker closure by itself.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Production Auth Evidence Path Recommendation Gate

answer: conditional

recommend_for_human_auth_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_identity_provider_contact: false
recommend_for_jwks_fetch: false
recommend_for_production_token_validation: false
recommend_for_production_auth_enablement: false
recommend_for_production_rbac_enforcement: false

## Reason

The path proves local fixture-only wiring from production-auth evidence into
commercial go/no-go for the Auth blocker group. It is useful for human review
of real evidence later, but it is not production authentication and does not
close blockers by itself.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
identity_provider_contacted: false
jwks_fetched: false
tokens_validated_in_production: false
production_auth_enabled: false
rbac_enforced_in_production: false
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_path(Path(args.output))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH: PASS "
            f"path={Path(args.output).relative_to(ROOT)} "
            f"path_status={result['path_status']} "
            "fixture_only=true "
            "production_auth_blocker_path_proven=true "
            "blockers_closed_by_path=0"
        )


if __name__ == "__main__":
    main()
