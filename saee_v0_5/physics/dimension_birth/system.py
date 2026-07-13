"""Generate, merge, and collapse evolution dimensions at runtime."""

from __future__ import annotations

import hashlib
from typing import Any


def _digest(parts: list[str], size: int = 8) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:size]


class EvolutionDimensionBirthSystem:
    """Maintain an unbounded dimension set generated from observations."""

    def __init__(self) -> None:
        self.dimensions: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []

    def update(self, observation: dict[str, Any], generation_index: int) -> dict[str, Any]:
        events: list[dict[str, Any]] = []
        for token in observation["novelty"]["novel_tokens"]:
            if not token:
                continue
            dimension_id = f"dim_{_digest([token, observation['phase_signal']['signature']], 10)}"
            if dimension_id not in self.dimensions:
                self.dimensions[dimension_id] = {
                    "dimension_id": dimension_id,
                    "source_token": token,
                    "born_generation": generation_index,
                    "state": "active",
                    "pressure": observation["novelty"]["novelty_score"],
                    "support": 1,
                    "parents": [],
                }
                events.append(
                    {
                        "event_type": "dimension_birth",
                        "generation_index": generation_index,
                        "dimension_id": dimension_id,
                        "source_token": token,
                    }
                )
            else:
                dimension = self.dimensions[dimension_id]
                dimension["support"] += 1
                dimension["pressure"] = round((dimension["pressure"] + observation["novelty"]["novelty_score"]) / 2, 6)

        merge_event = self._merge_if_needed(generation_index)
        if merge_event:
            events.append(merge_event)
        collapse_events = self._collapse_if_needed(observation, generation_index)
        events.extend(collapse_events)
        self.events.extend(events)
        return {
            "dimensions": self.snapshot(),
            "dimension_events": events,
        }

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {key: dict(value) for key, value in sorted(self.dimensions.items())}

    def export_events(self) -> list[dict[str, Any]]:
        return list(self.events)

    def _merge_if_needed(self, generation_index: int) -> dict[str, Any] | None:
        active = [item for item in self.dimensions.values() if item.get("state") == "active"]
        if len(active) < 4:
            return None
        left, right = sorted(active, key=lambda item: (item["support"], item["dimension_id"]))[:2]
        merged_token = f"{left['source_token']}_{right['source_token']}"
        merged_id = f"dim_{_digest([merged_token, str(generation_index)], 10)}"
        if merged_id in self.dimensions:
            return None
        left["state"] = "merged"
        right["state"] = "merged"
        self.dimensions[merged_id] = {
            "dimension_id": merged_id,
            "source_token": merged_token,
            "born_generation": generation_index,
            "state": "active",
            "pressure": round((left["pressure"] + right["pressure"]) / 2, 6),
            "support": left["support"] + right["support"],
            "parents": [left["dimension_id"], right["dimension_id"]],
        }
        return {
            "event_type": "dimension_merge",
            "generation_index": generation_index,
            "dimension_id": merged_id,
            "parents": [left["dimension_id"], right["dimension_id"]],
        }

    def _collapse_if_needed(self, observation: dict[str, Any], generation_index: int) -> list[dict[str, Any]]:
        if observation["phase_signal"]["collapse_pressure"] <= 0:
            return []
        events = []
        active = [
            dimension
            for dimension in self.dimensions.values()
            if dimension["state"] == "active" and dimension["support"] <= 1
        ]
        for dimension in sorted(active, key=lambda item: (item["support"], item["dimension_id"]))[:2]:
            dimension["state"] = "collapsed"
            events.append(
                {
                    "event_type": "dimension_collapse",
                    "generation_index": generation_index,
                    "dimension_id": dimension["dimension_id"],
                }
            )
        return events
