# Support Contact Bridge Validator Dry Run

support_contact_bridge_validator_dry_run_v0_1: true
status: pass_fixture_only
dry_run_scope: local_tempfile_fixture_validator_compatibility_only
fixture_only: true
combined_input_fixture_used: true
temp_exports_only: true
local_validators_invoked: true
first_owner_validator_validation_status: pass
support_contact_approval_validation_status: pass
support_contact_approval_builder_ready: true
ready_for_evidence_collection: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blockers_closed_by_dry_run: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This fixture-only dry run verifies that the combined bridge input shape can be
split into the two existing local validator inputs and accepted by both
validators. It uses temporary files only.

## Boundary

The dry run does not run an evidence builder, configure or publish a support
contact, send tests, contact customers or vendors, collect evidence, close
blockers, launch product, or claim production readiness.
