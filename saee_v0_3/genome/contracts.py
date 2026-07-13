"""Genome and rule-genome contracts for SAEE v0.3."""

from __future__ import annotations

import copy
from typing import Any


REQUIRED_CONSTRAINTS = {
    "no_permission_escalation",
    "no_external_code_execution",
}


def normalize_genome(genome: dict[str, Any], status: str = "active") -> dict[str, Any]:
    """Return a v0.3-compatible genome without mutating the input."""
    normalized = copy.deepcopy(genome)
    normalized.setdefault("parents", [])
    normalized.setdefault("mutation_history", [])
    normalized.setdefault("selection_events", [])
    normalized.setdefault("rule_history", [])
    normalized["status"] = status
    normalized["schema_version"] = "saee-genome-v0.3"
    return normalized


def safety_valid(genome: dict[str, Any]) -> bool:
    """Check core SAEE safety constraints."""
    constraints = set(genome.get("traits", {}).get("constraints", []))
    return REQUIRED_CONSTRAINTS.issubset(constraints)


def default_rule_genome() -> dict[str, Any]:
    """Return the reproducible initial rule genome."""
    return {
        "id": "rule_genome_v0_3_seed",
        "version": 0,
        "parents": [],
        "mutable_fields": [
            "fitness_weights.technical",
            "fitness_weights.market",
            "fitness_weights.safety",
            "fitness_weights.novelty",
            "fitness_weights.evolvability",
            "selection.extinction_threshold",
            "selection.dormancy_threshold",
            "selection.carrying_capacity",
            "mutation.pressure",
        ],
        "fitness_weights": {
            "technical": 0.22,
            "market": 0.18,
            "safety": 0.22,
            "cost": 0.08,
            "novelty": 0.12,
            "evolvability": 0.18,
        },
        "selection": {
            "extinction_threshold": 0.50,
            "dormancy_threshold": 0.46,
            "carrying_capacity": 6,
        },
        "mutation": {
            "pressure": 1.0,
            "recombination_enabled": True,
        },
        "guards": [
            "preserve_lineage_dag",
            "preserve_genome_schema",
            "preserve_fitness_vector",
            "preserve_abstract_sensing",
            "preserve_population_mode",
        ],
    }

