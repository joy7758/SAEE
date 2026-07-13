"""Generate phase events from structural signatures."""

from __future__ import annotations

import hashlib
from typing import Any


class PhaseEmergenceEngine:
    """Detect irreversible structural transitions without enum regimes."""

    def __init__(self) -> None:
        self.previous_signature: str | None = None
        self.phase_events: list[dict[str, Any]] = []

    def detect(
        self,
        observation: dict[str, Any],
        dimensions: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        active = sorted(key for key, value in dimensions.items() if value.get("state") == "active")
        collapsed = sorted(key for key, value in dimensions.items() if value.get("state") == "collapsed")
        signature_payload = [
            *active,
            *collapsed,
            observation["phase_signal"]["signature"],
            str(observation["population_metrics"]["lineage_span"]),
        ]
        signature = hashlib.sha256("|".join(signature_payload).encode("utf-8")).hexdigest()[:14]
        irreversible = self.previous_signature is not None and signature != self.previous_signature and bool(collapsed or generation_index % 3 == 0)
        transition_id = f"transition_{self.previous_signature or 'seed'}_to_{signature}"
        phase = {
            "phase_id": f"phase_g{generation_index:03d}_{signature}",
            "generation_index": generation_index,
            "structure_signature": signature,
            "previous_signature": self.previous_signature,
            "transition_id": transition_id,
            "irreversible": irreversible,
            "active_dimension_count": len(active),
            "collapsed_dimension_count": len(collapsed),
            "origin_observation": observation["observation_id"],
        }
        self.previous_signature = signature
        self.phase_events.append(phase)
        return phase

    def export(self) -> list[dict[str, Any]]:
        return list(self.phase_events)
