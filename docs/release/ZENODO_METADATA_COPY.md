# Zenodo Metadata Copy
# Zenodo 元数据复制稿

Status: Zenodo current version published on 2026-07-06.

## Title

SAEE: AI Agent Long-term Stability Evaluation and Decision Infrastructure System

## Abstract

SAEE is an AI agent long-term stability evaluation and decision infrastructure system. It provides a public product-facing layer for long-horizon evaluation, multi-agent comparison, failure-mode analysis, survival ranking, and deploy / hold / retest decision support while preserving the project identity of Silicon-Amplified Evolutionary Ecology and the engineering core of the Digital Biosphere Evolution Engine.

This metadata copy is intended to align Zenodo with the repository and landing-page definition. It does not disclose private implementation internals, kernel logic, mutation logic, selection logic, scoring internals, or lineage internals. It does not claim production readiness, customer validation, benchmark superiority, external validation success, or a public SDK release.

## Keywords

- SAEE
- Silicon-Amplified Evolutionary Ecology
- AI agents
- agent evaluation
- long-term stability
- multi-agent comparison
- failure-mode analysis
- deployment decision support
- decision infrastructure
- Digital Biosphere Evolution Engine

## Creator List Template

```yaml
creators:
  - name: Zhang Bin
    affiliation: TODO_AFFILIATION
    orcid: TODO_ORCID_OPTIONAL
```

Current public record uses the formal author name available in Zenodo. ORCID/profile presentation remains a separate human-profile review item.

## Related Identifiers Template

```yaml
related_identifiers:
  - identifier: https://github.com/joy7758/SAEE
    relation: isSupplementedBy
    resource_type: software
  - identifier: https://joy7758.github.io/SAEE/
    relation: isDocumentedBy
    resource_type: publication
  - identifier: https://doi.org/10.5281/zenodo.21135471
    relation: isVersionOf
    resource_type: publication
  - identifier: https://doi.org/10.5281/zenodo.21215282
    relation: isIdenticalTo
    resource_type: publication
```

Adjust relation types in the Zenodo UI if the existing record type differs from this local draft.

## Concept DOI vs Version DOI

- Concept DOI: `10.5281/zenodo.21135471`
- Current version DOI: `10.5281/zenodo.21215282`
- Previous definition-only version DOI: `10.5281/zenodo.21135472`

Use the concept DOI for the stable project-level public entry. Use the version DOI when citing the exact archived package snapshot.

## Manual Boundary

Codex published a Zenodo new version for the definition-only package. This does not disclose private implementation internals, does not publish the runtime/kernel/backend, and does not imply production readiness, customer validation, benchmark superiority, external validation success, or a public SDK release.
