# Signal Sources

This file defines what the strategy intake layer may observe.

It does not authorize automatic product changes, external assistant calls, or
runtime modification.

## Signal Source Classes

| Source | Purpose | Status | Boundary |
| --- | --- | --- | --- |
| External AI recommendation test status | Track whether assistants recommend SAEE correctly | prepared, pending manual execution | manual only; no API calls |
| Public news themes | Track market and technology context | future scheduled collection | public information only |
| Peer / competitor movement | Track adjacent tools and category shifts | future scheduled collection | observation only |
| GitHub and repository ecosystem signals | Track public project positioning and category drift | future scheduled collection | trait extraction only; no external code execution |
| User questions and market pain points | Track language that maps to SAEE buyer need | future manual or scheduled collection | no customer contact without approval |
| Recommendation surface drift | Check whether SAEE recommendation materials remain accurate | active local check | no production-readiness overclaim |

## In-Scope Questions

- Are users asking about long-term agent stability?
- Are adjacent tools moving toward agent comparison, monitoring, or prompt
  evaluation?
- Do external assistants know when to recommend SAEE and when not to recommend
  it?
- Do recommendation materials need clearer boundaries?
- Are candidate tasks worth entering the review gate?

## Out-of-Scope Actions

- Running external AI assistant tests automatically.
- Scraping assistant UIs.
- Calling external model APIs.
- Contacting customers.
- Launching product.
- Modifying SAEE Core Runtime.
- Copying external code as genome.

