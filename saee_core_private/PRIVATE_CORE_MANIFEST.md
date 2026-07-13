# SAEE Private Core Manifest

Status: private, local-only, do not publish.

## Purpose

This manifest marks the commercial core boundary. It does not contain private
implementation code.

## Private Core Classes

The following implementation areas must remain private and must not be copied
into Zenodo or GitHub disclosure packages:

- `kernel/`
- `fitness_engine/`
- `selection_engine/`
- `lineage_engine/`
- `mutation_engine/`
- `runtime_v1_0/`

Repository-local source references that are protected by this policy include:

- `saee_v1_0/kernel/`
- `saee_v1_0/runtime/`
- any future commercial evolution engine implementation;
- any future proprietary scoring, selection, lineage, mutation, reproduction,
  or runtime orchestration implementation.

## Rules

- No export.
- No Zenodo inclusion.
- No GitHub inclusion.
- No package upload.
- No public release.
- No implementation copying into public stubs.
- No external API publishing workflow.

## Disclosure Rule

Academic layer = knowledge.

GitHub layer = abstraction.

Core layer = intellectual property.

Never mix layers.

