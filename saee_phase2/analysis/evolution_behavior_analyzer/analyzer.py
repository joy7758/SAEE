"""Extract behavior trajectories from observed evolution records."""

from __future__ import annotations

from statistics import mean
from typing import Any


class EvolutionBehaviorAnalyzer:
    """Analyze population trajectories without modifying evolution kernels."""

    def analyze(self, record: dict[str, Any]) -> dict[str, Any]:
        v07_cycles = {
            cycle["generation_index"]: cycle
            for cycle in record.get("v0_7_reflexive_record", {}).get("cycles", [])
        }
        trajectory = []
        motifs: list[dict[str, Any]] = []
        for cycle in record["cycles"]:
            generation = cycle["generation_index"]
            population = cycle.get("population", [])
            active_count = sum(1 for genome in population if genome.get("status") == "active")
            dormant_count = sum(1 for genome in population if genome.get("status") == "dormant")
            identity_scores = [
                float(genome.get("identity_continuity", {}).get("identity_continuity_score", 0.0))
                for genome in population
            ]
            selection_scores = [
                float(genome.get("identity_selection_score", genome.get("selection_score", 0.0)))
                for genome in population
            ]
            v07_cycle = v07_cycles.get(generation, {})
            mutation_events = v07_cycle.get("reflexive_mutation_events", [])
            point = {
                "generation_index": generation,
                "population_count": len(population),
                "active_count": active_count,
                "dormant_count": dormant_count,
                "mean_identity_score": round(mean(identity_scores), 6) if identity_scores else 0.0,
                "mean_selection_score": round(mean(selection_scores), 6) if selection_scores else 0.0,
                "mutation_event_count": len(mutation_events),
                "explanation_driven_mutation_count": sum(
                    1 for event in mutation_events if event.get("event_type") == "explanation_driven_mutation"
                ),
                "semantic_stabilization_count": sum(
                    1 for event in mutation_events if event.get("event_type") == "semantic_stabilization"
                ),
                "semantic_drift_after": cycle["semantic_drift_control"]["drift_after"],
                "identity_break_count": cycle["identity_lineage"]["continuity_break_count"],
                "observer_feedback_bounded": cycle["bounded_observer_loop"]["observer_feedback_bounded"],
            }
            trajectory.append(point)
        if trajectory and all(point["identity_break_count"] == 0 for point in trajectory):
            motifs.append(
                {
                    "motif": "identity_continuity_plateau",
                    "description": "Identity remains continuous while reflexive mutation still occurs.",
                    "support_generations": [point["generation_index"] for point in trajectory],
                }
            )
        if any(point["semantic_stabilization_count"] for point in trajectory):
            motifs.append(
                {
                    "motif": "stabilized_reflexive_variation",
                    "description": "Some explanation feedback stabilizes structures instead of increasing mutation.",
                    "support_generations": [
                        point["generation_index"]
                        for point in trajectory
                        if point["semantic_stabilization_count"]
                    ],
                }
            )
        if trajectory and all(point["observer_feedback_bounded"] for point in trajectory):
            motifs.append(
                {
                    "motif": "bounded_observer_feedback",
                    "description": "Observer feedback stays in the loop but remains identity-bounded.",
                    "support_generations": [point["generation_index"] for point in trajectory],
                }
            )
        return {
            "analysis_type": "evolution_behavior_analysis",
            "source_status": record["status"],
            "generation_count": len(trajectory),
            "trajectory": trajectory,
            "behavioral_motifs": motifs,
            "metrics": {
                "mean_population_count": round(mean(point["population_count"] for point in trajectory), 6) if trajectory else 0.0,
                "mean_identity_score": round(mean(point["mean_identity_score"] for point in trajectory), 6) if trajectory else 0.0,
                "total_explanation_driven_mutations": sum(point["explanation_driven_mutation_count"] for point in trajectory),
                "total_semantic_stabilizations": sum(point["semantic_stabilization_count"] for point in trajectory),
            },
        }

