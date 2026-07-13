"""Lineage tracking for SAEE kernel v0.1."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class LineageTracker:
    """Collect and export generation-level lineage events."""

    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    def record(
        self,
        parent: dict[str, Any],
        children: list[dict[str, Any]],
        selected: dict[str, Any],
        scored_offspring: list[dict[str, Any]],
        signals: dict[str, Any],
    ) -> dict[str, Any]:
        event = {
            "time": datetime.now(timezone.utc).isoformat(),
            "event_type": "selection",
            "parent": parent["id"],
            "children": [child["id"] for child in children],
            "selected": selected["id"],
            "signal_source": signals.get("source", "unknown"),
            "scores": [
                {
                    "genome_id": item["genome"]["id"],
                    "fitness": item["fitness"],
                }
                for item in scored_offspring
            ],
        }
        self.history.append(event)
        return event

    def export_json(self) -> str:
        return json.dumps(self.history, indent=2, sort_keys=True)

    def export_file(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.export_json() + "\n", encoding="utf-8")

