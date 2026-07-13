# From Agent Traces to Accountability Claims: A Verifiable Evidence Adequacy Framework for Agentic Systems

Draft status: `local_research_discussion_draft_not_submitted`

This manuscript is a bounded academic draft derived from a local synthetic artifact package. It is not a submission, camera-ready paper, preprint, standards document, external validation report, or production-system description.

## Abstract

Agent systems generate increasingly complex execution traces that describe model calls, tool invocations, resource references, authorization observations, and human-interaction events. These records are useful for debugging and observability, but trace data alone does not establish whether the available evidence is adequate to support a specific accountability claim. A record may be structurally valid while lacking publisher identity, content binding, authorization context, approval scope, temporal ordering, or causal linkage. This paper draft presents the SAEE evidence-adequacy framework, an implemented research prototype that separates observations from candidate evidence, evidence objects, claim-specific adequacy requirements, and bounded evaluation results. The framework includes four components: structured evidence objects for resource-resolution claims; evidence-adequacy profiles that specify required fields and semantic relationships; a candidate mapping layer for synthetic OpenTelemetry-style observations; and a deterministic synthetic benchmark. The benchmark contains 12 curated scenarios spanning four claim types and four evidence levels, from trace-only records to complete synthetic evidence packages. In the current local evaluation, all scenario outcomes, missing-requirement sets, and reason codes match their predefined expectations; the curated suite records zero false-positive outcomes and zero claim-boundary violations. These results demonstrate internal consistency against fixed fixtures, not real-world accuracy or legal proof. The evaluation uses synthetic identities, resources, approvals, actions, and effects, runs offline, and does not ingest traces from deployed agents or external OpenTelemetry systems. The artifact describes local reproduction commands and environment constraints, but it has not been independently reproduced or externally validated. SAEE therefore supports analysis of evidence adequacy for defined accountability claims while preserving a strict distinction between profile satisfaction and establishment of real-world accountability.

## 1 Introduction

Agentic systems increasingly coordinate model inference, external tools, software resources, policy decisions, and human intervention. Their execution environments commonly produce logs, spans, events, and tool-call records. Such observability surfaces help operators reconstruct system behavior, but the presence of a trace field does not by itself establish the identity, authorization, integrity, or causal relationships needed to support an accountability claim [REF-OBSERVABILITY] [REF-AGENT-SYSTEMS].

Consider an agent trace that states that a repository was cloned before a tool was executed. The trace may identify a requested repository name and a URL, yet still omit whether the URL was the resolved resource, whether the publisher identity was checked, whether the retrieved bytes matched an expected digest, whether a policy decision authorized retrieval, and whether the resulting effect was causally bound to those bytes. Similar gaps arise when a trace records an authorization reference without the policy object, or records a human identifier without review context, approved scope, and temporal ordering.

This distinction motivates the central research question of this draft:

> **What evidence relationships are sufficient to support defined accountability claims?**

We study this question through a bounded implementation called the SAEE evidence-adequacy framework. Within the broader SAEE Digital Biosphere Evolution Engine, the framework is an evidence and rollback-immune subsystem rather than the project core. It does not execute the external world, replace an agent runtime, or provide a general governance platform. Its purpose is to make the transition from observation to claim evaluation explicit and machine-checkable.

The draft makes four implementation-backed contributions:

1. an evidence-object layer that binds related resource, identity, digest, policy, and sandbox declarations;
2. claim-specific evidence-adequacy profiles that define required fields and semantic relationships;
3. a candidate mapping layer that prevents synthetic trace observations from being automatically promoted to evidence;
4. a local reproducibility and benchmark package for evaluating deterministic behavior on curated synthetic scenarios.

These contributions are research artifacts, not claims of a new standard, universal governance, legal validity, external system compatibility, or production readiness.

## 2 Related Work

This section provides a conceptual organization only. All citations remain explicit placeholders pending a separate verified literature-review task.

### 2.1 Agent Observability

Agent observability uses logs, traces, telemetry, and event correlation to expose model calls, tool invocations, handoffs, token usage, errors, and latency [REF-OBSERVABILITY] [REF-TELEMETRY]. OpenTelemetry-style semantic conventions offer a possible common representation for some observed fields [REF-OTEL]. Observability primarily addresses what a system recorded and how operators can inspect it. It does not necessarily establish the authenticity of observed identities, the integrity of retrieved content, or the validity of an authorization decision.

### 2.2 Agent Governance

Agent-governance systems commonly address identity, authorization, policy enforcement, sandboxing, and control over external actions [REF-GOVERNANCE] [REF-AUTHORIZATION]. Such controls can decide whether an operation is permitted and can produce useful policy records. However, an allow/deny decision and an execution trace do not automatically specify which combination of records is adequate to support a later claim about a particular action.

### 2.3 Audit Evidence and Provenance

