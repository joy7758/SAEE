"""Observer loop record after identity boundaries are applied."""

from __future__ import annotations

from typing import Any


class BoundedObserverLoop:
    """Record observer-in-loop events as identity-bounded reflexive inputs."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def record(
        self,
        v0_7_observer_event: dict[str, Any],
        boundary_record: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        record = {
            "generation_index": generation_index,
            "source_observer_event_id": v0_7_observer_event["observation_event_id"],
            "identity_anchor_id": boundary_record["identity_anchor_id"],
            "observer_embedded": v0_7_observer_event["observer_embedded"],
            "observer_feedback_bounded": boundary_record["observer_feedback_bounded"],
            "recursion_depth_limit": boundary_record["maximum_recursion_depth"],
            "status": "bounded_observer_loop_active",
        }
        self.records.append(record)
        return record

    def export(self) -> list[dict[str, Any]]:
        return list(self.records)

