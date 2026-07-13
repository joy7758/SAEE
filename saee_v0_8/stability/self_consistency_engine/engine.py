"""Self-consistency checks for identity-stable evolution."""

from __future__ import annotations

import copy
from typing import Any


class SelfConsistencyEngine:
    """Reject local variants that violate identity continuity."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def validate(
        self,
        population: list[dict[str, Any]],
        identity_kernel: Any,
        identity_snapshot: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        invariant = identity_snapshot["invariant_model"]
        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        score_records = []
        for genome in population:
            score = identity_kernel.score_genome(genome)
            score_records.append(score)
            if score["identity_continuity_score"] < invariant["minimum_identity_score"]:
                rejected.append(
                    {
                        "genome_id": genome["id"],
                        "reason": "identity_continuity_below_threshold",
                        "identity_score": score["identity_continuity_score"],
                    }
                )
                continue
            accepted_genome = copy.deepcopy(genome)
            accepted_genome.setdefault("identity_history", [])
            accepted_genome["identity_history"].append(
                {
                    "generation_index": generation_index,
                    "identity_anchor_id": score["identity_anchor_id"],
                    "identity_continuity_score": score["identity_continuity_score"],
                    "identity_preserved": score["identity_preserved"],
                }
            )
            accepted.append(accepted_genome)
        record = {
            "generation_index": generation_index,
            "identity_anchor_id": identity_snapshot["identity_anchor"]["identity_anchor_id"],
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "rejected": rejected,
            "score_records": score_records,
            "identity_break_detected": bool(rejected),
            "status": "consistent" if not rejected else "repaired_by_rejection",
            "accepted_population": accepted,
        }
        self.records.append(record)
        return record

    def export(self) -> list[dict[str, Any]]:
        return list(self.records)