Research on audit evidence and provenance studies origin, derivation, integrity, temporal ordering, and relationships among records [REF-PROVENANCE] [REF-AUDIT-EVIDENCE]. Evidence objects can package multiple assertions, while digests and signatures may support specific integrity properties. The evidentiary meaning of an object nevertheless depends on what was bound, which verification material was available, and which claim the object is intended to support.

### 2.4 Difference from SAEE

SAEE focuses on evidence-adequacy evaluation, not replacing observability or governance platforms. The framework treats telemetry fields as candidate inputs, structured receipts as evidence objects, and claim profiles as explicit requirements over fields and relationships. It then reports whether local profile requirements are satisfied while retaining `accountability_claim_established=false`. This scope differs from runtime monitoring, policy enforcement, legal adjudication, and standards conformance.

## 3 SAEE Framework

The framework separates five stages so that information cannot silently move from an observation to a stronger evidentiary conclusion.

**[FIGURE 1 PLACEHOLDER: SAEE architecture overview. See `docs/paper-draft/FIGURE_REFERENCES.md`.]**

### 3.1 Observation Layer

The observation layer accepts declarations about agents, actions, tools, resources, timestamps, and human interactions. The v0.1 artifact uses closed synthetic OpenTelemetry-style JSON rather than a live SDK, collector, or deployed-agent trace. Values at this layer remain observations produced by a system; no identity, authorization, or event-occurrence property is inferred from field presence.

### 3.2 Candidate Evidence Mapping

The mapping layer projects allowed observation fields into candidate evidence fields. Mapping outcomes are `PASS`, `PARTIAL`, or `FAIL`, depending on whether the synthetic trace contains a closed minimum context. A successful mapping can still produce an adequacy `FAIL`. In the current artifact, three successfully mapped examples remain inadequate because observation fields do not supply complete publisher, digest, policy, approval, or causal evidence.

**[FIGURE 2 PLACEHOLDER: Trace-to-evidence flow and the separation between mapping success and adequacy result.]**

### 3.3 Evidence Object Layer

The evidence-object layer represents related declarations using closed JSON contracts. The resource-resolution receipt distinguishes the resource requested by an agent from the URI declared as resolved, records a publisher-identity claim and verification method, binds synthetic inline content to a SHA-256 digest, and references a policy decision and sandbox boundary. A local receipt digest detects changes to covered fields. It is not a digital signature and does not authenticate an external publisher or resource.

### 3.4 Evidence Adequacy Layer

An adequacy profile defines the evidence fields and semantic relationships required for a bounded claim type. The evaluator distinguishes three questions:

1. Does a record or field exist?
2. Is the record structurally and locally valid?
3. Are the available fields and relationships sufficient for the selected local claim profile?

Relationship checks include equality of agent and action references, authorization-window coverage, scope coverage, approval timing, and digest-consistent causal binding. This prevents adequacy from collapsing into a count of present fields.

**[FIGURE 3 PLACEHOLDER: Evidence-adequacy evaluation flow from claim profile and evidence package to missing requirements and reason codes.]**

### 3.5 Accountability Claim Evaluation

The evaluator returns `PASS` or `FAIL`, evaluated fields, missing requirements, and stable reason codes. A `PASS` means that the current synthetic package satisfies the current local profile. It does not mean that the event occurred, the identity was independently verified, the action was legally authorized, or accountability was established. Accordingly, the result surface retains:

```text
profile_requirements_satisfied=true | false
accountability_claim_established=false
underlying_events_proven=false
production_ready=false
```

## 4 Evidence Adequacy Model

The model defines a claim as a statement that an evidence package attempts to support. Each claim profile contains required evidence paths, optional paths, semantic relationships, and stable failure reasons.

**[TABLE 1 PLACEHOLDER: Claim vs. required evidence relationships.]**

| Claim type | Required evidence focus | Key relationships | Explicit limitation |
|---|---|---|---|
| `RESOURCE_AUTHENTICITY` | requested resource, resolved URI, publisher declaration, digest, policy reference | resource receipt passes local semantic validation | does not independently establish real-world authenticity |
| `AUTHORIZED_AGENT_ACTION` | agent/action identity, requested scope, timestamp, allow decision, authority window | agent and action references match; authority scope and time cover action | does not prove an external policy service or non-revoked authority |
| `HUMAN_OVERSIGHT` | human identity declaration, review context, approved scope, approval time and decision | approval targets same action, covers scope, and precedes action | does not authenticate a real human or prove meaningful review |
| `EXECUTION_BOUNDARY` | resource receipt, content digest, resolved URI, execution effect, sandbox and causal link | receipt, effect, URI, digest, and causal references are mutually consistent | does not prove that external execution occurred |

### 4.1 Field Presence Is Insufficient

