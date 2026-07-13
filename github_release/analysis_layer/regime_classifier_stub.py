"""Public-safe regime classifier stub.

The classifier uses toy proxy values only. It does not expose SAEE private
fitness, selection, mutation, lineage, or runtime implementation.
"""

from __future__ import annotations

from typing import Any


def classify_regime(row: dict[str, Any]) -> str:
    """Classify a toy observation row."""

    diversity = float(row.get("diversity_proxy", 0.0))
    stability = float(row.get("stability_proxy", 0.0))
    if diversity <= 0.35 and stability >= 0.55:
        return "stable_regime"
    if diversity >= 0.8:
        return "exploratory_regime"
    return "transition_regime"


def summarize_regimes(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Count toy regime labels."""

    counts: dict[str, int] = {}
    for row in rows:
        label = classify_regime(row)
        counts[label] = counts.get(label, 0) + 1
    return counts

