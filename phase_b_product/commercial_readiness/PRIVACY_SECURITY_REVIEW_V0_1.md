# SAEE Privacy / Security Review Readiness v0.1

Status: controlled-preview privacy and security review readiness draft.

SAEE Privacy / Security Review Readiness v0.1 documents the public-shell data
boundary, privacy assumptions, and security review gaps needed before customer
or production use. It is an agent-readable readiness layer for human review.

This is not a formal legal review, security certification, penetration test,
SOC 2 report, ISO 27001 certification, DPA, production security program,
customer data approval, customer validation, or production readiness claim.

## Scope

Included:

- public-shell data classification;
- public-shell data map;
- draft policy that personal data should not be submitted to the local MVP;
- secret-handling guidance for preview operators;
- third-party processor inventory for the current local shell;
- draft vulnerability disclosure policy and security intake contact boundary;
- explicit blockers for production privacy and security readiness.

Excluded:

- formal privacy or legal review;
- customer data processing terms;
- data processing agreement;
- penetration testing;
- full vulnerability disclosure or remediation program;
- SOC 2 / ISO 27001 / security certification;
- SIEM, compliance logging, or production security operations;
- external model API calls or external assistant testing.

## CLI

```bash
python3 scripts/saee_privacy_security_readiness.py
```

## Current State

```text
privacy_security_review_v0_1: true
privacy_security_review_status: hold
data_classification_available: true
public_shell_data_map_available: true
pii_policy_draft_available: true
personal_data_allowed: false
secret_handling_guidance_available: true
third_party_processor_inventory_available: true
legal_readiness_v0_1: true
legal_readiness_status: hold
terms_of_service_draft_available: true
terms_of_service_published: false
terms_legal_review_completed: false
privacy_notice_draft_available: true
privacy_notice_published: false
dpa_review_packet_available: true
data_processing_agreement_draft_available: true
customer_contract_template_available: false
legal_approval_completed: false
production_legal_ready: false
vulnerability_management_readiness_v0_1: true
vulnerability_management_readiness_status: hold
vulnerability_disclosure_policy_draft_available: true
security_contact_configured: false
vulnerability_intake_contact_configured: false
controlled_preview_security_contact_required: false
vulnerability_triage_runbook_available: true
external_model_api_called: false
external_ai_assistant_tested: false
formal_security_review_completed: false
privacy_legal_review_completed: false
data_processing_agreement_available: false
security_certification_available: false
soc2_available: false
iso27001_available: false
penetration_test_completed: false
vulnerability_remediation_sla_available: false
coordinated_disclosure_available: false
vulnerability_management_available: false
production_vulnerability_management_ready: false
compliance_logging_available: false
production_security_ready: false
customer_data_processing_ready: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
customer_contacted: false
```

## Public-Shell Data Map

```text
input: candidate agent/workflow/policy identifiers and opaque config strings or JSON.
input_boundary: no secrets, credentials, personal data, customer production data, or private core details.
processing: deterministic local stability, survival, failure-mode, and ranking evaluation.
stored_default: in-memory experiment summaries only.
stored_optional: local SQLite public-shell experiment summaries if explicitly configured.
request_audit_optional: metadata only; request and response bodies are not recorded.
external_processors: none in the current local shell.
```

## Operator Guidance

- Do not submit personal data, secrets, API keys, customer production traces, or
  proprietary source code as agent configuration.
- Use synthetic or sanitized candidate descriptions during local and controlled
  preview testing.
- Keep `SAEE_REQUEST_AUDIT_ENABLED` limited to metadata-only audit until a
  formal privacy review approves broader handling.
- Do not route request audit logs to external processors without separate
  human approval and a processor review.

## Production Blockers

- formal security review is not complete;
- legal/privacy review is not complete;
- DPA and customer data processing terms do not exist;
- penetration testing is not complete;
- vulnerability management is not production-ready;
- remediation SLA and coordinated disclosure are not available;
- SOC 2 / ISO 27001 / security certification is not available;
- compliance logging and SIEM integration are not available.

## Boundary

Privacy / Security Review Readiness v0.1 does not modify product behavior,
backend routes, API schema, runtime, kernel, scoring, selection, mutation,
lineage, private core, or landing page interaction. It does not contact
customers, call external model APIs, or claim production readiness.
