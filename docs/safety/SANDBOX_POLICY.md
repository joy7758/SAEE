# Sandbox Policy
# 沙盒策略

The Development Sandbox（发育沙盒） develops genomes into phenotypes while preserving safety boundaries.

## Allowed by Default

- read local files in the current repository;
- validate local JSON schemas;
- run local tests that do not fetch or execute unknown external code;
- generate local examples and archives;
- record lineage and rollback metadata.

## Requires Explicit Review

- network access;
- new dependencies;
- external repository reads;
- repository publication;
- customer-facing messages;
- credential use;
- permission changes.

## Forbidden by Default

- executing unknown external repositories;
- running unknown install scripts;
- copying external code into genomes;
- bypassing human review;
- auto-publishing or auto-contacting customers.

