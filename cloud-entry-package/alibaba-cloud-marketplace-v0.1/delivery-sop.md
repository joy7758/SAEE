# SAEE Alibaba Cloud Marketplace Delivery SOP v0.1

Status: local draft; no customer order or production delivery has occurred.

## Bounded delivery flow

1. Confirm the order scope is exactly one Agent workflow and one scenario.
2. Require explicit authority for every submitted execution record and evidence
   reference.
3. Reject secrets, credentials, unrestricted personal data, unknown executable
   repositories, and requests to expand permissions.
4. Normalize the accepted input into the canonical Commercial Assessment
   Service request contract.
5. Run only the two public read-only assessment operations in an isolated
   environment.
6. Generate JSON and human-readable reports with input digests, evidence gaps,
   limitations, and one bounded recommendation.
7. Perform a human quality and boundary review before delivery.
8. Deliver through the Marketplace service flow and retain only the evidence
   authorized by the contract and retention policy.
9. If validation, privacy, scope, or integrity checks fail, stop delivery,
   preserve the failure receipt, and initiate the approved refund or rework
   path.

## Implemented local bridge

The bounded prepare/finalize bridge is implemented at
`saee_backend/services/marketplace_assessment_delivery.py`. It accepts only the
closed normalized intake contract, delegates to `saee.evaluate_agent_run`,
binds JSON and Chinese Markdown artifacts by SHA-256, requires human boundary
review, and deletes the local intake source only through an explicit finalize
command constrained to the declared intake root.

This implementation makes a local delivery candidate reproducible. It does
not mean a Marketplace order has been delivered or accepted.

## Acceptance conditions

- The report binds to the accepted input digest and scenario.
- Every finding references evidence or explicitly states insufficient evidence.
- The recommendation is one of `CONTINUE`, `REPLAN`,
  `HUMAN_REVIEW_REQUIRED`, or `STOP`.
- The report states that assessment is not certification, deployment approval,
  or an automated decision.

## Open owner decisions

- Tax rate and invoice presentation.
- Delivery business days.
- Support hours and response target.
- Acceptance window.
- Refund and rework terms.
- Data retention and deletion period for real customer delivery.

Until those decisions are approved, this SOP is not a customer-facing service
commitment.

The proposed owner-directed launch price is RMB 999 per assessment for the
bounded one-workflow, one-scenario initial SKU. It remains a local form-entry
decision until the Marketplace sales-information page is saved; it is not yet
a published price or completed order.