A profile can fail even when no required field is missing. For example, the benchmark contains an action record whose policy decision points to a different action, a human approval timestamp that occurs after the action, and an execution link whose digest differs from the bound resource and effect. These cases fail due to semantic relationships rather than missing fields.

### 4.2 Claim-Specific Sufficiency

Adequacy is evaluated relative to a defined claim. A resource receipt may satisfy the local `RESOURCE_AUTHENTICITY` profile while providing no support for `HUMAN_OVERSIGHT`. The framework therefore avoids a global “evidence valid” status that would obscure which proposition is being evaluated.

### 4.3 Bounded Result Semantics

The evaluator's conclusion is deliberately narrower than an accountability finding. It supports evaluation of whether specified local requirements are met. Authenticity, legal validity, external trust roots, and adjudication remain outside v0.1.

## 5 Evaluation

### 5.1 Synthetic Benchmark Design

The benchmark contains 12 curated synthetic scenarios. Each scenario specifies a claim type, evidence level, fixed local input, explicit transformations, expected result, expected missing requirements, and expected reason codes. All identities, resources, authorizations, approvals, actions, and effects are synthetic. The runner accepts only repository-controlled fixture paths and performs no network access.

### 5.2 Evidence Levels

The scenarios are evenly divided across four evidence levels:

- `LEVEL_0_TRACE_ONLY`: observations without complete evidence objects;
- `LEVEL_1_RECEIPT`: structured records with missing or inconsistent relationships;
- `LEVEL_2_RECEIPT_WITH_RELATIONSHIPS`: records with relationship fields that may still be semantically invalid;
- `LEVEL_3_COMPLETE_EVIDENCE_PACKAGE`: packages satisfying the current local profile requirements.

**[FIGURE 4 PLACEHOLDER: Benchmark evidence-level comparison for the fixed 12-scenario synthetic suite.]**

### 5.3 Metrics

- **Claim coverage** reports local `PASS/total` counts for each claim type. It is not real-world coverage.
- **Missing evidence accuracy** checks exact agreement between actual and predefined missing paths.
- **False accountability rate** is defined for future evaluation as the fraction of expected-`FAIL` cases incorrectly accepted as profile-satisfying. The v0.1 runner reports the underlying `false_positive_count`; it does not present a generalized performance rate.
- **Boundary violations** count any result that incorrectly elevates event occurrence, legal accountability, certification, external validation, or production status.
- **Reason-code accuracy** checks exact agreement between emitted and predefined local reason codes.

**[TABLE 2 PLACEHOLDER: Benchmark scenario and evidence-level summary.]**

| Evidence level | Scenarios | Local PASS | Local FAIL | Interpretation |
|---|---:|---:|---:|---|
| `LEVEL_0_TRACE_ONLY` | 3 | 0 | 3 | observations omit evidence needed by selected profiles |
| `LEVEL_1_RECEIPT` | 3 | 1 | 2 | a receipt may support a limited claim; mismatched or incomplete relationships fail |
| `LEVEL_2_RECEIPT_WITH_RELATIONSHIPS` | 3 | 1 | 2 | relationship fields do not help when time or digest semantics are inconsistent |
| `LEVEL_3_COMPLETE_EVIDENCE_PACKAGE` | 3 | 3 | 0 | current local profile requirements are satisfied |

### 5.4 Reproducibility Procedure

The artifact package declares repository paths, expected outputs, Python and dependency constraints, and Makefile commands. Validation is deterministic and offline after an approved local environment has been prepared. The package records Python 3.10 as a technical syntax/runtime floor, Python 3.14.5 as the observed local version, and `not_formally_declared` as the minimum supported version because no fixed CI version matrix has been completed.

## 6 Results

All 12 scenario outcomes match their predefined expected results. Actual missing-requirement sets match the curated expectations for 12 of 12 scenarios, and emitted reason-code sets match for 12 of 12 scenarios. Five scenarios return local profile `PASS` and seven return `FAIL`.

The fixed suite records `false_positive_count=0`: none of the seven curated expected-`FAIL` scenarios is accepted as profile-satisfying. This count applies only to the constructed dataset and must not be interpreted as a real-world false-positive rate. The runner also records `boundary_violation_count=0`: no scenario result elevates a local profile outcome into proof of event occurrence, legal accountability, certification, external validation, or production readiness.

Three relationship-focused negative cases show that field completeness alone is not sufficient. A mismatched action reference, an approval after the action, and a digest-inconsistent causal link all fail with their predefined semantic reason codes. The candidate mapping tests additionally record `trace_auto_accepted_as_evidence=0`.

These results support only an internal-consistency conclusion: the implementation behaves as specified on its fixed synthetic fixtures. They do not establish accuracy, superiority, statistical generalization, security effectiveness, or real-world accountability.

## 7 Limitations

