# Isolated-directory reproduction report

```text
date=2026-07-19
isolated_directory_reproduction=true
fresh_operating_system=false
fresh_virtual_environment=false
dependency_reinstallation=false
cross_platform_validation=false
network_access=false
external_repository_execution=false
result=PASS
```

## Procedure

The following artifacts were copied from the working repository into a new
temporary directory:

- `paper_reconstructability_readiness/experiment/`;
- `saee_backend/services/` and the package initializer;
- the four evidence-adequacy profiles;
- the four allowlisted positive fixtures; and
- the evidence-profile and resource-receipt JSON schemas.

The canonical runner was then executed for five repetitions inside the new
directory, followed by `verify_artifact.py`.

## Observed result

```text
SAEE_RECONSTRUCTABILITY_ADEQUACY_ARTIFACT: PASS
pairs=16/16
cases=32/32
reconstructability_complete=32/32
pairwise_semantic_divergence=16/16
field_complete_false_supports=16
type_and_shape_false_supports=16
decision_aware_false_supports=14
semantic_profile_false_supports=0
deterministic_runs=5/5
canonical_result_sha256=4d101bb8633e4acf6cf4d38c08734afddb47d52c6c8b1748d23f6494c4962f44
boundary_violation_count=0
production_ready=false
results_file_sha256=479de2f2916fcb7fe27c91306a3313d45dafb27b1258c31f21efa7eabd1bdf87
```

## Interpretation boundary

The rehearsal shows that the declared artifact subset runs outside the source
working directory on the same machine and interpreter. It does not establish
portability to another operating system, Python version, dependency version,
hardware architecture, or independently administered environment.
