# SAEE Phase II System Spec

Status: local-only evolution behavior science layer.

## Identity

SAEE Phase II is not a v0.x kernel upgrade. It is an observation and analysis
layer over existing local evolution records.

Phase I built local evolution mechanisms. Phase II studies observed behavior:
patterns, attractors, regimes, topology, drift, invariants, and empirical laws.

## Analysis Loop

```text
Observe local v0.8 run record
-> Evolution Behavior Analyzer
-> Attractor Discovery Engine
-> Regime Classification System
-> Lineage Topology Mapper
-> Graph Dynamics
-> Cross-Generation Drift Model
-> Invariant Detector
-> Evolution Law Extractor
-> Behavior science reports
```

## Core Objects

| Object | File | Purpose |
| --- | --- | --- |
| Evolution Behavior Analyzer | `analysis/evolution_behavior_analyzer/analyzer.py` | Extracts population and mutation trajectories. |
| Attractor Discovery Engine | `analysis/attractor_engine/engine.py` | Finds recurring state signatures and convergence basins. |
| Regime Classification System | `analysis/regime_classifier/classifier.py` | Classifies stable, exploratory, chaotic, and collapse regimes. |
| Lineage Topology Mapper | `topology/lineage_topology_mapper/mapper.py` | Measures branching, bottlenecks, and diversity change. |
| Graph Dynamics | `topology/graph_dynamics/dynamics.py` | Measures edge-type and generation-level lineage dynamics. |
| Cross-Generation Drift Model | `drift/cross_generation_drift_model/model.py` | Separates structural, semantic, and behavioral drift. |
| Invariant Detector | `laws/invariants/detector.py` | Detects observed local invariants. |
| Evolution Law Extractor | `laws/evolution_law_extractor/extractor.py` | Produces local empirical evolution laws. |
| Phase II Runtime | `runtime/phase2_behavior_runtime.py` | Runs analysis without modifying evolution. |

## Validation Contract

Phase II is valid only when:

- evolution_modified is false;
- outputs are analysis_only;
- attractor states are identified;
- regimes are classified;
- lineage topology is analyzed;
- behavioral, structural, and semantic drift are measurable;
- empirical laws are extracted with local scope.

## Reproducibility

Run:

```bash
python3 saee_phase2/bootstrap/phase2_bootstrap.py --generations 6 --output-dir saee_phase2/output/demo-run
```

Outputs:

- `phase2_record.json`
- `evolution_behavior_report.json`
- `attractor_map.json`
- `regime_transition_log.json`
- `lineage_topology_map.json`
- `graph_dynamics.json`
- `cross_generation_drift.json`
- `invariants.json`
- `evolution_laws.json`
- `phase2_summary.json`
- `source_v0_8_record.json`

## Boundary

Phase II does not modify v0.1-v0.8 kernels, add new mutation mechanics, add
new selection mechanics, call real APIs, execute external repositories, expand
permissions, or claim external scientific validation.