1. **Synthetic scenarios.** The benchmark is curated and deterministic; it does not represent an observed deployment distribution.
2. **No real agents.** Inputs do not come from deployed autonomous agents, real users, or production tool chains.
3. **No external OpenTelemetry data.** The mapping layer uses synthetic OpenTelemetry-style JSON and does not import an SDK or collector output.
4. **No production deployment.** The artifact does not evaluate scalability, latency, availability, operational controls, or production integration.
5. **No legal evidence claims.** Local schema, digest, and relationship checks do not establish admissibility, legal authorization, identity, intent, or liability.
6. **No external validation.** The artifact has not been independently reproduced, externally annotated, or evaluated by a third party.
7. **No external trust roots.** v0.1 does not verify publisher credentials, certificate chains, external signatures, revocation, or remote policy authorities.
8. **No comparative baseline.** The evaluation does not compare SAEE with observability, governance, provenance, or audit systems.
9. **Limited claim set.** Only four locally defined claim types and twelve scenarios are included.
10. **Environment coverage.** Only one local Python version was observed; a fixed cross-version CI matrix is absent.

## 8 Discussion and Future Work

### 8.1 External Trace Ingestion

Future work could define a controlled ingestion boundary for real trace exports while preserving the distinction between observed values and verified evidence. Such work should evaluate redaction, schema drift, untrusted payload handling, and provenance of the trace producer before expanding the current synthetic input surface.

### 8.2 Richer Evidence Composition

Additional profiles could examine multi-agent delegation, revocation, cross-organization authority chains, memory and deletion events, and composed causal histories. These additions would require explicit trust assumptions and conflict-resolution semantics rather than broader field collection alone.

### 8.3 Privacy-Preserving Evidence

Evidence packages may expose prompts, identifiers, policy data, or execution details. Future designs could study detached payloads, selective disclosure, role-scoped views, retention limits, and deletion evidence [REF-PRIVACY-EVIDENCE]. No privacy-preserving cryptographic mechanism is implemented in v0.1.

### 8.4 External Evaluation

A next evaluation design should specify trace sources, sampling, annotation, baselines, failure taxonomy, privacy controls, and preregistered acceptance criteria before collecting data. External evaluation should be reported separately from the current curated regression suite.

### 8.5 Standard Discussions

The local crosswalk may support future discussions about terminology and interoperability [REF-AGENT-AUDIT] [REF-STANDARDS]. Mapping should not be presented as compliance, conformance, adoption, or normative contribution unless relevant specifications are independently verified and an implementation is tested against them.

## 9 Conclusion

This draft presents SAEE as an implemented research framework for evaluating whether available evidence fields and relationships satisfy defined accountability-claim profiles. It separates observations, candidate mappings, evidence objects, adequacy requirements, and bounded evaluation outcomes. On a fixed 12-scenario synthetic benchmark, the implementation matches predefined local expectations and preserves explicit claim boundaries.

The contribution is deliberately limited. SAEE explores evidence adequacy evaluation for agent accountability claims; it does not establish real-world events, legal responsibility, external-system compatibility, or production readiness. The next research step is to design an external evaluation that preserves these boundaries while testing the framework on independently sourced trace and evidence material.

## Artifact References

- `agent-interface/research-artifact/saee-artifact-manifest.v0.1.json`
- `docs/research-artifact/SAEE_RESEARCH_ARTIFACT_OVERVIEW.md`
- `docs/research-artifact/SAEE_ARCHITECTURE.md`
- `docs/research-artifact/SAEE_EXPERIMENT_SUMMARY.md`
- `docs/EVIDENCE_ADEQUACY_BENCHMARK.md`
- `agent-interface/benchmarks/evidence-adequacy/benchmark.v0.1.json`
- `agent-interface/reproducibility/expected-results.v0.1.json`
- `docs/REPRODUCE_SAEE_EXPERIMENT.md`
- `docs/REPRODUCIBILITY_ENVIRONMENT_REQUIREMENTS.md`

## Citation Placeholders

- `[REF-AGENT-SYSTEMS]`: agentic-system architecture and execution research.
- `[REF-OBSERVABILITY]`: agent and distributed-system observability research.
- `[REF-TELEMETRY]`: telemetry and trace semantics.
- `[REF-OTEL]`: verified OpenTelemetry primary documentation or specification.
- `[REF-GOVERNANCE]`: agent governance and runtime-control research.
- `[REF-AUTHORIZATION]`: authorization and policy-decision research.
- `[REF-PROVENANCE]`: provenance and evidence-object research.
- `[REF-AUDIT-EVIDENCE]`: audit-evidence and evidentiary-adequacy research.
- `[REF-PRIVACY-EVIDENCE]`: privacy-preserving evidence research.
- `[REF-AGENT-AUDIT]`: independently verified agent-audit specification or research.
- `[REF-STANDARDS]`: independently verified standards-related sources.
