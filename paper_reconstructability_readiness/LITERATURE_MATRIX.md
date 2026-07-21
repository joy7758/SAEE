# Literature and novelty matrix

Reviewed against primary papers and official standards available on
2026-07-19. This is a collision and positioning audit, not an exhaustive
systematic review.

| Work | Main contribution | Relationship and distinction |
|---|---|---|
| Solozobov, *Load-Bearing Evidence* (2026) | Eight-property cross-harness reconstructability metric | Direct motivation, but this paper studies the sufficiency of an evidence abstraction for semantic labels; it neither reimplements the metric nor performs replay |
| Nian et al., *Auditable Agents* (2026) | Auditability dimensions and mechanism classes | Supports separation of recovery, policy checking, and evidence integrity; this paper is not a full auditability framework |
| AgentTrace / OpenTelemetry | Structured runtime observations | Potential upstream capture surfaces; this paper evaluates relations after capture and contributes no instrumentation |
| W3C PROV | Relational provenance model | Establishes that provenance semantics depend on relations, not isolated fields; no PROV conformance is claimed |
| Gao et al., ALCE (2023) | Evaluates generated answers with citations, including citation support | Adjacent warning that citation presence is insufficient; this paper does not evaluate natural-language answers or source relevance |
| Wallat et al. (2024) | Separates correctness from causal faithfulness in RAG attributions | Adjacent distinction between a support-compatible citation and actual generator reliance; this paper evaluates deterministic structured relations, not model reliance |
| Segura et al. (2016) | Survey of metamorphic testing | Grounds the paired-transformation design; our metamorphic relation is verdict divergence under value mutation with structure preservation |
| Ribeiro et al., CheckList (2020) | Behavioral tests beyond aggregate accuracy | Grounds capability- and behavior-oriented failure discovery; our target is evidence-claim validity rather than NLP behavior |
| Jia and Harman (2011) | Mutation-testing development and survey | Grounds deliberate perturbation as a test-strength probe; no mutation-score comparison is claimed |
| Rabanser et al. (2026) | Multidimensional agent reliability | Motivates rejecting one-dimensional success/completeness scores; this paper does not estimate agent reliability |
| NIST AI RMF | Govern/Map/Measure/Manage separation | Supports keeping measurement separate from contextual authority; no certification or conformance is claimed |
| AgentBound / xChk (2026) | Runtime governance and verifier-determined sufficiency | Supports separating supplied evidence from relying-party permission; this paper implements neither identity nor authorization |

## Novelty statement

The AIJ-oriented novelty is the combination of:

1. a general claim-separation criterion for evidence abstractions;
2. a matched-pair error lower bound for non-separating abstractions;
3. 16 executable witnesses spanning four agent-evidence claim families;
4. a gradient from presence to structure to decision semantics to relations;
5. pinned pre-study evaluator/profile/fixture components; and
6. machine-enforced non-claims preventing local profile support from becoming
   external truth or authorization.

The theorem is intentionally concise. Its value is not mathematical depth in
isolation; it provides a testable design criterion and connects representation
sufficiency to concrete AI-agent evaluation failures.

## Collision stop rules

```text
Load-Bearing Evidence=eight-property cross-harness reconstructability
this paper=claim separation under evidence abstraction
metric reimplementation=false
executed replay=false
cross-harness experiment=false
general agent benchmark=false
```
