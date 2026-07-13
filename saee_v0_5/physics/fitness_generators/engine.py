"""Self-generate fitness expressions from laws and dimensions."""

from __future__ import annotations

import copy
import hashlib
from typing import Any


def _digest(parts: list[str], size: int = 10) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:size]


class SelfGeneratedFitnessEngine:
    """Generate and apply fitness functions without a fixed score schema."""

    def __init__(self) -> None:
        self.functions: list[dict[str, Any]] = []

    def generate(
        self,
        law: dict[str, Any],
        dimensions: dict[str, Any],
        observation: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        terms = []
        active_dimensions = [item for item in dimensions.values() if item.get("state") != "collapsed"]
        for index, dimension in enumerate(sorted(active_dimensions, key=lambda item: item["dimension_id"])):
            law_match = self._law_match(law, dimension)
            pressure = dimension.get("pressure", 0.0)
            novelty = observation["novelty"]["novelty_score"]
            coefficient = round(0.10 + law_match * 0.35 + pressure * 0.25 + novelty * 0.20 + index * 0.01, 6)
            terms.append(
                {
                    "term_id": f"term_{_digest([law['law_id'], dimension['dimension_id'], str(index)], 8)}",
                    "dimension_id": dimension["dimension_id"],
                    "coefficient": coefficient,
                    "measurement": f"trait_overlap::{dimension['source_token']}",
                }
            )
        if not terms:
            terms.append(
                {
                    "term_id": f"term_seed_{generation_index:03d}",
                    "dimension_id": "generated_seed_dimension",
                    "coefficient": 1.0,
                    "measurement": "lineage_presence::seed",
                }
            )
        function_id = f"fitness_g{generation_index:03d}_{_digest([law['law_id'], *[term['term_id'] for term in terms]])}"
        generated = {
            "fitness_function_id": function_id,
            "generation_index": generation_index,
            "source_law": law["law_id"],
            "origin_observation": observation["observation_id"],
            "expression_terms": terms,
            "normalization": "generated_term_sum",
        }
        self.functions.append(generated)
        return generated

    def score(self, population: list[dict[str, Any]], generated_function: dict[str, Any]) -> list[dict[str, Any]]:
        scored = []
        for genome in population:
            components = []
            for term in generated_function["expression_terms"]:
                value = self._measure(genome, term)
                components.append(
                    {
                        "term_id": term["term_id"],
                        "dimension_id": term["dimension_id"],
                        "coefficient": term["coefficient"],
                        "value": value,
                        "contribution": round(value * term["coefficient"], 6),
                    }
                )
            total_weight = sum(term["coefficient"] for term in generated_function["expression_terms"]) or 1.0
            score = sum(item["contribution"] for item in components) / total_weight
            scored.append(
                {
                    "genome": copy.deepcopy(genome),
                    "generated_fitness": {
                        "fitness_function_id": generated_function["fitness_function_id"],
                        "components": components,
                        "score": round(max(0.0, min(1.0, score)), 6),
                    },
                }
            )
        return scored

    def export(self) -> list[dict[str, Any]]:
        return list(self.functions)

    def _law_match(self, law: dict[str, Any], dimension: dict[str, Any]) -> float:
        source = dimension["source_token"]
        blob = " ".join(law.get("source_terms", []))
        return 1.0 if source in blob else 0.35

    def _measure(self, genome: dict[str, Any], term: dict[str, Any]) -> float:
        measurement = term["measurement"].split("::", 1)[-1]
        traits = genome.get("traits", {})
        scope = " ".join(traits.get("mutation_scope", []) + traits.get("generated_traits", []))
        sensing = " ".join(traits.get("sensing", []))
        niche = str(traits.get("niche_target", ""))
        haystack = f"{scope} {sensing} {niche}".lower()
        if measurement in haystack:
            return 0.90
        token_parts = [part for part in measurement.split("_") if part]
        matches = sum(1 for part in token_parts if part in haystack)
        base = min(0.75, 0.18 + matches * 0.12)
        history_bonus = min(0.20, len(genome.get("mutation_history", [])) * 0.025)
        return round(base + history_bonus, 6)
