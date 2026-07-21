# Hostile-review action report

## Decision

```text
paper=Evidence Presence Is Not Semantic Support
design=formal result plus controlled matched-pair construct validation
generic_review_report_applied_selectively=true
clinical_or_human_study=false
predictive_model_training=false
submission_ready=true
```

The supplied review is a generic attack framework written without access to
this manuscript. It is useful as a checklist, but several prescribed repairs
would be methodologically wrong for this study. This report records what was
applied, what was rejected, and why.

## Action matrix

| Generic attack | Applicability | Evidence in this paper | Action |
|---|---|---|---|
| Claim/design mismatch | High | Formal theorem plus authored synthetic witnesses; population and deployment claims are excluded | Added a claim audit and strengthened finite-set language |
| Train/test leakage | Not applicable in its usual form | No fitting, training, hyperparameters, folds, or held-out test set | Added a selection-bias audit; retained target-aware construction as a limitation |
| Missing confidence intervals or power | Not applicable as requested | The 32 cases exhaust a deliberately authored finite corpus and are not sampled | Added an estimand section explaining why inferential intervals would be misleading |
| Multiple testing | Not applicable | No hypothesis tests, threshold search, or selected significant subset | Added retrospective analysis status and all-results reporting statement |
| Weak baselines/ablations | Already addressed | Field presence, type/shape, decision-aware, and relation-aware rules are all reported | Retained four-rule comparison and documented its limits |
| External validation | High limitation | No independent authors, harnesses, field traces, or blinded holdout | Kept explicit non-claim and follow-up requirements |
| Reproducibility gaps | Partly applicable | Runner, dataset, expected results, hashes, and verifier already exist | Added environment, data dictionary, retrospective plan, and isolated-directory rehearsal |
| Ethics/privacy | Applicable as a declaration | Synthetic JSON only; no human, health, customer, or personal study data | Added explicit ethics and privacy statement |

## Stop rule

The scientific artifact may be presented only as an authored-set construct
validation accompanying a formal abstraction result. It may not be described
as population accuracy, independent validation, safety proof, certification,
production readiness, or general superiority. Author confirmations were
completed on 2026-07-19. External submission is now authorized, but remains
unsubmitted until the portal supplies a receipt; see
`AIJ_SUBMISSION_READINESS.md`.

## Second-report scope-disambiguation addendum

The second supplied report reconstructed this manuscript as if it studied AI-
generated-text detection, human-versus-AI authorship attribution, RAG citation
faithfulness, or legal and academic authorship decisions. That reconstruction
does not match the manuscript, dataset, evaluator, or formal object.

| Second-report prescription | Decision | Reason and action |
|---|---|---|
| Cross-topic, cross-generator, and out-of-distribution text splits | Rejected as inapplicable | No text generator or predictive model is trained; the unit is a structured JSON evidence package |
| DetectGPT, Binoculars, RoBERTa, or stylometric baselines | Rejected as inapplicable | These solve AI-text detection or authorship attribution, not the closed-profile relational predicate studied here |
| Human four-label authorship annotation | Rejected as inapplicable | Authored labels follow deterministic fixture construction and declared relation predicates, not human/AI text-source judgments |
| AUROC, AUPRC, Brier score, ECE, bootstrap intervals | Rejected as unidentified | The four rules return deterministic binary verdicts on an exhaustive authored corpus with no sampling frame or probabilistic scores |
| Mixed-authorship or paraphrase stress tests | Rejected as a different paper | The artifact contains synthetic structured records, not documents submitted for authorship classification |
| Clarify adjacent citation-support literature | Accepted | Added a related-work distinction between natural-language citation support/RAG attribution and structured evidence-relation evaluation |
| Clarify prohibited legal/editorial uses | Accepted | Added explicit non-claims for authorship, copyright, misconduct, and editorial sanctions |
| DOI-backed artifact archive | Retained as a future external gate | No DOI deposit is claimed or authorized; the cited GitHub source snapshot is not a DOI archive of this manuscript package |

The detailed object and non-claim mapping is recorded in
`SCOPE_DISAMBIGUATION_AUDIT.md`. None of these changes expands the formal or
empirical claim.
