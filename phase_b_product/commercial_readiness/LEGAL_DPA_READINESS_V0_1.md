# SAEE Legal / DPA Readiness v0.1

Status: controlled-preview legal review readiness, not legal approval.

This file records the legal and DPA review packet for the SAEE public API
shell. It is a commercial-readiness surface for human review. It does not
publish legal terms, approve customer data processing, contact customers,
launch product, modify backend behavior, modify API schema, or expose private
core.

## Purpose

SAEE can be tried locally and prepared for controlled preview, but a
customer-facing commercial system needs legal review before it may process
customer data or make paid contractual commitments.

This readiness layer records:

- draft terms-of-service review packet;
- draft privacy notice review packet;
- DPA review checklist;
- explicit customer-data-processing hold state;
- production legal readiness non-claim.

## Current State

```text
legal_readiness_v0_1: true
legal_readiness_status: hold
terms_of_service_draft_available: true
terms_of_service_published: false
terms_legal_review_completed: false
privacy_notice_draft_available: true
privacy_notice_published: false
privacy_legal_review_completed: false
dpa_review_packet_available: true
data_processing_agreement_draft_available: true
data_processing_agreement_available: false
customer_contract_template_available: false
legal_approval_completed: false
customer_data_processing_ready: false
production_legal_ready: false
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
external_model_api_called: false
```

## Review Packet

The draft packet is limited to human review. It does not create public legal
terms.

Required human review items:

1. Confirm whether SAEE will process personal data during controlled preview.
2. Approve a customer-facing terms-of-service document before any paid or
   customer-facing preview.
3. Approve a privacy notice before customer data is collected.
4. Approve a DPA before any customer uploads, customer logs, or customer
   production data are processed.
5. Confirm data retention, backup, restore, support, and vulnerability
   response language before customer use.

## Explicit Non-Claims

This readiness layer does not provide:

- legal advice;
- completed privacy legal review;
- approved terms of service;
- published privacy notice;
- available DPA;
- customer contract template;
- customer data processing approval;
- production legal readiness;
- customer validation;
- product launch;
- public SDK release.

## Boundary

SAEE remains local MVP / controlled-preview preparation only. Legal readiness
is `hold` until a qualified human/legal reviewer approves terms, privacy
notice, DPA, and customer-data-processing conditions.
