"""SAEE Phase II behavior science runtime.

This runtime observes SAEE evolution records and extracts behavior science
surfaces. It does not modify v0.1-v0.8 kernels, mutation logic, selection
logic, identity kernels, or lineage mechanics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_phase2.analysis.attractor_engine import AttractorDiscoveryEngine
from saee_phase2.analysis.evolution_behavior_analyzer import EvolutionBehaviorAnalyzer
from saee_phase2.analysis.regime_classifier import RegimeClassificationSystem
from saee_phase2.drift.cross_generation_drift_model import CrossGenerationDriftModel
from saee_phase2.laws.evolution_law_extractor import EvolutionLawExtractor
from saee_phase2.laws.invariants import InvariantDetector
from saee_phase2.topology.graph_dynamics import GraphDynamics
from saee_phase2.topology.lineage_topology_mapper import LineageTopologyMapper
from saee_v0_8.runtime.identity_stable_kernel import IdentityStableKernel, load_seed as load_v08_seed


class Phase2BehaviorRuntime:
    """Analyze observed evolution behavior as a local science layer."""

    def __init__(self) -> None:
        self.behavior_analyzer = EvolutionBehaviorAnalyzer()
        self.attractor_engine = AttractorDiscoveryEngine()
        self.regime_classifier = RegimeClassificationSystem()
        self.topology_mapper = LineageTopologyMapper()
        self.graph_dynamics = GraphDynamics()
        self.drift_model = CrossGenerationDriftModel()
        self.invariant_detector = InvariantDetector()
        self.law_extractor = EvolutionLawExtractor()

    def analyze_record(self, record: dict[str, Any]) -> dict[str, Any]:
        behavior = self.behavior_analyzer.analyze(record)
        attractors = self.attractor_engine.discover(behavior, record)
        regimes = self.regime_classifier.classify(behavior, attractors)
        topology = self.topology_mapper.map(record)
        graph_dynamics = self.graph_dynamics.analyze(record)
        drift = self.drift_model.measure(behavior, regimes, topology)
        invariants = self.invariant_detector.detect(record, behavior)
        laws = self.law_extractor.extract(behavior, attractors, regimes, topology, drift, invariants)
        phase2_summary = {
            "generation_count": behavior["generation_count"],
            "attractor_count": len(attractors["attractors"]),
            "dominant_regime": regimes["dominant_regime"],
            "regime_transition_count": len(regimes["transitions"]),
            "lineage_node_count": topology["node_count"],
            "lineage_edge_count": topology["edge_count"],
            "branching_density": topology["branching_density"],
            "semantic_drift_max": drift["drift_summary"]["semantic_drift_max"],
            "behavioral_regime_changes": drift["drift_summary"]["behavioral_regime_changes"],
            "invariant_count": invariants["invariant_count"],
            "law_count": laws["law_count"],
            "evolution_modified": False,
            "analysis_only": True,
        }
        return {
            "phase": "SAEE Phase II",
            "runtime": "Evolution Behavior Science Layer",
            "version": "phase2.0",
            "status": "local_phase2_behavior_science_analysis",
            "source_record_status": record["status"],
            "behavior_analysis": behavior,
            "attractor_map": attractors,
            "regime_classification": regimes,
            "lineage_topology": topology,
            "graph_dynamics": graph_dynamics,
            "cross_generation_drift": drift,
            "invariants": invariants,
            "evolution_laws": laws,
            "phase2_summary": phase2_summary,
            "source_record": record,
            "boundaries": [
                "analysis_only",
                "no_evolution_kernel_modification",
                "no_new_mutation_mechanics",
                "no_new_selection_mechanics",
                "no_architecture_layer_upgrade",
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_external_code_as_genome",
                "no_publication_claim",
                "not_production_science_claim",
                "local_reproducible_analysis_only",
            ],
        }


def load_record(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def generate_v08_observation(seed_path: Path, generations: int, initial_population_size: int) -> dict[str, Any]:
    seed = load_v08_seed(seed_path)
    runtime = IdentityStableKernel(seed, initial_population_size=initial_population_size)
    return runtime.run(generations)


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "phase2_record.json": record,
        "evolution_behavior_report.json": record["behavior_analysis"],
        "attractor_map.json": record["attractor_map"],
        "regime_transition_log.json": record["regime_classification"],
        "lineage_topology_map.json": record["lineage_topology"],
        "graph_dynamics.json": record["graph_dynamics"],
        "cross_generation_drift.json": record["cross_generation_drift"],
        "invariants.json": record["invariants"],
        "evolution_laws.json": record["evolution_laws"],
        "phase2_summary.json": record["phase2_summary"],
        "source_v0_8_record.json": record["source_record"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

