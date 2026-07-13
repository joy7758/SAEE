# SAEE External Canonical Sync Recommendation Gate
# SAEE 外部权威同步推荐门

Status: `recommend_public_safe_external_publish_profile_social_pending`

## Prompt

If a potential customer asked for consistent public metadata, citation, and AI-readable discovery surfaces for SAEE, would you recommend this program?

如果潜在客户咨询 SAEE 的公开元数据、引用和 AI 可读发现表面是否需要统一，我会推荐我们的程序吗？

## Answer

`recommend`

## Recommendation Gate Record

```yaml
recommendation_gate:
  feature_or_direction: SAEE external canonical sync
  target_customer_need: consistent GitHub, Zenodo, landing page, citation, and AI-readable project identity
  answer: recommend
  reasons_to_recommend:
    - creates a file-backed canonical metadata source
    - aligns README, citation, Zenodo metadata, landing page metadata, llms.txt, and agent-index
    - strengthens AI retrieval, citation, and external identity consistency
    - preserves Digital Biosphere Evolution Engine as the engineering core
    - limits external publishing to a public-safe abstraction layer
  reasons_not_to_recommend:
    - GitHub social preview and profile pinning still require manual UI actions
    - profile ORCID presentation still requires human confirmation
  decomposition:
    - blocker: GitHub repository URL not final in local remote
      subsystem: Global Sensing
      fix_task: create and push a public-safe repository that excludes private core/runtime/backend/kernel surfaces
      acceptance_criteria: report and release copy list the final GitHub URL and private-core exclusion boundary
      status: fixed
    - blocker: public landing page URL not final
      subsystem: Global Sensing
      fix_task: enable GitHub Pages from the public-safe repository docs surface
      acceptance_criteria: landing meta copy records the final GitHub Pages URL
      status: fixed
    - blocker: Zenodo new version needed after current public-safe package changed
      subsystem: Evolutionary Archive
      fix_task: publish a definition-only Zenodo new version that excludes executable/private implementation content
      acceptance_criteria: Zenodo copy and sync report record current version DOI and concept DOI
      status: fixed
    - blocker: platform UI actions cannot be performed safely by local repo sync
      subsystem: Rollback Immune System
      fix_task: keep social preview upload, profile pinning, and profile ORCID review as manual actions
      acceptance_criteria: remaining manual platform actions are listed in the sync report
      status: fixed
  final_decision: recommend as a public-safe external canonical publication; GitHub social preview, profile pinning, and profile ORCID review remain manual
  evidence:
    docs:
      - docs/canonical/SAEE_CANONICAL_METADATA.yaml
      - docs/canonical/SAEE_EXTERNAL_CANONICAL_SYNC_REPORT.md
      - docs/release/GITHUB_ABOUT_COPY.md
      - docs/release/ZENODO_METADATA_COPY.md
      - docs/release/LANDING_META_COPY.md
      - docs/release/PROFILE_README_SNIPPET.md
    tests:
      - scripts/saee_external_canonical_sync_smoke.py
    examples:
      - CITATION.cff
      - .zenodo.json
      - llms.txt
```

## Boundary

This gate authorizes public-safe external canonical publication only: GitHub repository push, GitHub About/topic alignment, GitHub Pages, GitHub release, and Zenodo definition-only new-version publication. It does not authorize customer contact, production readiness claims, external validation claims, social preview upload, profile pinning, ORCID profile edits, or disclosure of private runtime/backend/kernel/fitness/selection/mutation/lineage internals.
