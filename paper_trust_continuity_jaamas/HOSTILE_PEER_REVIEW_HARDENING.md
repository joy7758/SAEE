# Hostile Peer-Review Hardening

Snapshot date: 2026-07-17

## Scope and command audit

This review applies only to the canonical manuscript package at
`paper_trust_continuity_jaamas`. The attachment named a non-existent parallel
draft under `papers/saee_trust_continuity_draft.md`; that path was not created.
The repository already contains a heavily modified and partially staged main
workspace, so the requested branch, staging, and commit operations were not
performed. Creating a branch from that state would not isolate the paper.

The paper remains a future-research Viewpoint. No code, schema, MCP artifact,
capability inventory, runtime, fixture, or experimental result was created.

```text
ATTACHMENT_TARGET_PATH_EXISTS=false
CANONICAL_MANUSCRIPT_USED=paper_trust_continuity_jaamas/MANUSCRIPT.md
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_CORRECTION=PAPER_ONLY_FUTURE_RESEARCH_SCOPE
EXPERIMENT_EXECUTED=false
GIT_BRANCH_CREATED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_CREATED=false
GIT_PUSH_EXECUTED=false
```

## Executive verdict

A hostile reviewer can still challenge whether the proposed construct earns a
distinct name, but the current manuscript is not the underdefined draft
described in the attachment. Before this pass it already contained:

- a claim-ground-transition assessment relation;
- explicit boundaries against authorization, execution, and universal scores;
- a composition analysis for provenance, observability, identity, MCP, A2A,
  and governance;
- a staged evaluation program with baselines and metrics; and
- eight explicit falsification and stop conditions.

The attachment's strongest valid criticism was narrower: recent adjacent work
on multi-agent contracts, agentic trust-risk-security management, inter-agent
message trust, and trace-based assurance was not represented. The manuscript
also needed a clearer ethics and legal boundary and a more concrete first-study
design. Those gaps were addressed without converting the Viewpoint into a
results paper.

```text
HOSTILE_REVIEW_VERDICT=MAJOR_REVISION_RISK_REDUCED
NOVELTY_PROVEN=false
DISTINCT_CONSTRUCT_VALUE_UNTESTED=true
VIEWPOINT_ARTICLE_TYPE_RETAINED=true
```

## Attack matrix

| Hostile attack | Finding against the current manuscript | Severity after revision | Disposition |
| --- | --- | --- | --- |
| “This is only a category label.” | Still a legitimate risk. The paper cannot prove a field exists; it can only define a testable question and surrender the label if simpler methods suffice. | Major | Retain candidate-category wording and explicit abandonment conditions. |
| “The construct is not operational.” | The attachment is stale. Section 4.2 already defines inputs and qualified outputs, while Sections 7 and 8 define annotations, baselines, metrics, and stop rules. Empirical identifiability remains untested. | Major | Added a concrete minimum pilot without claiming execution. |
| “There is no evaluation plan.” | Incorrect for the current draft. The plan was already substantial. | Minor | Added only a bounded first-study design; rejected a large benchmark mandate. |
| “Contracts and runtime assurance already solve this.” | Previously under-addressed. Recent formal contracts and trace-based assurance are strong baselines. | Major | Added direct comparisons and an absorption stop condition. |
| “Message trust management already solves this.” | Previously missing. Message or agent trustworthiness is close but not identical to later applicability of declared grounds. | Major | Added the accepted ACL work as a direct baseline. |
| “The paper ignores recent agentic trust surveys.” | Valid before revision. | Minor | Added the 2026 TRiSM review and narrowed the category-level claim. |
| “The scope mixes protocols, identity, governance, and observability.” | The prose boundaries existed but were expensive to reconstruct. | Minor | Added an operational boundary table. |
| “The legal and privacy consequences of pervasive evidence are ignored.” | Valid before revision. | Major | Added data-minimization, retention, surveillance, and jurisdictional limits plus a scoped EU AI Act discussion. |
| “The paper implies deployment or compliance.” | Not supported by the current text. | Minor | Preserved explicit non-claims and added a no-compliance statement. |
| “The paper needs experimental results.” | Not required by the target journal's Viewpoint definition, which is intended to stimulate new areas rather than report original research. | Minor | Retain Viewpoint framing; do not fabricate or prematurely execute a study. |

## Verified adjacent work added

