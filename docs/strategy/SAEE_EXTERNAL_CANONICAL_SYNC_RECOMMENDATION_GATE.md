# SAEE External Canonical Sync Recommendation Gate
# SAEE 外部权威同步推荐门

Status: `recommend_repo_layer_only_manual_platform_publish_pending`

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
    - aligns README, citation, Zenodo draft metadata, landing page metadata, llms.txt, and agent-index
    - strengthens AI retrieval, citation, and external identity consistency
    - preserves Digital Biosphere Evolution Engine as the engineering core
    - keeps platform publication actions manual
  reasons_not_to_recommend:
    - public GitHub repository URL is not final in local git remote
    - public landing page URL is not final
    - license, affiliation, ORCID, and Zenodo UI metadata require human confirmation
    - GitHub About, topics, social preview, and profile pinning require manual UI actions
  decomposition:
    - blocker: GitHub repository URL not final in local remote
      subsystem: Global Sensing
      fix_task: use https://github.com/joy7758/SAEE placeholders and require manual replacement after public repository selection
      acceptance_criteria: report and release copy list the placeholder and manual action
      status: deferred
    - blocker: public landing page URL not final
      subsystem: Global Sensing
      fix_task: use self-canonical local HTML and https://joy7758.github.io/SAEE copy until deployment
      acceptance_criteria: landing meta copy records canonical target decision and manual replacement requirement
      status: deferred
    - blocker: Zenodo author, ORCID, access, and license choices need human confirmation
      subsystem: Evolutionary Archive
      fix_task: keep creator/license fields explicit as templates and do not claim Zenodo update
      acceptance_criteria: Zenodo copy and sync report include human-review boundary
      status: deferred
    - blocker: platform UI actions cannot be performed safely by local repo sync
      subsystem: Rollback Immune System
      fix_task: generate GitHub/Zenodo/profile/social copy without performing platform writes
      acceptance_criteria: manual platform actions are listed in the sync report
      status: fixed
  final_decision: recommend as a repository-layer canonical alignment; external platform publication remains manual and pending
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

This gate authorizes only repository-layer metadata alignment. It does not authorize GitHub settings changes, Zenodo record edits, Zenodo new-version publication, release creation, tag creation, deployment, customer contact, production readiness claims, or external validation claims.
