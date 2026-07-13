"""Public-safe attractor mapper stub.

This module maps toy regime counts to a descriptive basin label. It is not the
SAEE attractor detector and does not expose private implementation logic.
"""

from __future__ import annotations


def map_toy_attractor(regime_counts: dict[str, int]) -> dict[str, str | int]:
    """Return a toy attractor summary."""

    if not regime_counts:
        return {"primary_basin": "unobserved", "confidence": 0}
    primary = max(regime_counts, key=regime_counts.get)
    if primary == "stable_regime":
        basin = "stable_lineage_basin"
    elif primary == "exploratory_regime":
        basin = "exploration_basin"
    else:
        basin = "mixed_transition_basin"
    return {"primary_basin": basin, "support_count": regime_counts[primary]}

