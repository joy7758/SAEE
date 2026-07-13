# SAEE Auth/OIDC/RBAC Fixture Dry Run

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
