"""Identity kernel that anchors reflexive evolution."""

from __future__ import annotations

from typing import Any

from saee_v0_8.identity.identity_anchor import IdentityAnchor
from saee_v0_8.identity.invariant_model import IdentityInvariantModel


class IdentityKernel:
    """Hold invariant identity and score continuity across evolving genomes."""

    def __init__(self, seed_genome: dict[str, Any]) -> None:
        self.invariant_model = IdentityInvariantModel(seed_genome)
        self.anchor = IdentityAnchor(self.invariant_model.export())
        self.identity_events: list[dict[str, Any]] = []

    def snapshot(self, generation_index: int) -> dict[str, Any]:
        invariant = self.invariant_model.export()
        anchor = self.anchor.export()
        snapshot = {
            "identity_kernel_id": "saee_identity_kernel_v0_8",
            "generation_index": generation_index,
            "identity_status": "stable",
            "invariant_model": invariant,
            "identity_anchor": anchor,
            "reference_frame": {
                "project_identity": invariant["project_identity"],
                "theory_identity": invariant["theory_identity"],
                "seed_genome_id": invariant["seed_genome_id"],
                "identity_anchor_hash": anchor["anchor_hash"],
            },
        }
        self.identity_events.append(snapshot)
        return snapshot

    def score_genome(self, genome: dict[str, Any]) -> dict[str, Any]:
        invariant = self.invariant_model.export()
        anchor = self.anchor.export()
        text = self._flatten(genome).lower()
        reference_terms = invariant["reference_terms"]
        matched_terms = [term for term in reference_terms if term in text]
        constraints = genome.get("traits", {}).get("constraints", [])
        constraint_matches = [
            constraint for constraint in invariant["required_constraints"] if constraint in constraints
        ]
        seed_id = invariant["seed_genome_id"]
        lineage_continuity = 1.0 if genome["id"].startswith(seed_id) else 0.55
        term_score = len(matched_terms) / max(1, len(reference_terms))
        constraint_score = len(constraint_matches) / max(1, len(invariant["required_constraints"]))
        score = round(max(0.0, min(1.0, term_score * 0.30 + constraint_score * 0.34 + lineage_continuity * 0.36)), 6)
        return {
            "identity_kernel_id": "saee_identity_kernel_v0_8",
            "identity_anchor_id": anchor["identity_anchor_id"],
            "identity_anchor_hash": anchor["anchor_hash"],
            "genome_id": genome["id"],
            "identity_continuity_score": score,
            "matched_reference_terms": matched_terms,
            "constraint_matches": constraint_matches,
            "lineage_continuity": lineage_continuity,
            "identity_preserved": score >= invariant["minimum_identity_score"],
        }

    def score_terms(self, terms: list[str]) -> dict[str, Any]:
        invariant = self.invariant_model.export()
        normalized = {term.lower() for term in terms}
        reference = set(invariant["reference_terms"])
        overlap = sorted(reference & normalized)
        score = round(len(overlap) / max(1, len(reference)), 6)
        return {
            "reference_overlap": overlap,
            "reference_overlap_score": score,
            "semantic_drift": round(1.0 - score, 6),
        }

    def export(self) -> dict[str, Any]:
        return {
            "kernel": "Identity Kernel",
            "invariant_model": self.invariant_model.export(),
            "identity_anchor": self.anchor.export(),
            "events": self.identity_events,
        }

    def _flatten(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(self._flatten(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._flatten(item) for item in value)
        return str(value)

