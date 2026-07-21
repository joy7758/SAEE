# Publication Boundary

This public repository is a canonical metadata, landing page, citation, and
public abstraction package. It also contains one explicitly approved,
source-bound DBOS Developer Preview evaluation projection.

It excludes:

- private core implementation;
- general SAEE runtime implementation;
- kernel, selection, mutation, private fitness/scoring, and lineage internals;
- production backend implementation;
- local secrets;
- local output artifacts;
- customer data;
- production credentials.

The bounded exception is the exact 19-file public-safe extraction recorded by
Digital Biosphere Architecture `ADR-020`. It may read the synthetic DBOS
Developer Preview envelope, reuse the listed evaluator closure, and return
fail-closed assessments and advisory recommendations. It does not expose the
private evolution core, create a network service, write back to DBOS, grant
authority, verify Evidence Truth, or authorize execution.

Claims intentionally not made:

- external validation success;
- customer validation;
- production readiness;
- public SDK release;
- benchmark superiority;
- universal law proof.
