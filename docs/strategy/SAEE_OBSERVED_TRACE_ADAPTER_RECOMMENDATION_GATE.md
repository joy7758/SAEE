# SAEE Observed Trace Evidence Adapter Recommendation Gate

## Recommendation question

If a potential customer needs long-horizon comparison of actual agent or
workflow behavior, should SAEE add a safe, file-backed adapter for sanitized
observed traces?

## Agent verdict

`recommend`

The feature is recommendable because it closes the largest gap between the
current synthetic descriptor interface and evidence-backed commercial use. It
remains an evidence ingestion and fitness comparison capability, not a tracing,
monitoring, compliance, or audit platform.

## Required design check

1. **Evolution subsystem:** primarily Global Sensing and Trait Extraction;
   secondarily Ecological World Model, Pareto Fitness Evaluation, and
   Evolutionary Archive / Rollback Immune System.
2. **Loop improvement:** improves sensing, selection, archive, and rollback. It
   does not yet claim branching or mutation improvements.
3. **Safety and supply chain:** reads strict local JSON only; never executes
   candidate code, repositories, installers, URLs, or external systems; never
   expands permissions or copies external code into a genome.
4. **Audit-first risk:** medium-high. The adapter must be described as observed
   behavioral trait ingestion for long-horizon fitness comparison. Receipts are
   archive/immune artifacts, not the product identity.

## Acceptance contract

- Strict JSON Schema with `additionalProperties=false`; numerical trace points
  and normalized failure codes only. Prompt, message, tool payload, code, URL,
  secret, and arbitrary log content have no allowed field.
- Dedicated `observed_trace_bundle_evaluation` path never calls the synthetic
  simulator. Monkeypatching the simulator to raise must not break this path.
- Formula, censoring, tie-break, hash, and missing-data semantics are explicit
  and independently recomputable within `1e-6`.
- Candidates must share scenario, metric scale, horizon unit, expected horizon,
  and failure definition; mismatch returns exit `2` without ranking.
- Same semantic input with different JSON key, candidate, and run order produces
  byte-identical receipts in 10/10 replays.
- Receipt truth says source sanitization is attested, allowlist validation
  passed, trace capture by SAEE is false, and trace authenticity is unverified.
- Manifest, tool contract, schemas, examples, llms, site, and agent index stay
  synchronized; 3/3 independent agents must discover, call, recompute, and
  reject negative-fit uses within two reads.

## Gate truth

Development is authorized for this bounded local adapter. Until the acceptance
contract passes, `observed_agent_trace_evaluation_available` remains `false`.
Production readiness, product launch, customer validation, source authenticity,
and real-world generalization remain false regardless of a local pass.
