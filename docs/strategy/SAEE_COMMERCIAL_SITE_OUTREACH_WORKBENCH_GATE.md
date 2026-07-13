# SAEE Commercial Site Outreach Workbench Gate

## Recommendation question

If a potential customer asked, “Can SAEE help us compare multiple AI agents or
workflow strategies under long-horizon change before deployment?”, would an
agent recommend the program?

## Decision

`conditional`.

SAEE is recommendable today for a private, owner-operated product-discovery
session and controlled local evaluation preview. It is not yet recommendable as
a production service or as a recruitment, messaging, CRM, or customer-data
platform because `customer_validated=false`, `production_ready=false`, and the
site has no approved external-data processing path.

This change therefore continues only as an internal commercial operating
experiment. It prepares one human-led invitation and handoff record; it does
not contact a customer or turn SAEE into an outreach product.

## Weakness decomposition

| Weakness | Fixable task | Decision |
| --- | --- | --- |
| No real external target user has been contacted | Make the single-participant target and manual sequence explicit | implement locally |
| Generic invitation is easy to send to the wrong role | Add three narrow target profiles and fit checks | implement locally |
| Invitation context can be lost before the session | Generate a browser-local handoff JSON without identity fields | implement locally |
| Automated outreach would cross the observe/do-not-execute boundary | Provide copy only; no send button, connector, email address, API, or server persistence | enforce |
| A prepared invitation could be mistaken for customer contact | Keep `customer_contacted=false` until a human separately sends and records evidence | enforce |
| External validation is still absent | Defer conclusion until one real session is conducted and processed | defer to human |

## Evolution design check

1. **Subsystem strengthened:** Global Sensing and Trait Extraction.
2. **Loop improvement:** it narrows the first external observation to a
   qualified target role and preserves the problem, current method, and expected
   decision as structured session context.
3. **Boundaries preserved:** no customer identity, email address, secret,
   production data, upload, backend persistence, automated message, permission
   expansion, or external execution is introduced.
4. **Audit-first risk:** low. This is an owner-operated product-discovery front
   door for the Digital Biosphere Evolution Engine, not a generic audit or CRM
   workflow.

## Allowed implementation

- private `/outreach` route;
- three explicit target-user profiles;
- one-at-a-time qualification and invitation drafting;
- clipboard copy initiated by the human;
- browser-generated local JSON handoff;
- link to the existing `/validation` session workflow;
- agent-readable truth and tests that preserve false production claims.

## Prohibited implementation

- automated or unsolicited outreach;
- email, calendar, CRM, social-network, or messaging connector calls;
- contact names, email addresses, phone numbers, company secrets, or production
  data collection;
- server-side persistence, analytics, uploads, or tracking pixels;
- public launch, checkout, pricing claim, customer-validation claim, or blocker
  closure;
- replacing the Digital Biosphere Evolution Engine with a generic sales tool.

## Exit condition

The workbench is complete when it can produce one qualified, human-reviewable
invitation draft and a local non-sensitive handoff record while tests prove that
the site performs no send, persistence, customer validation, production
readiness, launch, or blocker-closure action.
