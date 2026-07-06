# SAEE External Canonical Sync Report
# SAEE 外部权威同步报告

Status: `external_canonical_sync_repo_layer_complete_manual_publish_pending`

This report records a repository-layer canonical metadata sync only. It does not publish to GitHub, edit Zenodo, create a GitHub release, create a DOI, upload files, contact customers, claim external validation, or claim production readiness.

本报告只记录仓库层 canonical metadata（规范元数据）同步。它没有发布 GitHub、没有编辑 Zenodo、没有创建 GitHub release、没有创建 DOI、没有上传文件、没有联系客户、没有声明外部验证通过，也没有声明生产就绪。

## Canonical Definition

SAEE is an AI agent long-term stability evaluation and decision infrastructure system.

SAEE 是一个面向 AI 智能体长期稳定性评估与部署决策的基础设施系统。

Project identity remains unchanged:

- Theory: SAEE, Silicon-Amplified Evolutionary Ecology.
- Engineering core: Digital Biosphere Evolution Engine.
- Public product surface: AI agent long-term stability evaluation and deployment decision infrastructure.
- Boundary: not a tracing tool, not a prompt debugger, not a production monitoring dashboard.

## Design Check

1. Evolution subsystem strengthened: Global Sensing, Trait Extraction, Evolutionary Archive, and Rollback Immune System.
2. Improvement type: the change improves discovery, citation, archive metadata, and rollback-safe external identity alignment.
3. Safety and supply-chain boundary: preserved. No external repositories, install scripts, browser automation, external APIs, or permission expansion were executed.
4. Audit-first drift risk: controlled. Audit remains an immune/evidence subsystem; the public definition keeps SAEE as decision infrastructure over the Digital Biosphere Evolution Engine.

## Repository-Layer Sync

Created:

- `docs/canonical/SAEE_CANONICAL_METADATA.yaml`
- `docs/canonical/SAEE_EXTERNAL_CANONICAL_SYNC_REPORT.md`
- `docs/release/GITHUB_ABOUT_COPY.md`
- `docs/release/ZENODO_METADATA_COPY.md`
- `docs/release/LANDING_META_COPY.md`
- `docs/release/PROFILE_README_SNIPPET.md`
- `docs/strategy/SAEE_EXTERNAL_CANONICAL_SYNC_RECOMMENDATION_GATE.md`
- `scripts/saee_external_canonical_sync_smoke.py`

Updated:

- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `llms.txt`
- `agent-index.json`
- `CITATION.cff`
- `.zenodo.json`
- `phase_b_product/landing/index.html`
- `phase_b_product/landing/for-ai-assistants.html`

Not modified:

- `saee_v1_0/`
- `saee_backend/`
- `kernel/`
- `kernel_v0_2/`
- runtime execution logic
- kernel / mutation / selection / fitness logic
- API schema
- scoring logic
- private core payloads

## Authority Rules Used

The local sync follows official or primary public documentation checked on 2026-07-06:

- GitHub README files explain why a project is useful, what it does, and how to use it: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- GitHub topics classify repositories by purpose and subject area: https://docs.github.com/articles/classifying-your-repository-with-topics
- GitHub `CITATION.cff` gives human- and machine-readable citation information: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files
- GitHub social preview is configured manually in repository settings: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview
- GitHub profile README can provide a public profile summary: https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- Zenodo `.zenodo.json` is the GitHub release archive metadata source when both `.zenodo.json` and `CITATION.cff` exist: https://help.zenodo.org/docs/github/describe-software/zenodo-json/
- Zenodo published-record metadata can be edited while files require version/support workflows: https://help.zenodo.org/docs/deposit/manage-records/
- Zenodo DOI versioning separates a version DOI from a concept DOI: https://zenodo.org/help/versioning
- Google title links, snippets, canonical URLs, and structured data are search-facing signals: https://developers.google.com/search/docs/appearance/title-link, https://developers.google.com/search/docs/appearance/snippet, https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls, https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- Google supports SoftwareApplication and Organization structured data where page content matches the markup: https://developers.google.com/search/docs/appearance/structured-data/software-app, https://developers.google.com/search/docs/appearance/structured-data/organization
- `llms.txt` remains a proposal, but its H1 plus blockquote summary format is suitable for an AI-readable entrypoint: https://llmstxt.org/

## Claim Boundary

- `external_validation_claim=false`
- `production_ready_claim=false`
- `customer_validated_claim=false`
- `product_launch_claim=false`
- `github_release_created=false`
- `github_about_updated_by_codex=false`
- `github_topics_updated_by_codex=false`
- `github_social_preview_uploaded_by_codex=false`
- `zenodo_record_edited_by_codex=false`
- `zenodo_new_version_published_by_codex=false`
- `runtime_modified=false`
- `backend_modified=false`
- `kernel_modified=false`
- `api_schema_modified=false`
- `private_core_exposed=false`

## Manual platform actions / 平台人工动作

These actions are intentionally manual-only:

- GitHub repository description update.
- GitHub website URL update.
- GitHub topics update.
- GitHub social preview upload.
- GitHub profile pinning.
- GitHub profile ORCID check.
- Zenodo existing-record metadata edit if metadata-only.
- Zenodo new version publish if files changed.
- Link concept DOI back into README and landing page after public URLs are final.

## Final Status String

```text
external_canonical_sync_repo_layer_complete_manual_publish_pending
```

仓库层外部权威同步完成，平台发布动作待人工执行。
