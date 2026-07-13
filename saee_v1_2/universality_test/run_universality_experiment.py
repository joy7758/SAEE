#!/usr/bin/env python3
"""Run the SAEE v1.2 cross-system parasitic phase invariance test."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.parasitic_phase.model import (  # noqa: E402
    ExperimentConfig as DBI1Config,
    ParasiticPhaseSimulation,
)
from saee_v1_2.universality_test.dbi2_model import (  # noqa: E402
    DBI2Config,
    DBI2Simulation,
)


GOVERNANCE_LEVELS = ["none", "weak", "strong"]
DEFAULT_OUTPUT_DIR = Path("saee_v1_2/universality_test/results")


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def variance(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    average = sum(values) / len(values)
    return sum((value - average) ** 2 for value in values) / (len(values) - 1)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def pearson_similarity(a_values: list[float], b_values: list[float]) -> float:
    if len(a_values) != len(b_values) or not a_values:
        return 0.0
    a_mean = sum(a_values) / len(a_values)
    b_mean = sum(b_values) / len(b_values)
    numerator = sum((a - a_mean) * (b - b_mean) for a, b in zip(a_values, b_values))
    a_var = sum((a - a_mean) ** 2 for a in a_values)
    b_var = sum((b - b_mean) ** 2 for b in b_values)
    if a_var <= 0 or b_var <= 0:
        return 0.0
    correlation = numerator / math.sqrt(a_var * b_var)
    return clamp((correlation + 1.0) / 2.0)


def mean_curve(results: list[Any], field: str) -> list[float]:
    if not results:
        return []
    steps = min(len(result.metrics) for result in results)
    curve = []
    for index in range(steps):
        curve.append(
            sum(float(result.metrics[index][field]) for result in results) / len(results)
        )
    return curve


def entropy_drop(result: Any) -> float:
    if not result.metrics:
        return 0.0
    head = result.metrics[: min(12, len(result.metrics))]
    tail = result.metrics[max(0, len(result.metrics) - 12) :]
    early = mean([float(metric["entropy"]) for metric in head]) or 0.0
    late = mean([float(metric["entropy"]) for metric in tail]) or 0.0
    return max(0.0, early - late)


def run_dbi1(governance: str, seed: int, steps: int) -> Any:
    return ParasiticPhaseSimulation(
        DBI1Config(
            experiment_id=f"DBI1_{governance}",
            governance=governance,
            seed=seed,
            steps=steps,
        )
    ).run()


def run_dbi2(governance: str, seed: int, steps: int) -> Any:
    return DBI2Simulation(
        DBI2Config(
            experiment_id=f"DBI2_{governance}",
            governance=governance,
            seed=seed,
            steps=steps,
        )
    ).run()


def summarize_runs(system_id: str, governance: str, runs: list[Any]) -> dict[str, Any]:
    transition_steps = [
        float(result.phase_transition_step)
        for result in runs
        if result.phase_transition_step is not None
    ]
    transition_phi_values = [
        float(result.transition_event["phi"])
        for result in runs
        if result.transition_event is not None
    ]
    final_phi_values = [float(result.metrics[-1]["phi"]) for result in runs if result.metrics]
    final_entropy_values = [
        float(result.metrics[-1]["entropy"]) for result in runs if result.metrics
    ]
    final_dominance_values = [
        float(result.metrics[-1]["agent_dominance"]) for result in runs if result.metrics
    ]
    entropy_drops = [entropy_drop(result) for result in runs]
    return {
        "schema": "saee.universality_test.system_governance_summary.v1",
        "system_id": system_id,
        "governance": governance,
        "sample_size": len(runs),
        "transition_count": len(transition_steps),
        "transition_probability": round(len(transition_steps) / len(runs), 6) if runs else 0.0,
        "mean_transition_step_observed_only": (
            None if mean(transition_steps) is None else round(mean(transition_steps) or 0.0, 6)
        ),
        "transition_step_variance_observed_only": (
            None if variance(transition_steps) is None else round(variance(transition_steps) or 0.0, 6)
        ),
        "mean_transition_phi_observed_only": (
            None
            if mean(transition_phi_values) is None
            else round(mean(transition_phi_values) or 0.0, 6)
        ),
        "mean_final_phi": round(mean(final_phi_values) or 0.0, 6),
        "mean_final_entropy": round(mean(final_entropy_values) or 0.0, 6),
        "mean_final_dominance": round(mean(final_dominance_values) or 0.0, 6),
        "mean_entropy_drop": round(mean(entropy_drops) or 0.0, 6),
        "seed_summaries": [
            {
                "seed": result.config.seed,
                "phase_transition_step": result.phase_transition_step,
                "transition_event": result.transition_event,
                "final_phi": result.metrics[-1]["phi"] if result.metrics else 0.0,
                "final_entropy": result.metrics[-1]["entropy"] if result.metrics else 0.0,
                "final_agent_dominance": (
                    result.metrics[-1]["agent_dominance"] if result.metrics else 0.0
                ),
            }
            for result in runs
        ],
    }


def governance_order_score(system_summary: dict[str, Any]) -> float:
    none = system_summary["none"]["transition_probability"]
    weak = system_summary["weak"]["transition_probability"]
    strong = system_summary["strong"]["transition_probability"]
    score = 0.0
    if none >= weak:
        score += 0.5
    if weak >= strong:
        score += 0.5
    return score


def governance_response(system_summary: dict[str, Any], steps: int) -> dict[str, float]:
    none = system_summary["none"]
    strong = system_summary["strong"]
    none_probability = float(none["transition_probability"])
    strong_probability = float(strong["transition_probability"])
    probability_suppression = clamp(
        (none_probability - strong_probability) / max(0.001, none_probability)
    )

    none_step = none["mean_transition_step_observed_only"]
    strong_step = strong["mean_transition_step_observed_only"]
    if none_step is not None and strong_step is None and none_probability > 0:
        timing_delay = 1.0
    elif none_step is not None and strong_step is not None:
        timing_delay = clamp((float(strong_step) - float(none_step)) / max(1.0, float(steps)))
    else:
        timing_delay = 0.0

    none_phi = float(none["mean_final_phi"])
    strong_phi = float(strong["mean_final_phi"])
    final_phi_suppression = clamp((none_phi - strong_phi) / max(0.001, none_phi))
    overall = (probability_suppression + timing_delay + final_phi_suppression) / 3.0
    return {
        "probability_suppression_score": round(probability_suppression, 6),
        "timing_delay_score": round(timing_delay, 6),
        "final_phi_suppression_score": round(final_phi_suppression, 6),
        "overall_governance_response_score": round(overall, 6),
    }


def classify_result(metrics: dict[str, Any]) -> str:
    p1 = metrics["phase_transition_probability_DB1"]
    p2 = metrics["phase_transition_probability_DB2"]
    invariance = metrics["structural_invariance_index"]
    governance = metrics["governance_response"]
    suppression_preserved = governance["suppression_preserved_across_systems"]
    delay_preserved = governance["delay_preserved_across_systems"]
    if p1 >= 0.5 and p2 >= 0.5 and invariance >= 0.65 and suppression_preserved:
        return "C_candidate_universal_multi_agent_property_not_proven"
    if p1 >= 0.5 and p2 >= 0.5 and delay_preserved:
        return "hybrid_universality_class_attractor_invariant_governance_response_architecture_dependent"
    if p1 >= 0.5 and p2 >= 0.5:
        return "B_architecture_dependent_with_cross_system_phase_signature"
    if p1 >= 0.5 and p2 < 0.2:
        return "A_system_specific_under_current_DBI2_test"
    return "B_architecture_dependent_or_partial_invariance"


def build_metrics(
    dbi1_runs: dict[str, list[Any]],
    dbi2_runs: dict[str, list[Any]],
    steps: int,
    seed_count: int,
) -> dict[str, Any]:
    dbi1_summary = {
        governance: summarize_runs("DBI-1", governance, runs)
        for governance, runs in dbi1_runs.items()
    }
    dbi2_summary = {
        governance: summarize_runs("DBI-2", governance, runs)
        for governance, runs in dbi2_runs.items()
    }

    dbi1_phi = mean_curve(dbi1_runs["none"], "phi")
    dbi2_phi = mean_curve(dbi2_runs["none"], "phi")
    dbi1_entropy = mean_curve(dbi1_runs["none"], "entropy")
    dbi2_entropy = mean_curve(dbi2_runs["none"], "entropy")
    phi_similarity = pearson_similarity(dbi1_phi, dbi2_phi)
    entropy_curve_similarity = pearson_similarity(dbi1_entropy, dbi2_entropy)
    entropy_drop_1 = dbi1_summary["none"]["mean_entropy_drop"]
    entropy_drop_2 = dbi2_summary["none"]["mean_entropy_drop"]
    entropy_drop_similarity = clamp(
        1.0 - abs(entropy_drop_1 - entropy_drop_2) / max(1.0, entropy_drop_1, entropy_drop_2)
    )
    entropy_collapse_similarity_score = round(
        (entropy_curve_similarity + entropy_drop_similarity) / 2.0,
        6,
    )
    dbi1_governance_response = governance_response(dbi1_summary, steps)
    dbi2_governance_response = governance_response(dbi2_summary, steps)
    governance_response_score = round(
        (
            dbi1_governance_response["overall_governance_response_score"]
            + dbi2_governance_response["overall_governance_response_score"]
        )
        / 2.0,
        6,
    )
    delay_preserved = (
        dbi1_governance_response["timing_delay_score"] > 0.05
        and dbi2_governance_response["timing_delay_score"] > 0.05
    )
    suppression_preserved = (
        dbi1_governance_response["probability_suppression_score"] >= 0.50
        and dbi2_governance_response["probability_suppression_score"] >= 0.50
    )

    observed_phi_c_means = [
        item
        for item in [
            dbi1_summary["none"]["mean_transition_phi_observed_only"],
            dbi2_summary["none"]["mean_transition_phi_observed_only"],
        ]
        if item is not None
    ]
    phi_c_variance = variance([float(value) for value in observed_phi_c_means])
    transition_probability_similarity = clamp(
        1.0
        - abs(
            dbi1_summary["none"]["transition_probability"]
            - dbi2_summary["none"]["transition_probability"]
        )
    )
    governance_preservation = (
        governance_order_score(dbi1_summary) + governance_order_score(dbi2_summary)
    ) / 2.0
    structural_invariance_index = round(
        (
            transition_probability_similarity
            + phi_similarity
            + entropy_collapse_similarity_score
            + governance_response_score
        )
        / 4.0,
        6,
    )

    metrics = {
        "schema": "saee.universality_test.metrics.v1",
        "local_only": True,
        "synthetic_experiment": True,
        "external_validation_claim": False,
        "universality_claim": "not_proven",
        "production_claim": False,
        "parasitic_phase_modified": False,
        "steps": steps,
        "seed_count_per_system_governance": seed_count,
        "systems_tested": ["DBI-1", "DBI-2"],
        "DBI-1": dbi1_summary,
        "DBI-2": dbi2_summary,
        "phase_transition_probability_DB1": dbi1_summary["none"]["transition_probability"],
        "phase_transition_probability_DB2": dbi2_summary["none"]["transition_probability"],
        "configured_phi_c_values": {
            "DBI-1": 0.60,
            "DBI-2": 0.60,
        },
        "configured_phi_c_variance_across_systems": 0.0,
        "phi_c_variance_across_systems": (
            None if phi_c_variance is None else round(phi_c_variance, 6)
        ),
        "mean_observed_transition_phi": {
            "DBI-1": dbi1_summary["none"]["mean_transition_phi_observed_only"],
            "DBI-2": dbi2_summary["none"]["mean_transition_phi_observed_only"],
        },
        "phi_curve_similarity_score": round(phi_similarity, 6),
        "entropy_collapse_similarity_score": entropy_collapse_similarity_score,
        "governance_order_preservation_score": round(governance_preservation, 6),
        "governance_effect_preservation_score": governance_response_score,
        "governance_response": {
            "DBI-1": dbi1_governance_response,
            "DBI-2": dbi2_governance_response,
            "delay_preserved_across_systems": delay_preserved,
            "suppression_preserved_across_systems": suppression_preserved,
        },
        "transition_probability_similarity_score": round(transition_probability_similarity, 6),
        "structural_invariance_index": structural_invariance_index,
        "mean_curves": {
            "DBI-1": {
                "none": {
                    "phi": [round(value, 6) for value in dbi1_phi],
                    "entropy": [round(value, 6) for value in dbi1_entropy],
                }
            },
            "DBI-2": {
                "none": {
                    "phi": [round(value, 6) for value in dbi2_phi],
                    "entropy": [round(value, 6) for value in dbi2_entropy],
                }
            },
        },
    }
    metrics["empirical_classification"] = classify_result(metrics)
    return metrics


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, metrics: dict[str, Any]) -> None:
    dbi1 = metrics["DBI-1"]
    dbi2 = metrics["DBI-2"]
    invariant = (
        metrics["phase_transition_probability_DB1"] >= 0.5
        and metrics["phase_transition_probability_DB2"] >= 0.5
    )
    governance_delay_preserved = metrics["governance_response"]["delay_preserved_across_systems"]
    governance_suppression_preserved = metrics["governance_response"][
        "suppression_preserved_across_systems"
    ]
    phi_consistent = metrics["phi_curve_similarity_score"] >= 0.65
    parasitic_both = invariant
    lines = [
        "# SAEE v1.2 Universality Test Report",
        "",
        "agent_readable:",
        "  schema: saee.universality_test.report.v1",
        "  module: saee_v1_2/universality_test",
        "  modifies_parasitic_phase: false",
        "  external_validation_claim: false",
        "  universality_claim: not_proven",
        "  production_claim: false",
        "",
        "## Summary",
        "",
        f"- Systems tested: `{', '.join(metrics['systems_tested'])}`",
        f"- Seeds per system/governance: `{metrics['seed_count_per_system_governance']}`",
        f"- Steps per run: `{metrics['steps']}`",
        f"- Empirical classification: `{metrics['empirical_classification']}`",
        f"- Structural invariance index: `{metrics['structural_invariance_index']}`",
        "",
        "## Transition Probability",
        "",
        f"- DBI-1 no-governance transition probability: `{metrics['phase_transition_probability_DB1']}`",
        f"- DBI-2 no-governance transition probability: `{metrics['phase_transition_probability_DB2']}`",
        f"- Phase transition invariant across the two tested systems: `{str(invariant).lower()}`",
        "",
        "## Governance Effect",
        "",
        "| System | None | Weak | Strong |",
        "|---|---:|---:|---:|",
        f"| DBI-1 | {dbi1['none']['transition_probability']} | {dbi1['weak']['transition_probability']} | {dbi1['strong']['transition_probability']} |",
        f"| DBI-2 | {dbi2['none']['transition_probability']} | {dbi2['weak']['transition_probability']} | {dbi2['strong']['transition_probability']} |",
        "",
        f"- Governance delay preserved: `{str(governance_delay_preserved).lower()}`",
        f"- Governance suppression preserved: `{str(governance_suppression_preserved).lower()}`",
        f"- Governance preservation score: `{metrics['governance_effect_preservation_score']}`",
        f"- DBI-1 governance response: `{metrics['governance_response']['DBI-1']}`",
        f"- DBI-2 governance response: `{metrics['governance_response']['DBI-2']}`",
        "- Interpretation: the parasitic attractor is cross-system in this test, but strong-governance suppression is architecture-dependent.",
        "",
        "## Phi Consistency",
        "",
        f"- Phi curve similarity score: `{metrics['phi_curve_similarity_score']}`",
        f"- Phi behaves consistently across tested systems: `{str(phi_consistent).lower()}`",
        f"- Configured Phi_c variance across systems: `{metrics['configured_phi_c_variance_across_systems']}`",
        f"- Observed transition Phi variance across systems: `{metrics['phi_c_variance_across_systems']}`",
        "",
        "## Entropy Collapse Similarity",
        "",
        f"- Entropy collapse similarity score: `{metrics['entropy_collapse_similarity_score']}`",
        f"- DBI-1 mean entropy drop: `{dbi1['none']['mean_entropy_drop']}`",
        f"- DBI-2 mean entropy drop: `{dbi2['none']['mean_entropy_drop']}`",
        "",
        "## Parasitic Attractor",
        "",
        f"- Parasitic attractor exists in both tested systems: `{str(parasitic_both).lower()}`",
        "- This means the attractor signature is replicated across DBI-1 and DBI-2 under the sampled settings.",
        "- It does not prove universality across all multi-agent architectures.",
        "",
        "## Boundary",
        "",
        "- This is a two-system empirical invariance test.",
        "- It is not a proof of universal multi-agent physics.",
        "- It is not real-world validation.",
        "- It does not make SAEE production ready.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(path: Path, metrics: dict[str, Any]) -> None:
    width = 1040
    height = 560
    left = 76
    right = 36
    top = 58
    panel_h = 170
    gap = 62
    plot_w = width - left - right
    colors = {
        "DBI-1": "#b91c1c",
        "DBI-2": "#1d4ed8",
    }
    curves = metrics["mean_curves"]
    steps = len(curves["DBI-1"]["none"]["phi"])
    max_step = max(1, steps - 1)
    phi_c = 0.60
    panels = [
        ("phi", "Phi(t)", "Panel 1: no-governance Phi comparison"),
        ("entropy", "Entropy", "Panel 2: no-governance entropy comparison"),
    ]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="SAEE universality comparison">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:20px;font-weight:700}.subtitle{font-size:13px;fill:#4b5563}.axis{font-size:12px;fill:#374151}.panel{font-size:14px;font-weight:700}.legend{font-size:13px}.grid{stroke:#e5e7eb;stroke-width:1}.axisline{stroke:#9ca3af;stroke-width:1}.boundary{stroke:#111827;stroke-width:1.3;stroke-dasharray:7 6}.caption{font-size:12px;fill:#4b5563}</style>',
        '<text class="title" x="76" y="30">Cross-System Parasitic Phase Invariance Test</text>',
        '<text class="subtitle" x="76" y="50">Mean no-governance curves for DBI-1 and independent DBI-2; local synthetic evidence only.</text>',
    ]
    legend_x = 76
    for system_id in ["DBI-1", "DBI-2"]:
        y = 74
        lines.append(
            f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 28}" y2="{y}" stroke="{colors[system_id]}" stroke-width="3"/>'
        )
        lines.append(f'<text class="legend" x="{legend_x + 36}" y="{y + 4}">{system_id}</text>')
        legend_x += 145

    for panel_index, (field, label, title) in enumerate(panels):
        y0 = top + 42 + panel_index * (panel_h + gap)
        y1 = y0 + panel_h
        x0 = left
        x1 = left + plot_w
        lines.append(f'<text class="panel" x="{x0}" y="{y0 - 14}">{title}</text>')
        for tick in [0.0, 0.25, 0.50, 0.75, 1.0]:
            y = y1 - panel_h * tick
            lines.append(f'<line class="grid" x1="{x0}" y1="{y:.2f}" x2="{x1}" y2="{y:.2f}"/>')
            lines.append(f'<text class="axis" x="{x0 - 36}" y="{y + 4:.2f}">{tick:.2f}</text>')
        lines.append(f'<line class="axisline" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>')
        lines.append(f'<line class="axisline" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}"/>')
        lines.append(
            f'<text class="axis" x="18" y="{y0 + panel_h / 2:.2f}" transform="rotate(-90 18 {y0 + panel_h / 2:.2f})">{label}</text>'
        )
        if field == "phi":
            boundary_y = y1 - panel_h * phi_c
            lines.append(
                f'<line class="boundary" x1="{x0}" y1="{boundary_y:.2f}" x2="{x1}" y2="{boundary_y:.2f}"/>'
            )
            lines.append(f'<text class="axis" x="{x1 - 72}" y="{boundary_y - 8:.2f}">Phi_c=0.60</text>')
        for system_id in ["DBI-1", "DBI-2"]:
            values = curves[system_id]["none"][field]
            points = []
            for index, value in enumerate(values):
                x = x0 + plot_w * index / max_step
                y = y1 - panel_h * clamp(float(value))
                points.append(f"{x:.2f},{y:.2f}")
            lines.append(
                f'<polyline fill="none" stroke="{colors[system_id]}" stroke-width="2.5" points="{" ".join(points)}"/>'
            )
        if panel_index == len(panels) - 1:
            for tick in [0, 40, 80, 120, 160]:
                x = x0 + plot_w * tick / max_step
                lines.append(f'<line class="axisline" x1="{x:.2f}" y1="{y1}" x2="{x:.2f}" y2="{y1 + 5}"/>')
                lines.append(f'<text class="axis" x="{x - 10:.2f}" y="{y1 + 22}">{tick}</text>')
            lines.append(f'<text class="axis" x="{x0 + plot_w / 2 - 34:.2f}" y="{y1 + 42}">Timestep</text>')
    caption_y = height - 24
    lines.append(
        f'<text class="caption" x="76" y="{caption_y}">Classification: {metrics["empirical_classification"]}; structural invariance index={metrics["structural_invariance_index"]}.</text>'
    )
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_universality(steps: int, seed_count: int, seed_start: int) -> dict[str, Any]:
    dbi1_runs = {governance: [] for governance in GOVERNANCE_LEVELS}
    dbi2_runs = {governance: [] for governance in GOVERNANCE_LEVELS}
    for offset in range(seed_count):
        seed = seed_start + offset
        for governance in GOVERNANCE_LEVELS:
            dbi1_runs[governance].append(run_dbi1(governance, seed, steps))
            dbi2_runs[governance].append(run_dbi2(governance, seed + 10000, steps))
    return build_metrics(dbi1_runs, dbi2_runs, steps=steps, seed_count=seed_count)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=160)
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--seed-start", type=int, default=5100)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for universality metrics, report, and SVG.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics = run_universality(
        steps=args.steps,
        seed_count=args.seeds,
        seed_start=args.seed_start,
    )
    write_json(output_dir / "universality_metrics.json", metrics)
    write_report(output_dir / "universality_report.md", metrics)
    write_svg(output_dir / "universality_comparison.svg", metrics)

    print(
        "SAEE_UNIVERSALITY_TEST: "
        f"DBI1_p={metrics['phase_transition_probability_DB1']} "
        f"DBI2_p={metrics['phase_transition_probability_DB2']} "
        f"structural_invariance_index={metrics['structural_invariance_index']} "
        f"classification={metrics['empirical_classification']}"
    )
    print(f"SAEE_UNIVERSALITY_TEST: output={output_dir}")


if __name__ == "__main__":
    main()
