# SAEE Version Unification Table

Status: canonical version equivalence table.

| Layer | Canonical Role | Source Version | Source Files | GSP State Field | Status |
| --- | --- | --- | --- | --- | --- |
| Theory | Formal universe | v1.1 / `saee_v1_theory` | `saee_v1_theory/formal_model.md`, `saee_v1_theory/evolution_laws.md` | `theory_state` | canonical reference |
| Physics | Generated evolution physics | v0.5 | `saee_v0_5/SAEE_V0_5_SYSTEM_SPEC.md` | `engineering_state.physics_layer` | engineering view |
| Observability | Evolution explanation | v0.6 | `saee_v0_6/SAEE_V0_6_SYSTEM_SPEC.md` | `engineering_state.observability_layer` | engineering view |
| Reflexivity | Explanation affects evolution | v0.7 | `saee_v0_7/SAEE_V0_7_SYSTEM_SPEC.md` | `engineering_state.reflexivity_layer` | engineering view |
| Identity stability | Bounded reflexive continuity | v0.8 | `saee_v0_8/SAEE_V0_8_SYSTEM_SPEC.md` | `engineering_state.identity_layer` | engineering view |
| Runtime | Stable local runtime | v1.0 | `saee_v1_0/SAEE_V1_0_SYSTEM_SPEC.md` | `engineering_state.stable_runtime_version` | runtime view |
| Long-horizon experiment | Passive runtime observation | v1.0 experiment | `saee_experiments/LONG_HORIZON_EXPERIMENT_SPEC.md` | `source_layers.experiment_layer` | observation view |
| Empirical alignment | Formal tuple measurement | v1.2 | `saee_v1_2/V1_2_SYSTEM_SPEC.md`, `saee_v1_2/results/demo-run/experiment_summary.json` | `experimental_state` | measured local view |
| Global State Protocol | Single source of truth | GSP 0.1 | `saee_global_state/SAEE_GLOBAL_STATE.json` | all canonical fields | controlling state view |

## Unification Rule

SAEE versions are not separate systems. They are views over one canonical
evolutionary object.

When a version conflicts with another version:

1. preserve the source boundary;
2. map the conflict in `DRIFT_ANALYSIS_REPORT.md`;
3. update `SAEE_GLOBAL_STATE.json`;
4. reject any interpretation that turns local status into external validation.
