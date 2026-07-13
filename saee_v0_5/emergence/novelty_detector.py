"""Detect novelty from local population and abstract signals."""

from __future__ import annotations

import hashlib
from typing import Any


class NoveltyDetector:
    """Produce novelty tokens without external sensing."""

    def __init__(self) -> None:
        self.seen_tokens: set[str] = set()

    def detect(
        self,
        population: list[dict[str, Any]],
        environment: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        tokens = self._tokens(population, environment)
        novel_tokens = [token for token in tokens if token not in self.seen_tokens]
        self.seen_tokens.update(tokens)
        novelty_score = len(novel_tokens) / max(1, len(tokens))
        signature = hashlib.sha256("|".join(tokens).encode("utf-8")).hexdigest()[:12]
        return {
            "novelty_id": f"novelty_g{generation_index:03d}_{signature}",
            "generation_index": generation_index,
            "tokens": tokens,
            "novel_tokens": novel_tokens[:8],
            "novelty_score": round(novelty_score, 6),
        }

    def _tokens(self, population: list[dict[str, Any]], environment: dict[str, Any]) -> list[str]:
        tokens: list[str] = []
        for signal in environment["signal_objects"]:
            tokens.append(self._clean(f"{signal['source']}_{signal['signal']}"))
            for tag in signal.get("tags", []):
                tokens.append(self._clean(tag))
        for genome in population:
            traits = genome.get("traits", {})
            for item in traits.get("mutation_scope", []) + traits.get("generated_traits", []):
                tokens.append(self._clean(item))
            tokens.append(self._clean(str(traits.get("niche_target", ""))))
        return sorted(token for token in dict.fromkeys(tokens) if token)

    def _clean(self, value: str) -> str:
        return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")
