# SAEE Letter Supplement

This supplement contains the existing report surfaces used by the manuscript
and a SHA-256 manifest. It does not contain a new experiment or a reconstructed
claim about the original execution environment.

## Evidence surfaces

- `experiment_config.yaml`: declared 100-generation experiment configuration.
- `seed_genome.json`: declared seed genome.
- `stability_report.json`: 100-generation fitness and collapse summary.
- `lineage_statistics.json`: lineage counts and endpoint-integrity result.
- `lineage_plot_projection.json`: compact node/edge plotting coordinates derived
  from the frozen experiment record and bound to its SHA-256 digest.
- `drift_report.json`: mutation accumulation and population turnover.
- `cross_generation_drift.json`: six-generation Phase II drift surface.
- `attractor_map.json`: discrete signature recurrence surface.
- `regime_transition_log.json`: local regime classifications.
- `generate_figures.py`: plotting projection used for the manuscript.
- `SHA256SUMS`: file fingerprints.

## Limits

- The exact original command, original execution commit, numeric random seed,
  operating system, Python version, and dependency lock are not recorded.
- The 23 MB local experiment record is not bundled. The compact lineage plotting
  projection preserves only the coordinates and survivor grouping needed to
  reproduce the submitted figure; it is not a substitute for the full record.
- `deterministic_seed=enabled` is a mode flag, not a numeric seed.
- The two evidence surfaces describe different runtime records.
- The supplement does not establish open-ended evolution, mathematical
  attractor existence, cross-run robustness, or external validation.
