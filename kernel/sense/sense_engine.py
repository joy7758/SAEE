"""Mock sensing engine for the SAEE kernel v0.1."""

from __future__ import annotations

from typing import Any

from kernel.config import MOCK_SIGNAL_SOURCE


class SenseEngine:
    """Return deterministic local mock signals without network access."""

    def __init__(self, sources: list[str] | None = None) -> None:
        self.sources = sources or []

    def sense(self) -> dict[str, Any]:
        """Return the v0.1 mock environment signal set."""
        return {
            "source": MOCK_SIGNAL_SOURCE,
            "github_signals": ["repo_growth_pattern", "issue_cluster"],
            "news_signals": ["AI_regulation", "enterprise_adoption"],
            "history_signals": ["past_agent_failures", "framework_cycles"],
            "boundaries": [
                "no_network_access",
                "no_external_repo_execution",
                "mock_signals_only",
            ],
        }

