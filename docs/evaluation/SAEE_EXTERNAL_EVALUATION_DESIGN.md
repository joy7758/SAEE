# SAEE External Evaluation Design v0.1

Status: `design_only`; no dataset collection, agent execution, baseline implementation, result generation, or external validation has occurred.

```text
Evaluation Design ≠ Evaluation Result
Experiment Protocol ≠ Experimental Validation
Planned Baseline ≠ Completed Comparison
Synthetic Validation ≠ Real-world Validation
```

This protocol is part of the evidence and rollback-immune subsystem within the broader SAEE Digital Biosphere Evolution Engine. It does not redefine SAEE as a general audit or governance platform.

## 1 Research Objective

The goal is to evaluate whether SAEE can assess evidence sufficiency for defined accountability claims under controlled scenarios that more closely resemble agent tool execution. The protocol asks whether different combinations of traces, receipts, and semantic evidence relationships support or fail to support a claim-specific local adequacy decision.

The evaluation is not intended to show that SAEE improves a production system, proves a real event, establishes legal accountability, or is superior to another approach. Those propositions require different evidence and are outside this design.

### Unit of analysis

The primary unit is one `claim_attempt`: one bounded agent task attempt, one selected accountability claim, one evidence condition, and one independently annotated reference bundle. Reporting must remain claim-level so that multiple claims derived from one task are not treated as independent runs without clustered analysis.

### Preregistration requirements

Before any main evaluation, a future execution plan should freeze:

- task and claim inclusion criteria;
- evidence-condition construction rules;
- baseline implementations;
- primary and secondary metrics;
- exclusion and failure rules;
- pilot/main split and power analysis;
- annotation codebook and adjudication procedure;
- statistical model and multiplicity handling;
- privacy, licensing, retention, and deletion controls.

## 2 Research Questions

### RQ1: Trace-only support

**How much accountability information can be supported by trace-only observations?**

Planned analysis: under Condition A, compare trace observations with independently annotated required evidence for each claim type. Report supported-claim coverage, unsupported-claim acceptance, and the distribution of missing evidence. Trace-field count alone must not be used as evidence adequacy.

### RQ2: Effect of structured evidence objects

**How does adding structured evidence objects affect evidence adequacy evaluation?**

Planned analysis: compare the same claim attempts across Conditions A–D. Use paired comparisons where the underlying task and claim are identical. Separate the effect of adding a receipt from the effect of adding valid semantic relationships.

### RQ3: Missing relationships and false accountability

**Can SAEE identify missing evidence relationships and avoid false accountability claims?**

Planned analysis: compare emitted missing-field and invalid-relationship sets against independent annotations. Report false accountability outcomes beside claim-support coverage so that a system cannot appear stronger merely by accepting more claims.

## 3 Evaluation Scenario

### Recommended first scenario: Code Agent Tool Execution

This scenario is recommended because it can be made reproducible, its tool and resource interactions are observable, resource/action/authorization relationships can be controlled, and failures can be injected without relying on subjective task quality.

The planned sequence is:

```text
Agent receives a bounded task
        ↓
Agent selects an allowlisted local tool
        ↓
Agent declares or accesses a version-pinned local resource
        ↓
Policy permits or denies the planned action
        ↓
Sandbox records a known effect or denial
        ↓
Evidence bundle is assembled under Condition A, B, C, or D
        ↓
One accountability claim is evaluated
```

No part of this sequence is executed in v0.1.

### Safety design for future execution

- use an isolated, non-networked sandbox;
- use allowlisted local tools and version-pinned researcher-owned task assets;
- never clone or execute an unknown external repository;
- prohibit package installation and permission expansion during the task;
- predefine allowed effects and denial cases;
- bind every task attempt to a stable task, action, policy, sandbox, resource, and effect identifier;
- record aborted and denied attempts rather than silently excluding them.

### Planned task strata

Future tasks should cover at least:

- authorized resource inspection;
- unauthorized resource request denied before effect;
- authorized tool invocation with known effect;
- mismatched resource or action reference;
- human-approval-required action approved before execution;
- late, absent, or scope-insufficient approval;
- effect record with valid or invalid causal digest binding.

### Sampling and assignment

A pilot should estimate class balance, task failure rates, annotation ambiguity, and within-task correlation. Final sample size must then be justified by a preregistered power or precision analysis. Evidence conditions should be generated from the same reference task bundle and assigned in a blocked, randomized order for human review. No sample-size result exists in this design.

## 4 Evidence Conditions

The conditions are planned comparison treatments, not completed experiments.

### Condition A: Trace Only

Contains agent/action observations, tool-call observations, resource-reference strings, timestamps, and observed outcomes. It intentionally omits independently bound receipts and complete policy, approval, publisher, digest, or causal material.

### Condition B: Trace + Receipt

