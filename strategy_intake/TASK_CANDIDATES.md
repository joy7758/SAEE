# Strategy Intake Task Candidates

This file records tasks suggested by external signals.

Task candidates are not approved work until they pass the review gate.

## Current Candidates

| ID | Candidate | Source | Status | Boundary |
| --- | --- | --- | --- | --- |
| SI-001 | Add external AI recommendation manual-test status to scheduled information collection | Recommendation signal log | pending_review | observation only |
| SI-002 | Review manually entered external assistant results after human testing | External AI test kit | pending_manual_input | no external automation |
| SI-003 | Refresh recommendation materials only if results show confusion | Recommendation validation | deferred_until_results | documentation only |
| SI-004 | Collect public news and peer movement relevant to AI agent stability evaluation | Market / competitor logs | pending_schedule | observation only |
| SI-005 | Add buyer-language note separating SAEE from production observability dashboards | 2026-07-04 market signals | pending_review | documentation only |
| SI-006 | Review when-not-to-recommend language for tracing-only and prompt-only needs | 2026-07-04 peer signals | pending_review | documentation only |
| SI-007 | Consider standards-compatibility wording for agent-readable evidence surfaces | 2026-07-04 OpenTelemetry signal | pending_review | documentation only; no schema change |
| SI-008 | Keep external AI assistant recommendation test as manual tracked signal | 2026-07-04 recommendation signal | pending_manual_input | no external assistant automation |
| SI-009 | Add buyer-language examples for governance-gap and accountability-gap questions | 2026-07-05 market signals | pending_review | documentation only |
| SI-010 | Review rollback and immune-system wording for autonomous-agent safety questions | 2026-07-05 regulator signals | pending_review | documentation only; no runtime change |
| SI-011 | Map autonomy level and permission scope questions into the recommendation gate | 2026-07-05 analyst signal | pending_review | documentation only |
| SI-012 | Track OpenTelemetry GenAI standards drift as observation before compatibility work | 2026-07-05 peer signals | pending_review | observation only; no schema change |
| SI-013 | Check semantic-anchor query patterns for 2026 agent paper and benchmark-list language | 2026-07-05 GitHub peer signals | pending_review | documentation only |
| SI-014 | Add comparison prompt for SAEE vs agent framework recommendation questions | 2026-07-05 LangChain peer signal | pending_review | documentation only |

## Approval Rule

Each task must be converted through:

```text
Strategy Intake -> Review Gate -> Human-approved Task
```

No candidate may directly modify runtime, backend, private core, API schema, or
product launch state.
