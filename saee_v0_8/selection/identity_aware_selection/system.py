"""Identity-aware selection pressure."""

from __future__ import annotations

import copy
from typing import Any


class IdentityAwareSelectionSystem:
    """Preserve identity coherence while retaining reflexive evolution."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def resolve(
        self,
        population: list[dict[str, Any]],
        identity_kernel: Any,
        identity_snapshot: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        scored = []
        for genome in population:
            item = copy.deepcopy(genome)
            identity_score = identity_kernel.score_genome(item)
            reflexive_score = float(item.get("selection_score", 0.45))
            epistemic_score = float(item.get("epistemic_fitness", {}).get("epistemic_score", reflexive_score))
            identity_selection_score = round(
                max(0.0, min(1.0, identity_score["identity_continuity_score"] * 0.44 + epistemic_score * 0.32 + reflexive_score * 0.24)),
                6,
            )
            item["identity_continuity"] = identity_score
            item["identity_selection_score"] = identity_selection_score
            item.setdefault("selection_events", [])
            item["selection_events"].append(
                {
                    "event": "identity_aware_selection",
                    "generation_index": generation_index,
                    "identity_anchor_id": identity_score["identity_anchor_id"],
                    "identity_selection_score": identity_selection_score,
                    "identity_continuity_score": identity_score["identity_continuity_score"],
                }
            )
            scored.append(item)
        ranked = sorted(scored, key=lambda genome: (genome["identity_selection_score"], genome["id"]), reverse=True)
        active_limit = min(14, max(4, len(ranked)))
        retained = ranked[:active_limit]
        suppressed = ranked[active_limit:]
        for genome in retained:
            if genome["identity_continuity"]["identity_preserved"]:
                genome["status"] = "active"
            else:
                genome["status"] = "dormant"
        for genome in suppressed:
            genome["status"] = "dormant"
        output_population = sorted(retained + suppressed[:4], key=lambda genome: genome["id"])
        record = {
            "generation_index": generation_index,
            "identity_anchor_id": identity_snapshot["identity_anchor"]["identity_anchor_id"],
            "retained_count": len(retained),
            "suppressed_count": len(suppressed),
            "minimum_identity_score": identity_snapshot["invariant_model"]["minimum_identity_score"],
            "population": output_population,
            "suppressed_genome_ids": [genome["id"] for genome in suppressed],
            "status": "identity_preserving_selection_applied",
        }
        self.records.append(record)
        return record

    def export(self) -> list[dict[str, Any]]:
        return list(self.records)

