# lb120 Supplementary Methods and Provenance

Status: `local_support_not_submitted`

No new experiment was run to create this supplement. It documents how the
values already present in the submitted LBA map to current repository artifacts.

## Submitted artifact

| Field | Value |
|---|---|
| Submission ID | `lb120` |
| Portal state observed | `Accept (Confirmed)` on 2026-07-18 |
| PDF | `paper_alife_lba/build/main.pdf` |
| PDF SHA-256 | `aef09e556b2e91b2374b51371164d887e2db40c39a260b3dac2ef7772d15ece8` |
| PDF pages | `1` |
| Source | `paper_alife_lba/main.tex` |
| Source SHA-256 | `b8206dc7ad6de10f31d82e5cf799b9f786575e45a12993fab1579eb1a00c7979` |

The PDF is ignored by Git under the repository-wide `build/` rule. Its SHA-256
is therefore the frozen local identifier used here.

## Long-horizon v1.0 provenance

| Role | Path | SHA-256 |
|---|---|---|
| Configuration | `saee_experiments/configs/experiment_config.yaml` | `a0346e079140da7766ace9f0104257660ed2d452096491221e1d8c6c883061ee` |
| Seed genome | `kernel/examples/seed_genome.json` | `15664f012eddc416817a1c445c49838bc7f4eb3dec8bf5aa2e22e1583df09ff9` |
| Full trace | `saee_experiments/output/demo-run/evolution_trace.jsonl` | `1f788ad0d8b9550f84b71a05cf28d500bdd4cf0b4e7920961b7488e4f8b66d76` |
| Experiment record | `saee_experiments/output/demo-run/experiment_record.json` | `8ca268c57f5e21fd55328986e352f7008807e6fb43cf9e78a80aea383ddd4c78` |
| Drift report | `saee_experiments/output/demo-run/drift_report.json` | `9b6dd56557e6bdb33a296a9410839f8bce6a4409758d7d427901b72d6f90f7d8` |
| Emergence report | `saee_experiments/output/demo-run/emergence_report.json` | `3b61e08f12209c3fd8a98052025472127170d91fc285fa4b2969f9b331800d3d` |
| Stability report | `saee_experiments/reports/stability_report.json` | `c5a706b96e519012ea1672b700dd245946cfc61b5f8c3252b89c39fcc05f1413` |
| Lineage statistics | `saee_experiments/reports/lineage_statistics.json` | `acd9b12f6a4891ace3df0d8abe15e2ced0baeb3be946fa4d4dd302e1900f6ba4` |

Repository entrypoint:

```text
python3 saee_experiments/bootstrap/experiment_bootstrap.py
```

This is the current documented reproduction entrypoint. The exact command used
for the artifact's original execution is not recorded.

## Phase II provenance

| Role | Path | SHA-256 |
|---|---|---|
| Source v0.8 record | `saee_phase2/output/demo-run/source_v0_8_record.json` | `389592c1df4e7c48ad7a983a63690d2547a6fe3b264eb6bce9b8e4d231462a8b` |
| Phase II summary | `saee_phase2/output/demo-run/phase2_summary.json` | `117905ffa8b800d429060037ad66c9fa6712d7ff119e3491ddda5189295adb55` |
| Attractor map | `saee_phase2/output/demo-run/attractor_map.json` | `8015e8137c0723ee46b62ff9efefed7bfe9bc3d56412c26fc3318b4e0cb5e217` |
| Regime log | `saee_phase2/output/demo-run/regime_transition_log.json` | `4349bebb427d466539e363d77557c21c444ffe69106901a212a1b25fe5e17013` |

Current documented reproduction entrypoint:

```text
python3 saee_phase2/bootstrap/phase2_bootstrap.py \
  --generations 6 \
  --output-dir saee_phase2/output/demo-run
```

The bootstrap default initial population size is `5`; the analyzed trajectory
contains a population count of `6` at each recorded generation. The exact
original command is not recorded and is not reconstructed by assumption.

## Phase-diagram compression provenance

| Role | Path | SHA-256 |
|---|---|---|
| Phase-space manifest | `docs/science/phase_diagram/SAEE_PHASE_SPACE_V1.json` | `5c4eacdf2d875164dd98cede381982801972cf1a949ca0c1fe2606e3f623d0ce` |
| Attractor basin map | `docs/science/phase_diagram/ATTRACTOR_BASIN_MAP.json` | `acd88c9422c97efd0f574a7c4d7c3eba1541e75becf6c2fcfea987d8dcb056bc` |
| Regime transition graph | `docs/science/phase_diagram/REGIME_TRANSITION_GRAPH.json` | `cf51c6ac40908df18de94bc52e303a4be9efcd73a54da63ef5f03213734ee987` |

These files declare `derivation_mode=existing_logs_only` and prohibit new data,
runtime changes, kernel changes, and new mechanisms.

## Provenance fields that remain unknown

The following are not recorded in the current run artifacts and are not filled
with values from the present workstation:

- original execution commit;
- exact original command line;
- original execution date beyond current filesystem metadata;
- numeric random seed (the long-horizon config contains a deterministic-mode
  flag, not a numeric seed);
- original OS and Python version;
- package lock or dependency snapshot;
- original CPU/GPU model.

During documentation hardening, the current repository HEAD was
`f6ac41f4b068377e7778e8c3d83b99bd8382debc`. This is a documentation snapshot,
not evidence that the original run executed at that commit.

## Current reconstruction environment

The workstation observed during this documentation pass reported macOS `26.5.2`
and Python `3.14.5`. These values describe the current inspection environment
only. They are not promoted to original-run provenance.

## Known limitations

- one long-horizon artifact set and one six-generation Phase II artifact set;
- no cross-seed or cross-parameter distribution;
- no formal continuous-state attractor analysis;
- no external validation;
- no comparison benchmark;
- no open-ended-evolution metric implementation;
- no post-submission portal update performed by this package.
