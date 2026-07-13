# Strategy Intake Scheduled Automation

## Automation Identity

- automation_id: `saee-strategy-intake-and-peer-signal-collection`
- status: `active`
- cadence: daily local Codex automation
- workspace: `.`

## Purpose

Run the SAEE Strategy Intake scheduled check together with public news / peer
signal collection.

The automation tracks:

- recommendation-test status
- public news themes
- peer and competitor movement
- GitHub and repository ecosystem signals
- user-question language and market pain points
- recommendation-surface drift

## External AI Assistant Test Boundary

The automation must not execute external AI assistant tests.

Allowed:

- check local pending/manual result files
- run local smoke scripts
- import and score manually entered results only after a human records them
- update strategy intake logs as observation surfaces

Forbidden:

- calling external AI assistant APIs
- calling external model APIs
- scraping assistant UIs
- automating browser sessions
- claiming external validation

## Core Runtime Boundary

The automation must not modify:

- SAEE Core Runtime
- backend
- kernel
- API contract or schema
- fitness, selection, mutation, or lineage internals
- private core
- product launch state
- customer-contact state

## Review Rule

Signals collected by this automation may become candidate tasks only through:

```text
Strategy Intake -> Review Gate -> Human-approved Task
```

