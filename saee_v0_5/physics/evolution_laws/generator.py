"""Generate evolution laws from observed lineage dynamics."""

from __future__ import annotations

import hashlib
from typing import Any


def stable_digest(parts: list[str], size: int = 10) -> str:
    payload = "|".join(str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:size]


class EvolutionLawGenerator:
    """Create law records from observations instead of fixed law names."""

    def __init__(self) -> None:
        self.laws: list[dict[str, Any]] = []

    def generate(
        self,
        observation: dict[str, Any],
        dimensions: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        source_terms = self._source_terms(observation, dimensions)
        digest = stable_digest([str(generation_index), *source_terms])
        parent_ids = [law["law_id"] for law in self.laws[-2:]]
        clauses = [
            self._clause(term, position, observation)
            for position, term in enumerate(source_terms[: max(2, min(5, len(source_terms)))])
        ]
        if observation["phase_signal"]["collapse_pressure"] > 0:
            clauses.append(
                {
                    "clause_id": f"clause_regenerate_{digest}",
                    "expression": f"regenerate_when_collapse_pressure_exceeds_{observation['phase_signal']['collapse_pressure']:.2f}",
                    "source": "phase_signal",
                }
            )
        law = {
            "law_id": f"law_g{generation_index:03d}_{digest}",
            "generation_index": generation_index,
            "parents": parent_ids,
            "origin_observation": observation["observation_id"],
            "source_terms": source_terms,
            "clauses": clauses,
            "support": {
                "lineage_branching": observation["population_metrics"]["branching_factor"],
                "novelty_pressure": observation["novelty"]["novelty_score"],
                "survival_pressure": observation["population_metrics"]["active_ratio"],
            },
        }
        self.laws.append(law)
        return law

    def export(self) -> list[dict[str, Any]]:
        return list(self.laws)

    def _source_terms(self, observation: dict[str, Any], dimensions: dict[str, Any]) -> list[str]:
        terms = [
            token
            for token in observation["novelty"]["novel_tokens"]
            if token not in {"", "none"}
        ]
        terms.extend(sorted(dimensions))
        terms.extend(observation["phase_signal"]["dominant_tokens"])
        deduped = []
        for term in terms:
            normalized = "".join(ch if ch.isalnum() else "_" for ch in term.lower()).strip("_")
            if normalized and normalized not in deduped:
                deduped.append(normalized)
        return deduped or ["seed_lineage"]

    def _clause(self, term: str, position: int, observation: dict[str, Any]) -> dict[str, Any]:
        lineage_span = observation["population_metrics"]["lineage_span"]
        novelty = observation["novelty"]["novelty_score"]
        expression_digest = stable_digest([term, str(position), str(lineage_span), f"{novelty:.4f}"], size=8)
        return {
            "clause_id": f"clause_{position}_{expression_digest}",
            "expression": f"if_{term}_cooccurs_with_lineage_span_{lineage_span}_then_amplify_{expression_digest}",
            "source": "lineage_novelty_observation",
        }
