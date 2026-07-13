# SAEE Public Claim Lint v0.1

public_claim_lint_v0_1: true
status: local_public_claim_guard_available
scope: public_and_agent_readable_claim_surfaces
blockers_closed_by_lint: 0

## Purpose

Public Claim Lint v0.1 scans selected public and agent-readable SAEE surfaces
for forbidden positive commercial claims. It is designed to prevent local demo,
internal validation, strategy-intake, or recommendation-material progress from
being described as production readiness, customer validation, product launch,
external validation, public SDK release, or private core exposure.

This is a guardrail for commercial-readiness language. It does not make SAEE
production-ready, customer-validated, externally validated, launched, or ready
for public SDK release.

## Scan Scope

The default scan covers:

- top-level status surfaces: `README.md`, `PROJECT_STATUS.md`, `ROADMAP.md`,
  `CHANGELOG.md`, `agent-readable.md`, `agent-index.json`, and `llms.txt`;
- static landing and assistant-facing pages;
- core recommendation materials;
- semantic anchor and semantic dominance materials;
- selected commercial readiness status reports.

The scan is intentionally curated. It avoids scripts and fixture files that
must contain forbidden example strings for tests.

## Checked Claim Classes

The lint checks for positive statements or machine-readable flags implying:

- production readiness;
- customer validation;
- product launch;
- private core exposure or export;
- external validation claim;
- public SDK release;
- customer contact;
- wrong-category claims such as production monitoring or full quant platform
  positioning.

## Boundary

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- customer_contacted: false
- customer_validated: false
- product_launched: false
- production_ready: false
- private_core_exposed: false
- external_validation_claim: false
- public_sdk_released: false
- blockers_closed_by_lint: 0

## Commands

```bash
python3 scripts/saee_public_claim_lint.py
python3 scripts/saee_public_claim_lint_smoke.py
make check-public-claim-lint
```

