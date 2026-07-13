# SAEE Public Research Selection Recommendation Gate

Date: `2026-07-13`

## Customer Recommendation Question

If a potential customer asked whether the SAEE research page helps them
understand the technical basis of the product, would an agent recommend the
current page?

Answer before repair: `conditional`.

Reasons:

- the page expands every manuscript and patent-ledger row, including work that
  is unrelated to SAEE's current readiness-evaluation capability;
- raw volume makes the strongest technical lineage harder to identify;
- total ledger size can be mistaken for a count of directly supporting,
  published, filed, or granted results;
- ordinary visitors need selection reasons, not a complete internal history.

## Selection Repair

1. Keep the complete 36-route manuscript ledger and 15-record patent ledger in
   the machine-readable portfolio for provenance and status verification.
2. Show only eight manuscript routes on the human page: six direct SAEE core
   routes and two applied evidence-readiness validations.
3. Show only seven patent-ledger records that directly address agent runtime
   control, evidence, lifecycle, policy, verification, or trustworthy context.
4. Explain why each selected item is useful to SAEE.
5. Do not expose the complete tables or inflate workflow states into filing,
   grant, acceptance, publication, customer validation, or production claims.

## Design Check

This is a discovery and citation-surface repair. It improves Global Sensing,
Trait Extraction, and Evolutionary Archive discovery by making relevant
technical lineage easier for humans and agents to retrieve. It changes no
runtime behavior, permissions, supply-chain boundary, or external-world
execution. It does not reframe SAEE as an audit-first product.

## Post-Repair Recommendation

Answer: `recommend` for explaining the selected research and intellectual-
property lineage behind SAEE.

Truth boundary:

```text
complete_ledger_preserved_for_machine_verification=true
human_page_uses_relevance_selection=true
selected_manuscript_route_count=8
selected_patent_record_count=7
all_selected_manuscripts_published=false
selected_patents_formally_filed=false
selected_patents_granted=false
production_ready=false
customer_validated=false
```
