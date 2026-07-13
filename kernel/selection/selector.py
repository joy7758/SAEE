"""Deterministic selector for SAEE kernel v0.1."""

from __future__ import annotations

from typing import Any


class Selector:
    """Select the best scored genome with stable tie-breaking."""

    def select(self, scored_offspring: list[dict[str, Any]]) -> dict[str, Any]:
        if not scored_offspring:
            raise ValueError("scored_offspring must not be empty")

        return sorted(
            scored_offspring,
            key=lambda item: (
                item["fitness"]["total"],
                item["genome"]["id"],
            ),
            reverse=True,
        )[0]

