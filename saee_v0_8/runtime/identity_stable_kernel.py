"""SAEE v0.8 identity-stable reflexive evolution kernel.

Agent-readable loop:
v0.7 reflexive cycle -> Identity Kernel -> Semantic Drift Controller
-> Reflexive Boundary Layer -> Self-Consistency Engine
-> Identity-Aware Selection -> Identity-Preserving Lineage
-> bounded feedback for the next generation.

v0.8 does not add external dynamics. It constrains v0.7 reflexivity so the
system remains the same local SAEE identity across continuous change.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from saee_v0_7.runtime.reflexive_kernel import ReflexiveEvolutionKernel
from saee_v0_8.identity.identity_kernel import IdentityKernel
from saee_v0_8.lineage.identity_preserving_lineage_graph import IdentityPreservingLineageGraph
from saee_v0_8.reflexivity.bounded_observer_loop import BoundedObserverLoop
from saee_v0_8.reflexivity.reflexive_boundary_layer import ReflexiveBoundaryLayer
from saee_v0_8.selection.identity_aware_selection import IdentityAwareSelectionSystem
from saee_v0_8.stability.self_consistency_engine import SelfConsistencyEngine
from saee_v0_8.stability.semantic_drift_controller import SemanticDriftController


class IdentityStableKernel:
    """Run reflexive evolution under a persistent identity kernel."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.reflexive = ReflexiveEvolutionKernel(seed_genome, initial_population_size)
        self.identity_kernel = IdentityKernel(seed_genome)
        self.drift_controller = SemanticDriftController()
        self.boundary = ReflexiveBoundaryLayer()
        self.bounded_observer = BoundedObserverLoop()
        self.consistency = SelfConsistencyEngine()
        self.identity_selection = IdentityAwareSelectionSystem()
        self.lineage = IdentityPreservingLineageGraph()
        self.cycles: list[dict[str, Any]] = []
        self.lineage_records: list[dict[str, Any]] = []

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            self.step()
        return self.record()

    def step(self) -> dict[str, Any]:
        v0_7_cycle = self.reflexive.step()
        generation_index = v0_7_cycle["generation_index"]
        identity_snapshot = self.identity_kernel.snapshot(generation_index)
        drift_record = self.drift_controller.control(
            v0_7_cycle["meaning_feedback_output"],
            identity_snapshot,
            generation_index,
        )
        boundary_record = self.boundary.apply(
            drift_record["bounded_feedback"],
            v0_7_cycle["self_model_output"],
            identity_snapshot,
            generation_index,
        )
        observer_record = self.bounded_observer.record(
            v0_7_cycle["observer_in_loop"],
            boundary_record,
            generation_index,
        )
        consistency_record = self.consistency.validate(
            self.reflexive.physics.population,
            self.identity_kernel,
            identity_snapshot,
            generation_index,
        )
        identity_selection = self.identity_selection.resolve(
            consistency_record["accepted_population"],
            self.identity_kernel,
            identity_snapshot,
            generation_index,
        )
        self.reflexive.physics.population = copy.deepcopy(identity_selection["population"])
        self.reflexive.feedback = copy.deepcopy(boundary_record["bounded_feedback"])
        self.reflexive.self_model.state = copy.deepcopy(boundary_record["bounded_self_model"])
        lineage_record = self.lineage.record(
            self.reflexive.physics.population,
            identity_selection,
            consistency_record,
            identity_snapshot,
            generation_index,
        )
        self.lineage_records.append(lineage_record)
        cycle = {
            "generation_id": f"v08-generation-{generation_index:03d}",
            "generation_index": generation_index,
            "v0_7_generation_id": v0_7_cycle["generation_id"],
            "identity_snapshot": identity_snapshot,
            "semantic_drift_control": {
                key: value
                for key, value in drift_record.items()
                if key != "bounded_feedback"
            },
            "reflexive_boundary": {
                key: value
                for key, value in boundary_record.items()
                if key not in {"bounded_feedback", "bounded_self_model"}
            },
            "bounded_observer_loop": observer_record,
            "self_consistency": {
                key: value
                for key, value in consistency_record.items()
                if key != "accepted_population"
            },
            "identity_aware_selection": {
                key: value
                for key, value in identity_selection.items()
                if key != "population"
            },
            "identity_lineage": lineage_record,
            "bounded_feedback": boundary_record["bounded_feedback"],
            "bounded_self_model": boundary_record["bounded_self_model"],
            "population": self.reflexive.physics.population,
        }
        self.cycles.append(cycle)
        return cycle

    def record(self) -> dict[str, Any]:
        identity_kernel_record = self.identity_kernel.export()
        lineage_graph = self.lineage.export()
        drift_records = self.drift_controller.export()
        consistency_records = self.consistency.export()
        boundary_records = self.boundary.export()
        selection_records = self.identity_selection.export()
        max_drift_after = max((item["drift_after"] for item in drift_records), default=0.0)
        anchor_hashes = {
            cycle["identity_snapshot"]["identity_anchor"]["anchor_hash"]
            for cycle in self.cycles
        }
        continuity_break_count = len(lineage_graph["identity_breaks"])
        self_model_invariant_violations = [
            cycle
            for cycle in self.cycles
            if cycle["bounded_self_model"].get("identity_anchor_id")
            != cycle["identity_snapshot"]["identity_anchor"]["identity_anchor_id"]
        ]
        stability_summary = {
            "generation_count": len(self.cycles),
            "identity_kernel_stable": len(anchor_hashes) == 1,
            "identity_anchor_hash_count": len(anchor_hashes),
            "max_semantic_drift_after": round(max_drift_after, 6),
            "semantic_drift_threshold": identity_kernel_record["invariant_model"]["semantic_drift_threshold"],
            "bounded_drift_intervention_count": sum(1 for item in drift_records if item["intervention_applied"]),
            "self_consistency_check_count": len(consistency_records),
            "consistency_rejection_count": sum(item["rejected_count"] for item in consistency_records),
            "identity_selection_count": len(selection_records),
            "observer_boundary_count": len(boundary_records),
            "bounded_observer_loop_count": len(self.bounded_observer.export()),
            "continuity_break_count": continuity_break_count,
            "self_model_invariant_violation_count": len(self_model_invariant_violations),
            "reflexive_source_generation_count": len(self.reflexive.cycles),
        }
        return {
            "kernel": "SAEE v0.8 Identity-Stable Reflexive Evolution Kernel",
            "version": "0.8.0",
            "status": "local_v0_8_identity_stable_reflexive_evolution",
            "generation_id": f"v08-generation-{len(self.cycles):03d}",
            "cycles": self.cycles,
            "population": self.reflexive.physics.population,
            "identity_kernel": identity_kernel_record,
            "semantic_drift": drift_records,
            "self_consistency": consistency_records,
            "identity_aware_selection": selection_records,
            "bounded_observer_loop": self.bounded_observer.export(),
            "reflexive_boundary": boundary_records,
            "identity_preserving_lineage_graph": lineage_graph,
            "v0_7_reflexive_record": self.reflexive.record(),
            "stability_summary": stability_summary,
            "boundaries": [
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_external_code_as_genome",
                "no_publication_claim",
                "not_production_runtime",
                "not_self_aware_system",
                "not_verified_identity_continuity",
                "not_verified_semantic_causality",
                "local_reproducible_simulation_only",
            ],
        }


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "run_record.json": record,
        "identity_stable_cycles.json": record["cycles"],
        "identity_kernel.json": record["identity_kernel"],
        "semantic_drift.json": record["semantic_drift"],
        "self_consistency.json": record["self_consistency"],
        "identity_aware_selection.json": record["identity_aware_selection"],
        "bounded_observer_loop.json": record["bounded_observer_loop"],
        "reflexive_boundary.json": record["reflexive_boundary"],
        "identity_preserving_lineage_graph.json": record["identity_preserving_lineage_graph"],
        "stability_summary.json": record["stability_summary"],
        "v0_7_reflexive_record.json": record["v0_7_reflexive_record"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

