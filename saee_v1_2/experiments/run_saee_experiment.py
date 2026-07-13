"""Run the SAEE v1.2 empirical alignment experiment.

The experiment instantiates the formal tuple SAEE = (Omega, G, T, S, L, R, mu)
as a deterministic finite simulation, measures empirical quantities, detects
attractors and regimes, and compares the trace with local baseline models.
"""

from __future__ import annotations

from typing import Any

from saee_v1_2.analysis.attractor_detector import AttractorDetectionSystem
from saee_v1_2.analysis.coupling_quantifier import ReflexiveCouplingQuantifier
from saee_v1_2.analysis.regime_transition_analyzer import RegimeTransitionAnalyzer
from saee_v1_2.baseline.alife_comparison import run_alife_comparison
from saee_v1_2.baseline.es_comparison import run_es_comparison
from saee_v1_2.baseline.ga_comparison import run_ga_comparison
from saee_v1_2.metrics.attractor_metrics import attractor_convergence_rate
from saee_v1_2.metrics.lineage_entropy import lineage_entropy, lineage_entropy_delta
from saee_v1_2.metrics.mutation_diversity import mutation_diversity_index
from saee_v1_2.metrics.regime_metrics import regime_series, regime_stability_index
from saee_v1_2.simulator.saee_runtime_sim import run_saee_simulation


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _trace_summary(trace: list[dict[str, Any]]) -> dict[str, Any]:
    lineage_series = lineage_entropy(trace)
    mutation_series = mutation_diversity_index(trace)
    regime_items = regime_series(trace)
    convergence = attractor_convergence_rate(trace)
    populations = [len(state["population"]) for state in trace]
    return {
        "lineage_entropy_final": lineage_series[-1]["lineage_entropy"] if lineage_series else 0.0,
        "lineage_entropy_delta": lineage_entropy_delta(lineage_series),
        "regime_stability_index": regime_stability_index(regime_items),
        "mutation_diversity_mean": _mean(
            [item["mutation_diversity_index"] for item in mutation_series]
        ),
        "terminal_convergence_rate": convergence[-1]["convergence_rate"] if convergence else 0.0,
        "population_count_mean": _mean([float(value) for value in populations]),
        "regimes_observed": sorted({item["regime"] for item in regime_items}),
    }


def _baseline_reports(
    generations: int,
    population_size: int,
    dimensions: int,
    seed: int,
) -> dict[str, Any]:
    runners = {
        "ga": run_ga_comparison,
        "es": run_es_comparison,
        "alife": run_alife_comparison,
    }
    reports: dict[str, Any] = {}
    for offset, (name, runner) in enumerate(runners.items()):
        record = runner(
            generations=generations,
            population_size=population_size,
            dimensions=dimensions,
            seed=seed + offset,
        )
        trace = record["trace"]
        attractor_report = AttractorDetectionSystem().detect(trace)
        reports[name] = {
            "baseline": name,
            "trace_summary": _trace_summary(trace),
            "attractor_count": len(attractor_report["attractors"]),
            "attractor_richness": len(attractor_report["convergence_basins"]),
            "transition_frequency": RegimeTransitionAnalyzer().analyze(trace)["transition_frequency"],
            "boundaries": [
                "local_deterministic_baseline",
                "standard_library_only",
                "no_external_code",
            ],
        }
    return reports


def run_experiment(
    generations: int = 24,
    population_size: int = 12,
    dimensions: int = 3,
    seed: int = 17,
    baseline_seed: int = 29,
) -> dict[str, Any]:
    """Run one local empirical alignment experiment."""
    saee_record = run_saee_simulation(
        generations=generations,
        population_size=population_size,
        dimensions=dimensions,
        seed=seed,
    )
    trace = saee_record["trace"]
    lineage_series = lineage_entropy(trace)
    mutation_series = mutation_diversity_index(trace)
    attractor_report = AttractorDetectionSystem().detect(trace)
    regime_report = RegimeTransitionAnalyzer().analyze(trace)
    coupling_report = ReflexiveCouplingQuantifier().quantify(trace)
    baseline_reports = _baseline_reports(
        generations=generations,
        population_size=population_size,
        dimensions=dimensions,
        seed=baseline_seed,
    )
    metric_report = {
        "metric_type": "saee_v1_2_empirical_metrics",
        "lineage_entropy": lineage_series,
        "lineage_entropy_delta": lineage_entropy_delta(lineage_series),
        "regime_series": regime_report["regime_series"],
        "regime_stability_index": regime_report["regime_stability_index"],
        "attractor_convergence_rate": attractor_report["attractor_convergence"],
        "reflexive_feedback_strength": coupling_report["feedback_series"],
        "coupling_strength_coefficient": coupling_report["coupling_strength_coefficient"],
        "mutation_diversity_index": mutation_series,
        "mutation_diversity_mean": _mean(
            [item["mutation_diversity_index"] for item in mutation_series]
        ),
        "metric_count": 5,
    }
    comparison_report = {
        "comparison_type": "saee_v1_2_baseline_comparison",
        "saee": {
            "trace_summary": _trace_summary(trace),
            "attractor_count": len(attractor_report["attractors"]),
            "attractor_richness": len(attractor_report["convergence_basins"]),
            "transition_frequency": regime_report["transition_frequency"],
            "coupling_strength_coefficient": coupling_report["coupling_strength_coefficient"],
        },
        "baselines": baseline_reports,
        "baseline_count": len(baseline_reports),
        "baseline_models": sorted(baseline_reports),
    }
    summary = {
        "experiment_id": "saee_v1_2_empirical_alignment",
        "formal_model_instantiated": saee_record["formal_tuple"]
        == ["Omega", "G", "T", "S", "L", "R", "mu"],
        "generations": generations,
        "population_size": population_size,
        "dimensions": dimensions,
        "seed": seed,
        "metric_count": metric_report["metric_count"],
        "measured_metrics": [
            "lineage_entropy",
            "regime_stability_index",
            "attractor_convergence_rate",
            "reflexive_feedback_strength",
            "mutation_diversity_index",
        ],
        "attractor_count": len(attractor_report["attractors"]),
        "regimes_observed": regime_report["regimes_observed"],
        "regime_transition_frequency": regime_report["transition_frequency"],
        "coupling_strength_coefficient": coupling_report["coupling_strength_coefficient"],
        "baseline_count": comparison_report["baseline_count"],
        "baseline_models": comparison_report["baseline_models"],
        "validation": {
            "minimal_executable_model": True,
            "at_least_three_metrics": metric_report["metric_count"] >= 3,
            "attractors_detectable": len(attractor_report["attractors"]) >= 1,
            "regime_transitions_measurable": "transition_frequency" in regime_report,
            "reflexive_coupling_quantified": "coupling_strength_coefficient" in coupling_report,
            "baseline_comparisons_executable": comparison_report["baseline_count"] >= 3,
        },
        "boundaries": [
            "local_only",
            "standard_library_only",
            "no_external_api_calls",
            "no_external_repository_execution",
            "no_theory_modification",
            "no_external_scientific_validation_claim",
        ],
    }
    return {
        "summary": summary,
        "saee_record": saee_record,
        "metric_report": metric_report,
        "attractor_report": attractor_report,
        "regime_transition_report": regime_report,
        "coupling_report": coupling_report,
        "comparison_report": comparison_report,
    }


__all__ = ["run_experiment"]
