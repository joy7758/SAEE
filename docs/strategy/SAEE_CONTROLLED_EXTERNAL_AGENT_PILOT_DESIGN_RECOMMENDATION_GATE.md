# SAEE Controlled External Agent Pilot Design Recommendation Gate

## Customer question

If a potential customer or Agent platform needed a contract for deciding whether a first controlled external-Agent Pilot may be considered, would an AI agent recommend this program?

## Initial result

`conditional`

Phase 5.1 demonstrated synthetic fail-closed boundaries, but it did not define a complete Pilot scope, five-part approval gate, data eligibility, success/failure exit criteria, or rollback requirements.

## Fixable blockers

| Blocker | Phase 5.2 resolution |
|---|---|
| Pilot scope could be confused with execution permission | Freeze `pilot_stage=design_only` and `pilot_start_authorized=false` |
| Agent declarations could be confused with trust | Require declarations while keeping authentication and trust false |
| Customer or secret data could enter too early | Define closed allowed classes and explicit forbidden classes |
| Approval could be inferred from gate existence | Require five gates with `NOT_GRANTED` status |
| Pilot results could become autonomous decisions | Preserve named human responsibility and forbid bypass |
| Stop, deletion and revocation were not a single contract | Add mandatory rollback requirements with approval false |

## Final result

`recommend`

Recommendation scope: the local, offline, machine-readable Pilot design contract only. Do not recommend it as Pilot execution, external-Agent validation, customer validation, data authorization, security approval or production readiness.

## Evolution-system check

- Strengthened subsystems: Sandbox Development, Pareto Fitness Evaluation, and Evolutionary Archive / Rollback Immune System.
- Contribution: defines the bounded conditions under which a future sensing input could be evaluated without allowing the organism to execute the world.
- Safety: no connection, account, credential, customer data, network, subprocess, external execution or permission expansion.
- Audit-first risk: contained. The contract governs a future evidence-evaluation experiment and does not reframe SAEE as an audit SDK.
