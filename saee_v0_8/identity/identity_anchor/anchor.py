"""Stable identity anchor for SAEE v0.8."""

from __future__ import annotations

import hashlib
from typing import Any


class IdentityAnchor:
    """Create a stable hash anchor from invariant identity fields."""

    def __init__(self, invariant_model: dict[str, Any]) -> None:
        parts = [
            invariant_model["project_identity"],
            invariant_model["theory_identity"],
            invariant_model["seed_genome_id"],
            invariant_model["seed_niche_target"],
            ",".join(invariant_model["required_constraints"]),
            ",".join(invariant_model["reference_terms"]),
        ]
        digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
        self.anchor = {
            "identity_anchor_id": f"identity_anchor_v0_8_{digest}",
            "anchor_hash": digest,
            "anchor_terms": list(invariant_model["reference_terms"]),
            "seed_genome_id": invariant_model["seed_genome_id"],
            "mutation_policy": "identity_core_is_invariant",
        }

    def export(self) -> dict[str, Any]:
        return dict(self.anchor)