Adds a structured resource or action receipt. The receipt may be locally valid while references or relationships remain absent or inconsistent. This condition tests whether object presence is incorrectly treated as claim sufficiency.

### Condition C: Trace + Receipt + Evidence Relationships

Adds authorization, temporal, scope, and causal relationship fields. Controlled negative variants retain all expected fields while mutating one relationship, such as action identity, approval order, or digest binding.

### Condition D: Complete SAEE Evidence Package

Adds all fields and relationships required by the selected SAEE profile, together with the verification material available in the controlled scenario. `Complete` means complete relative to the preregistered local profile; it does not mean legal, universal, or externally authentic.

### Condition-construction invariant

For a paired comparison, the task attempt and reference event facts remain fixed. Only the evidence presentation changes. Every transformation must be recorded in a manifest so that condition differences cannot hide changes to the underlying task.

## 5 Baselines

The baselines are conceptual definitions. No baseline has been implemented or run.

### Baseline A: Observability-only approach

Decision surface: presence and internal consistency of trace fields. It may identify missing observations but does not require a structured evidence object or claim-specific relationship profile.

### Baseline B: Receipt/log based approach

Decision surface: presence and local validity of a structured receipt or log record. It does not require all claim-specific semantic relationships.

### Baseline C: SAEE evidence adequacy approach

Decision surface: claim-specific required fields, locally validated evidence objects, and semantic relationships. Its output remains profile satisfaction rather than real-world accountability.

### Fair-comparison requirements

- use the same claim attempts and evidence-condition inputs;
- expose the same non-sensitive source fields to each baseline;
- document any baseline-specific normalization;
- freeze decision thresholds before main evaluation;
- report abstentions and errors, not only accepted claims;
- do not tune on the final evaluation partition;
- avoid product or vendor names unless a later verified study justifies them.

## 6 Metrics

Primary metrics must be reported together and stratified by claim type, evidence condition, and task stratum. Accuracy-only reporting is not sufficient.

### 6.1 False Accountability Rate

```text
FAR = unsupported claims incorrectly accepted
      ----------------------------------------
      all reference-unsupported claims
```

The reference label describes whether the evidence package supports the selected bounded claim under the annotation protocol. FAR does not measure legal error, event falsity, or universal safety. Confidence intervals and raw numerator/denominator counts should accompany the rate.

### 6.2 Missing Evidence Identification Accuracy

Report:

- exact missing-set match per claim attempt;
- item-level precision, recall, and F1 for missing fields;
- the same set metrics for invalid relationships;
- reason-code agreement as a diagnostic measure.

The term `accuracy` refers to agreement with protocol annotations, whose disagreement and adjudication rates must be disclosed.

### 6.3 Claim Support Coverage

```text
CSC = reference-supportable claims marked profile-satisfied
      ----------------------------------------------------
      all reference-supportable claims
```

Coverage must be interpreted beside FAR. A method that accepts every claim would have high coverage and unacceptable false accountability.

### 6.4 Evidence Relationship Completeness

```text
ERC = present and reference-valid required relationships
      --------------------------------------------------
      all required relationships for the selected claim
```

ERC should be calculated separately for reference equality, scope, time, receipt validity, and causal binding. Completeness does not prove that an external identity, authorization, or causal event is genuine.

### Secondary and safety reporting

- abstention and evaluator-error count;
- boundary-violation count;
- deterministic-repeat agreement;
- annotation-disagreement and adjudication rate;
- per-condition evidence volume and sensitive-field exposure;
- processing time only as an operational descriptor, not the main research contribution.

### Planned statistical analysis

Use paired or clustered analysis because multiple conditions and claims may originate from the same task attempt. Report effect estimates with uncertainty rather than p-values alone. The exact model, confidence level, multiplicity policy, and minimum detectable effect must be preregistered after the pilot and before the main evaluation.

## 7 Dataset Requirements

Every dataset option requires a manifest describing source, owner, license or permission, collection method, transformations, redactions, retention, deletion, and allowed research uses.

Required modalities are:

- agent action traces;
- tool calls;
- resource references;
- authorization events;
- human approval events where the scenario requires them;
- execution outcomes or explicit denials;
- authoritative task, policy, resource, and expected-effect reference bundles.

### Synthetic option

Use researcher-controlled tasks and assets with known reference relationships. This option supports fault injection and initial protocol testing, but it remains synthetic and cannot establish real-world validity.

### Real-world option

Use independently sourced or consenting-participant traces only after source approval, license and terms review, privacy assessment, redaction, retention planning, and provenance documentation. Real-world traces must not be assumed to contain ground-truth authorization or causality merely because they are authentic logs.

### Hybrid option

Use realistic, approved trace structures with controlled omissions and relationship mutations. This can preserve known reference labels while testing more realistic field distributions. Every injected mutation must be separately marked and unavailable to blinded annotators.

### Exclusion rules

Exclude or quarantine:

- data without provenance or permission records;
- secrets, credentials, private keys, or unnecessary personal data;
- traces whose task or policy context cannot be reconstructed;
- external code or repositories requiring execution to interpret;
- cases with unresolved license, consent, or retention status;
- corrupted records, while still reporting exclusion counts and reasons.

No dataset has been selected, downloaded, or evaluated under this design.

## 8 Annotation Protocol

### Annotation unit and labels

Annotators review one claim attempt and label:

- `claim_support_status`: `SUPPORTED`, `UNSUPPORTED`, or `INDETERMINATE` under the protocol;
- `missing_evidence_set`;
- `invalid_relationship_set`;
- authorization boundary and whether scope/time cover the action;
- causal relationship status;
- uncertainty reason and evidence references used for the judgment.

`SUPPORTED` means the presented evidence is adequate under the codebook for the bounded claim. It does not mean the real event or legal proposition is proven.

### Procedure

1. Two annotators independently review each item.
2. Annotators are blinded to evaluation condition labels, system output, and injected-mutation identifiers.
3. Evidence is shown in a normalized, order-randomized view.
4. Annotators record evidence references and uncertainty, not only a class label.
5. Disagreements go to a third adjudicator after the independent pass is frozen.
6. Codebook changes trigger re-annotation of the affected pilot items and version increments.
7. Main-evaluation labels are frozen before method outputs are compared.

### Inter-annotator agreement

Report Cohen's kappa or Krippendorff's alpha for categorical labels, plus set Jaccard and item-level F1 for missing/invalid relationship sets. A provisional target of at least 0.80 is proposed before the main evaluation; failure to reach it requires codebook revision, ambiguity analysis, or redefinition of the construct. The target is planned and has not been measured.

### Annotator qualifications and conflicts

Record training, domain familiarity, conflicts of interest, and whether an annotator contributed to SAEE implementation. At least one independent annotator should participate in the final phase. Developer annotations alone cannot be reported as independent validation.

## 9 Threats to Validity

### Internal validity

- scenario-design bias may favor known SAEE relationships;
- condition generation may accidentally change the underlying task;
- baseline tuning may use evaluation labels;
- annotation codebooks may encode evaluator assumptions;
- task failures and exclusions may distort class balance.

Mitigations: paired condition manifests, frozen transformations, holdout partitions, blinded annotation, preregistered exclusions, and reporting all failure paths.

### External validity

- code-agent tool execution is only one domain;
- controlled local tools may not reflect multi-organization or long-horizon agents;
- selected trace sources may omit privacy, memory, delegation, and revocation behavior;
- real deployments may use different policy and identity systems.

Mitigation: report domain limits and add new domains only through separately versioned protocols.

### Construct validity

- evidence adequacy is defined by local claim profiles;
- `SUPPORTED` may be confused with event truth or legal proof;
- relationship completeness may not capture trust-root quality;
- false accountability depends on annotation quality.

Mitigations: explicit construct definitions, `INDETERMINATE` labels, independent review, sensitivity analysis over profile requirements, and separate truth-boundary reporting.

### Reproducibility

- Python, dependency, collector, and agent-runtime versions may differ;
- trace schemas and tool outputs may drift;
- external datasets may become unavailable or restricted;
- privacy redaction may make full replay impossible.

Mitigations: versioned environment manifests, immutable input hashes where permitted, transformation logs, offline replay packages, and clear disclosure of non-shareable data.

## 10 Future Execution Plan

All phases are planned and not started.

### Phase 1: Dataset preparation

- approve data source, privacy, license, consent, retention, and provenance plans;
- build a researcher-controlled pilot corpus;
- freeze task identifiers and reference bundles;
- run annotation training and revise the codebook;
- estimate variance and define the main-study sample size.

Exit gate: dataset and annotation protocol approved; no evaluation result claimed.

### Phase 2: Baseline implementation

- implement the three comparison decision surfaces against a shared input contract;
- add unit and negative tests;
- freeze thresholds and failure behavior;
- prevent final-partition tuning.

Exit gate: baseline code locally validated; no comparative result claimed.

### Phase 3: SAEE evaluation

- run the preregistered conditions on the frozen evaluation partition;
- preserve raw outputs and errors;
- compute metrics with uncertainty and stratification;
- perform boundary and privacy audits.

Exit gate: internal results package prepared; external validation still false.

### Phase 4: Independent validation

- provide the frozen protocol, permitted data, environment, and analysis scripts to independent evaluators;
- record deviations and reproduction failures;
- separate independent results from developer-run results;
- update external-validation status only after independently reviewable evidence exists.

Exit gate: defined by a future independent-validation protocol; not satisfied by this design.

## Current Truth State

```text
status=design_only
executed=false
external_data_used=false
real_agents_run=false
opentelemetry_collectors_run=false
external_code_executed=false
external_validation_completed=false
results_available=false
production_ready=false
```
