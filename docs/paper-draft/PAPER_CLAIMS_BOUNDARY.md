# SAEE Academic Paper Draft Claims Boundary

## Draft state

```text
paper_draft_created=true
paper_submitted=false
paper_accepted=false
arxiv_uploaded=false
doi_created=false
external_validation=false
production_ready=false
```

Paper Draft ≠ Paper Submission  
Research Prototype ≠ Production System  
Synthetic Evaluation ≠ Real-world Validation

## Supported claims

The draft may state only that:

- a local framework has been implemented for separating observations, candidate mappings, evidence objects, adequacy profiles, and bounded claim evaluation;
- four local claim profiles are represented in machine-readable files;
- the synthetic benchmark has been executed locally on 12 curated scenarios;
- actual local results, missing requirements, and reason codes match predefined expectations for 12/12 scenarios;
- the curated suite records `false_positive_count=0` and `boundary_violation_count=0`;
- local reproducibility files, commands, expected outputs, Python observations, and dependency constraints are described;
- the artifact provides a framework for and supports evaluation of evidence adequacy under its explicit local assumptions.

## Unsupported claims

The draft must not state or imply:

- a universal AI-governance solution;
- guaranteed accountability, authenticity, authorization, oversight, or causality;
- legal proof, admissibility, liability attribution, or regulatory acceptance;
- compliance, conformance, adoption, or certification against an external standard;
- production readiness, commercial deployment, reliability, scalability, or security certification;
- external validation, independent reproduction, real-world accuracy, statistical generalization, or superiority over another system;
- paper submission, acceptance, publication, arXiv upload, DOI creation, GitHub release, or publication tag.

## Required wording

Prefer:

- “supports evaluation of”;
- “provides a framework for”;
- “enables analysis of”;
- “matches predefined expectations on a curated synthetic suite”;
- “satisfies the current local profile requirements”.

Avoid unqualified uses of:

- “solves”;
- “guarantees”;
- “proves”;
- “certifies”;
- “complies”;
- “production ready”.

Negated boundary statements may use these words only to explain what the draft does not claim.

## Evidence sources

- `agent-interface/research-artifact/saee-artifact-manifest.v0.1.json`
- `agent-interface/reproducibility/expected-results.v0.1.json`
- `docs/research-artifact/SAEE_EXPERIMENT_SUMMARY.md`
- `docs/research-artifact/PAPER_ARTIFACT_CHECKLIST.md`

Any stronger statement requires new evidence and a separate claims review. Local prose changes cannot promote an external state.