1. Dewes and Dimitrova, “Contract-based Design and Verification of Multi-Agent
   Systems with Quantitative Temporal Requirements,” AAAI 2025. This is a
   peer-reviewed formal-contract baseline:
   <https://doi.org/10.1609/aaai.v39i22.34480>
2. Raza et al., “TRiSM for Agentic AI,” *AI Open* 2026. This is a broad,
   peer-reviewed lifecycle review and a category-level collision:
   <https://doi.org/10.1016/j.aiopen.2026.02.006>
3. He et al., “To Trust or Not to Trust: Attention-based Trust Management for
   LLM Multi-Agent Systems.” The arXiv record states acceptance to ACL 2026
   main; it is used as a message- and agent-trust baseline:
   <https://arxiv.org/abs/2506.02546>
4. Paduraru et al., “Trace-to-Logic Assurance for Agentic AI,” ENASE 2026. This
   is a peer-reviewed trace-analysis and runtime-deviation baseline:
   <https://doi.org/10.5220/0014983100004015>
5. Regulation (EU) 2024/1689 is used only to illustrate scoped logging,
   documentation, transparency, oversight, and retention obligations for
   covered high-risk systems:
   <https://eur-lex.europa.eu/eli/reg/2024/1689/oj>

## Official boundary sources rechecked

- A2A 1.0 specifies discovery, messaging, task and artifact exchange, and
  long-running interaction semantics; it is not cited as a trust decision
  system: <https://a2a-protocol.org/latest/specification/>
- MCP's latest specification remains an interaction and context-exchange
  protocol with capability negotiation, not a continuity evaluator:
  <https://modelcontextprotocol.io/specification/latest>
- OpenTelemetry defines telemetry signals and collection semantics, not the
  later applicability of a bounded reliance claim:
  <https://opentelemetry.io/docs/concepts/signals/>
- NIST emphasizes context-sensitive testing, evaluation, validation, and
  verification rather than a universal trust measurement:
  <https://www.nist.gov/ai-test-evaluation-validation-and-verification-tevv>
- JAAMAS explicitly defines Viewpoints as timely articles intended to stimulate
  activity in new areas or ideas rather than report original research, and
  requires a rigorous 1-2 page information sheet:
  <https://link.springer.com/journal/10458/submission-guidelines>

## Sources not promoted into the core argument

The attachment also pointed toward several 2026 runtime-safety and runtime-
protection preprints. They were not added merely because they were recent.
Where acceptance or archival publication could not be verified, they were
excluded from the numbered reference list in accordance with the journal's
reference rule. Citation placeholders were not inserted into a submission-ready
draft.

Commercial and identity-industry pages now use the exact phrase `trust
continuity`. That reinforces the existing prohibition on claiming the phrase as
new, but such pages are not used as evidence for the academic construct.

## Surgical revisions completed

- Added recent-work collisions to the introduction and synthesis method.
- Added direct distinctions from contract verification, TRiSM, message trust
  management, and trace-to-logic assurance.
- Added captions for the existing dimension table and the new infrastructure
  boundary table.
- Added a concrete minimum pilot with paired transitions, blinded annotation,
  strong baselines, and scoped metrics.
- Added ethical and legal considerations with explicit non-surveillance and
  no-compliance boundaries.
- Updated the information sheet, literature matrix, novelty-collision review,
  and claims boundary.

## Revisions deliberately rejected

- No claim that 200-500 traces are required before the construct is defined.
- No procurement or helpdesk case study was invented.
- No result, precision, recall, agreement, or runtime cost was fabricated.
- No `TODO` or unresolved citation placeholder was inserted into the manuscript.
- No new state engine, goal engine, governance platform, protocol, schema, or
  product capability was created.

## Residual rejection risk

The main residual risk is substantive rather than editorial: a reviewer may
conclude that claim-ground continuity is already expressible through contracts,
provenance, assurance cases, or ordinary domain checklists. The manuscript now
accepts that outcome explicitly. The proposed category earns further work only
if a later study demonstrates more stable annotation or better decision utility
than those alternatives at acceptable cost.

```text
HOSTILE_REVIEW_HARDENING_STATUS=COMPLETE
RECENT_RELATED_WORK_GAP_REDUCED=true
ETHICS_LEGAL_BOUNDARY_ADDED=true
MINIMUM_EVALUATION_PLAN_ADDED=true
EMPIRICAL_VALIDATION_COMPLETED=false
CURRENT_CAPABILITY_CHANGED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
PAPER_SUBMITTED=false
```
