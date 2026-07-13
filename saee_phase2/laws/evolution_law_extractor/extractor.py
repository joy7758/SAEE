"""Extract empirical evolution laws from observed behavior."""

from __future__ import annotations

from typing import Any


class EvolutionLawExtractor:
    """Derive empirical, local-scope behavior laws from analysis outputs."""

    def extract(
        self,
        behavior: dict[str, Any],
        attractors: dict[str, Any],
        regimes: dict[str, Any],
        topology: dict[str, Any],
        drift: dict[str, Any],
        invariants: dict[str, Any],
    ) -> dict[str, Any]:
        laws = []
        invariant_names = {item["invariant"] for item in invariants["invariants"]}
        if "single_identity_anchor" in invariant_names and "bounded_semantic_drift" in invariant_names:
            laws.append(
                {
                    "law_id": "phase2_law_001_identity_bounded_reflexivity",
                    "statement": "In the observed local run, reflexive feedback remains behaviorally active while identity and semantic drift stay bounded.",
                    "evidence": [
                        "single_identity_anchor",
                        "bounded_semantic_drift",
                        "total_explanation_driven_mutations",
                    ],
                    "scope": "local_empirical_observation",
                }
            )
        if attractors["attractors"] and regimes["dominant_regime"] == "stable_regime":
            laws.append(
                {
                    "law_id": "phase2_law_002_stable_attractor_under_identity_kernel",
                    "statement": "Observed generations converge to a stable identity-preserving behavioral attractor.",
                    "evidence": [
                        "attractor_support_count",
                        "dominant_regime == stable_regime",
                    ],
                    "scope": "local_empirical_observation",
                }
            )
        if topology["identity_break_count"] == 0 and topology["branching_density"] >= 0:
            laws.append(
                {
                    "law_id": "phase2_law_003_lineage_continuity_over_branching",
                    "statement": "Observed lineage branching does not require identity continuity breaks.",
                    "evidence": [
                        "identity_break_count == 0",
                        "branching_density",
                    ],
                    "scope": "local_empirical_observation",
                }
            )
        if drift["drift_summary"]["semantic_drift_state"] == "bounded":
            laws.append(
                {
                    "law_id": "phase2_law_004_drift_partitioning",
                    "statement": "Observed structural, semantic, and behavioral drift can be measured separately without modifying evolution.",
                    "evidence": [
                        "structural_drift",
                        "semantic_drift",
                        "behavioral_drift",
                    ],
                    "scope": "local_empirical_observation",
                }
            )
        return {
            "analysis_type": "evolution_law_extraction",
            "laws": laws,
            "law_count": len(laws),
            "non_claims": [
                "not_a_universal_law",
                "not_external_validation",
                "not_kernel_modification",
            ],
        }

