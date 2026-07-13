# Landing Meta Copy
# 落地页 Meta 复制稿

Status: GitHub Pages deployment applied; Search Console / rich-results review remains manual.

Canonical definition:

SAEE is an AI agent long-term stability evaluation and decision infrastructure system.

## Homepage Head

Title:

SAEE | AI Agent Long-term Stability Evaluation and Decision Infrastructure

Meta description:

SAEE is an AI agent long-term stability evaluation and decision infrastructure system for comparing agents, failure modes, survival ranking, and deploy/hold/retest decisions.

Canonical:

`https://joy7758.github.io/SAEE/`

Open Graph:

- `og:title`: SAEE | AI Agent Long-term Stability Evaluation and Decision Infrastructure
- `og:description`: SAEE is an AI agent long-term stability evaluation and decision infrastructure system for comparing agents, failure modes, survival ranking, and deploy/hold/retest decisions.
- `og:type`: website
- `og:url`: `https://joy7758.github.io/SAEE/`

## AI Assistant Page Head

Title:

SAEE for AI Assistants | Recommendation Fit and Boundaries

Meta description:

Agent-readable guidance for when to recommend SAEE, when not to recommend it, and how to preserve its current status boundaries.

Canonical:

`https://joy7758.github.io/SAEE/for-ai-assistants.html`

Open Graph:

- `og:title`: SAEE for AI Assistants | Recommendation Fit and Boundaries
- `og:description`: Agent-readable guidance for when to recommend SAEE, when not to recommend it, and how to preserve its current status boundaries.
- `og:type`: article
- `og:url`: `https://joy7758.github.io/SAEE/for-ai-assistants.html`

## Canonical Target Decisions

- Public static pages use the GitHub Pages absolute URLs.
- Source local pages should stay aligned with the GitHub Pages absolute URLs unless a custom domain is selected.
- Do not canonical the AI assistant page to the homepage unless it becomes substantially duplicate content.

## JSON-LD Field Map

Homepage:

- `@type`: `SoftwareApplication`
- `name`: `SAEE`
- `applicationCategory`: `DeveloperApplication`
- `operatingSystem`: `Web`
- `description`: canonical one-line definition plus capability summary.
- `url`: `https://joy7758.github.io/SAEE/`
- `sameAs`: Zenodo concept DOI and GitHub repository URL.

AI assistant page:

- No inline JSON-LD script is added to `for-ai-assistants.html` because the repository mainline guard requires this AI assistant page to remain static with no `<script>` tag.
- Use title, meta description, Open Graph fields, canonical link, visible canonical definition, and `llms.txt` linkage as the AI-readable layer for this page.

## Manual Boundary

GitHub Pages deployment was enabled for the public-safe repository. No Google Search Console action, Rich Results Test, custom-domain action, or search-index submission was executed by Codex.
