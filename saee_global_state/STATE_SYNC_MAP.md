# SAEE Global State Synchronization Map

Status: local canonical synchronization map.

## Purpose

SAEE-GSP defines SAEE as one system with multiple views. The map below links
the theory layer, engineering layer, empirical layer, lineage layer,
architecture layer, and identity layer into one canonical state.

## State Mapping

| Canonical State | Theory Layer | Engineering Layer | Empirical Layer | GSP Field |
| --- | --- | --- | --- | --- |
| Evolution space | `Omega` phase space | v0.4/v0.5 evolution-space and generated physics views | v1.2 finite simulation space with 3 dimensions | `theory_state.operator_mapping.Omega` |
| Genome space | `G` genome space | v1.0 population genomes; v0.8 identity-scored variants | v1.2 finite numeric genome vectors | `theory_state.operator_mapping.G` |
| Transformation | `T`, mapped to mutation field `M` | v0.5 generated variation, v0.7 reflexive mutation, v1.0 mutate step | v1.2 reflexive transformation operator | `theory_state.operator_mapping.T` |
| Selection | `S` selection pressure field | v0.5 selection evolution, v0.8 identity-aware selection, v1.0 ranked selection | v1.2 reflexive selection field | `theory_state.operator_mapping.S` |
| Lineage | `L` lineage topology | v0.5 hypergraph, v0.6 semantic lineage, v0.7 explanation DAG, v0.8 identity lineage | v1.2 measured DAG with 156 nodes and 144 edges | `lineage_state` |
| Observer/reflexivity | `R`, mapped to `O_t` | v0.6 observer loop, v0.7 observer-in-loop | v1.2 reflexive coupling coefficient 0.091126 | `experimental_state.reflexive_coupling_strength` |
| Population measure | `mu`, mapped to `P_t` | v1.0 population pool | v1.2 normalized population mass over 12 genomes | `experimental_state.population_size` |
| Identity | `I` identity constraint | v0.8 identity kernel and drift controller | boundary-only in v1.2, not directly mutated | `identity_constraint` |
| Layer authority | LCR-REDS as frozen scientific object | SAEE-MP coordination and runtime projection boundaries | experiments are observation-only and non-authoritative | `architecture_state` |
| Paper interpretation | frozen LCR-REDS definition and claim boundary | no runtime authority; documentation-only projection | no new data; interprets existing phase-space and law surfaces | `theory_state.paper_state` |
| ALife paper formatting | same frozen paper-facing object and claim boundary | no runtime authority; LaTeX representation-only projection | no new data; rewrites existing evidence into ALife-style sections | `theory_state.paper_state.alife_format_status` |
| ALife hostile-review repair | same frozen paper-facing object, with venue-compliance and claim-safety repairs | no runtime authority; paper repair only | no new data; repairs wording, definitions, captions, and venue notes | `theory_state.paper_state.alife_hostile_review_repair_status` |
| ALIFE 2026 Late-Breaking Abstract package | same frozen paper-facing object compressed for the currently open LBA route | no runtime authority; two-page presentation-only projection | no new data; compresses existing evidence and records Linklings submission state `lb120` / `Under Evaluation` | `theory_state.paper_state.alife_lba_status` |

## Bidirectional Traceability

Every canonical state has a source and target:

- Theory to engineering: formal symbols map to files under `saee_v0_5/`,
  `saee_v0_6/`, `saee_v0_7/`, `saee_v0_8/`, and `saee_v1_0/`.
- Engineering to experiment: local runtime and prototype views map to
  empirical measurements under `saee_v1_2/results/demo-run/`.
- Experiment to theory: measured lineage entropy, regimes, attractors, and
  reflexive coupling map back to theoretical laws.
- Identity to all layers: `IDENTITY_CONSTRAINT.md` bounds every future layer.
- Architecture to all layers: `FINAL_ARCHITECTURE_SPEC.md` forbids reverse
  dependency from runtime or protocol layers into the frozen scientific object.
- Paper interpretation to theory state: `paper_final/` maps to
  `theory_state.paper_state` and does not create a new canonical theory layer.
- ALife formatting to theory state: `paper_alife/` maps to
  `theory_state.paper_state.alife_format_status` and does not create a new
  canonical theory layer, experiment, or submission state.
- ALife hostile-review repair to theory state: `paper_alife/REVIEW_RESPONSE.md`
  maps to `theory_state.paper_state.alife_hostile_review_repair_status` and
  does not create a new canonical theory layer, experiment, or submission
  state.
- ALIFE 2026 Late-Breaking Abstract package to theory state:
  `paper_alife_lba/` maps to `theory_state.paper_state.alife_lba_status`.
  It does not create a new canonical theory layer, experiment, full-paper
  route, acceptance, publication, DOI, or external validation state. It records
  the LBA portal submission state only: `lb120`, `Under Evaluation`,
  `07/02/26`.

## No Orphan State Rule

A future SAEE artifact is synchronized only if it maps to at least one of:

- theory state;
- engineering state;
- experimental state;
- lineage state;
- architecture state;
- identity constraint;
- global properties.

Artifacts that cannot be mapped are orphan states and must not become canonical
until a mapping is added.
