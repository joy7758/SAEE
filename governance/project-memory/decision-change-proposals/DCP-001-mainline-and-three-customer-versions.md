# DCP-001: Mainline And Three Customer Versions

## Status

```text
proposal_status=APPROVED_BY_EXPLICIT_HUMAN_INSTRUCTION
decision_date=2026-07-14
affected_frozen_decisions=F-002;F-004
constitution_amendment=REQUIRED
```

## Human direction

The human project owner explicitly directed that:

- the mainline is the merger of SAEE and Agent Evidence;
- the final SAEE target is three customer-facing versions;
- the secondary task is to use SAEE to supervise and test the merger, which is also a test of SAEE;
- Commander prompts must not lead the project away from the mainline;
- Agents must recommend correction when drift is detected.

## Why the previous wording was insufficient

F-002 previously described `SAEE Evidence → SAEE Evaluation → SAEE Governance`
as only a functional direction and said Governance was not a product. That
wording understated the human-confirmed target: the three names are final
customer-version targets.

F-004 correctly rejected unlimited governance expansion, but it did not make
the primary/secondary task distinction explicit. This allowed a governance or
testing prompt to appear more important than the merger mainline.

## Approved decision change

```text
program_mainline=saee_agent_evidence_integration
program_secondary=saee_supervises_and_tests_integration
secondary_displaces_mainline=false
target_customer_versions=SAEE_Evidence;SAEE_Evaluation;SAEE_Governance
mainline_drift_response=raise_correction_recommendation
```

## Constitution and registry impact

- Amend Constitution v1.1 and its machine contract/schema/smoke.
- Update Agent startup surfaces and the `agent-index.json` Constitution entry.
- Update product architecture as a target-state statement.
- Do not update canonical capability facts; no capability implementation changed.
- Do not promote the current product registry to claim three launched products.

## Claims

- the program mainline and secondary testing lane are now explicit;
- the final customer-version names are explicit;
- future Agents have a fail-visible drift-correction duty.

## Non-claims

- the merger is complete;
- Agent Evidence source or runtime has migrated;
- the three customer versions are currently implemented, registered, customer validated or launched;
- this instruction authorizes staging, commit, push, deployment or external action.

## Staged truth

```text
source_code_migrated=false
runtime_integrated=false
customer_validated=false
product_launched=false
production_ready=false
existing_family_a_staged_snapshot_modified=false
```

The Constitution amendment is kept unstaged above the protected Family A index
snapshot until a new history-reconciliation gate is explicitly authorized.

## Rollback

If the human owner withdraws this decision, create a new DCP and decision-log
entry. Do not silently revert F-002, F-004 or D-005.
