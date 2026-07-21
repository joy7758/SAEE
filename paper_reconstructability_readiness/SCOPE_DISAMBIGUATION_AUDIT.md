# Scope disambiguation audit

## Actual research object

```text
unit_of_analysis=structured synthetic JSON evidence package
target_label=closed-profile semantic support
decision_rule=file-backed deterministic relational predicates
formal_question=whether an evidence abstraction separates different labels
experiment=16 authored matched positive-negative pairs
model_fitting=false
natural_language_authorship_classification=false
```

The paper asks whether a representation preserves every relation required by a
named AI-agent evidence claim. It does not infer who wrote text, whether a
language model generated text, or whether a model causally relied on a cited
passage.

## False reconstruction detected

The supplied second hostile-review report treated the manuscript as a study of
one or more of the following:

```text
AI-generated-text detection
human-versus-AI authorship attribution
mixed-authorship classification
RAG citation correctness or faithfulness
legal authorship or copyright ownership
academic-misconduct adjudication
```

None is present in `main.tex`, `experiment/dataset.v0.1.json`, the deterministic
runner, or the evaluator snapshot. Implementing generator splits, stylometric
baselines, human authorship annotation, or probabilistic calibration would
replace the current research question rather than repair it.

## Accepted repair

1. The Introduction now states the unit of analysis and explicitly excludes AI-
   text detection, authorship attribution, RAG citation-faithfulness
   evaluation, and legal or misconduct adjudication.
2. Related work now distinguishes natural-language citation support and RAG
   attribution faithfulness from the structured evidence-relation predicate.
3. The authority-validity discussion and machine-readable claim boundary now
   prohibit authorship, copyright, misconduct, and editorial-sanction uses.
4. The DOI-backed archive state is made explicit without claiming a deposit.

## Adjacent-literature boundary

ALCE asks whether generated natural-language answers carry citations and
whether those citations support their statements. Work separating correctness
from faithfulness in RAG asks whether a cited document is not only compatible
with an answer but was actually used by the generator. This manuscript instead
evaluates deterministic relations among structured evidence operands. The
neighboring work supports the general warning that presence is insufficient;
it does not supply this paper's label, dataset, or evaluator.

## External archive state

```text
source_snapshot_cited=true
source_snapshot_is_manuscript_package_archive=false
doi_backed_archive_deposited=false
archive_deposit_authorized=false
submission=false
publication=false
```

A future DOI deposit would be a separate external action requiring author
approval and an immutable, privacy-reviewed artifact package.
