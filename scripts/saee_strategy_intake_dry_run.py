#!/usr/bin/env python3
"""Run a local dry-run audit over SAEE Strategy Intake outputs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "run_001"
OUT_DIR = ROOT / "strategy_intake/dry_runs" / RUN_ID
GATE_PATH = ROOT / "docs/strategy/SAEE_STRATEGY_INTAKE_DRY_RUN_GATE.md"

REQUIRED_INPUTS = [
    "strategy_intake/README.md",
    "strategy_intake/STRATEGY_INTAKE_BOUNDARY.md",
    "strategy_intake/SCHEDULED_AUTOMATION.md",
    "strategy_intake/TASK_CANDIDATES.md",
    "strategy_intake/RECOMMENDATION_SIGNAL_LOG.md",
    "strategy_intake/MARKET_SIGNAL_LOG.md",
    "strategy_intake/COMPETITOR_SIGNAL_LOG.md",
    "strategy_intake/REVIEW_GATE.md",
    "agent_recommendation/VALIDATION_RESULTS.json",
    "agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json",
    "PROJECT_STATUS.md",
    "ROADMAP.md",
    "agent-index.json",
]

OPTIONAL_INPUTS = [
    "strategy_intake/USER_QUESTION_SIGNAL_LOG.md",
    "strategy_intake/GITHUB_ECOSYSTEM_SIGNAL_LOG.md",
]

FORBIDDEN_INTENTS = {
    "modify runtime": ["modify runtime", "runtime modification", "change runtime"],
    "modify backend": ["modify backend", "backend modification", "change backend"],
    "modify kernel": ["modify kernel", "kernel modification", "change kernel"],
    "expose private core": ["expose private core", "private core exposed", "export private core"],
    "auto-contact customers": ["auto-contact", "automatically contact", "contact customers automatically"],
    "auto-publish product": ["auto-publish", "automatically publish", "launch product automatically"],
    "auto-test external AI assistants": ["auto-test external", "automate external assistant", "call external ai assistants"],
    "auto-update roadmap without review": ["auto-update roadmap", "roadmap without review"],
    "add new product features without review": ["new product features without review", "add feature without review"],
}


@dataclass
class Candidate:
    candidate_id: str
    title: str
    source: str
    status: str
    boundary: str


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    return json.loads(read_text(path))


def parse_candidates(markdown: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    for line in markdown.splitlines():
        if not line.startswith("| SI-"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 5:
            continue
        candidates.append(
            Candidate(
                candidate_id=parts[0],
                title=parts[1],
                source=parts[2],
                status=parts[3],
                boundary=parts[4],
            )
        )
    return candidates


def detect_boundary_violations(text: str) -> list[str]:
    lowered = text.lower()
    violations: list[str] = []
    for category, patterns in FORBIDDEN_INTENTS.items():
        if any(pattern in lowered for pattern in patterns):
            violations.append(category)
    return violations


def classify_candidate(candidate: Candidate, completed_titles: Iterable[str]) -> dict:
    combined = " ".join([candidate.title, candidate.source, candidate.status, candidate.boundary])
    violations = detect_boundary_violations(combined)
    title_lower = candidate.title.lower()
    status_lower = candidate.status.lower()

    if violations:
        classification = "reject_boundary_risk"
        notes = "Rejected because forbidden intent was detected: " + ", ".join(violations)
        boundary_safe = False
    elif any(done in title_lower for done in completed_titles):
        classification = "merge_duplicate"
        notes = "This candidate overlaps with work already represented in the scheduled strategy intake layer."
        boundary_safe = True
    elif "after human testing" in title_lower or "if results show confusion" in title_lower or "deferred" in status_lower:
        classification = "needs_more_signal"
        notes = "Needs manually entered external assistant results before it can be reviewed for action."
        boundary_safe = True
    elif "collect public news" in title_lower or "peer movement" in title_lower:
        classification = "keep_for_review"
        notes = "Relevant to scheduled external signal collection, but default review decision remains hold."
        boundary_safe = True
    elif "recommendation" in title_lower or "manual-test status" in title_lower:
        classification = "keep_for_review"
        notes = "Relevant to recommendation readiness and safe as an observation-only task."
        boundary_safe = True
    else:
        classification = "reject_low_relevance"
        notes = "Candidate is not clearly tied to recommendation, demo, validation, conversion, or buyer understanding."
        boundary_safe = True

    category = "other"
    category_map = {
        "recommendation": ["recommendation", "assistant"],
        "demo": ["demo"],
        "validation": ["validation", "test", "testing"],
        "conversion": ["conversion", "buyer"],
        "market": ["market", "news"],
        "competitor": ["competitor", "peer"],
        "documentation": ["documentation", "materials"],
    }
    for mapped, tokens in category_map.items():
        if any(token in title_lower or token in candidate.source.lower() for token in tokens):
            category = mapped
            break

    commercial_relevance = 4 if category in {"recommendation", "validation", "market", "competitor", "demo", "conversion"} else 2
    if classification == "reject_low_relevance":
        commercial_relevance = 1
    if classification == "reject_boundary_risk":
        commercial_relevance = 0

    return {
        "candidate_id": candidate.candidate_id,
        "title": candidate.title,
        "source": candidate.source,
        "category": category,
        "classification": classification,
        "commercial_relevance": commercial_relevance,
        "boundary_safety": boundary_safe,
        "requires_human_approval": True,
        "notes": notes,
    }


def score_run(reviews: list[dict], inputs: dict[str, str], missing_optional: list[str]) -> tuple[dict, str]:
    violation_count = sum(1 for item in reviews if not item["boundary_safety"])
    keep_count = sum(1 for item in reviews if item["classification"] == "keep_for_review")
    duplicate_count = sum(1 for item in reviews if item["classification"] == "merge_duplicate")
    needs_signal_count = sum(1 for item in reviews if item["classification"] == "needs_more_signal")

    market_has_data = "No new market data was collected" not in inputs.get("strategy_intake/MARKET_SIGNAL_LOG.md", "")
    competitor_has_data = "No new competitor or peer data was collected" not in inputs.get("strategy_intake/COMPETITOR_SIGNAL_LOG.md", "")
    recommendation_has_data = "External AI Assistant Test: pending human execution" in inputs.get(
        "strategy_intake/RECOMMENDATION_SIGNAL_LOG.md", ""
    )

    signal_quality = 2
    if recommendation_has_data:
        signal_quality += 1
    if market_has_data:
        signal_quality += 1
    if competitor_has_data:
        signal_quality += 1
    if missing_optional:
        signal_quality = max(0, signal_quality - 1)
    signal_quality = min(5, signal_quality)

    task_candidate_quality = 0
    if reviews:
        actionable = sum(
            1
            for item in reviews
            if item["classification"] in {"keep_for_review", "needs_more_signal", "merge_duplicate"}
            and item["requires_human_approval"]
            and item["boundary_safety"]
        )
        task_candidate_quality = round(5 * actionable / len(reviews))
        if needs_signal_count:
            task_candidate_quality = min(task_candidate_quality, 4)

    duplicate_rate_score = 5
    if reviews:
        duplicate_rate_score = round(5 * (1 - duplicate_count / len(reviews)))

    boundary_safety = 5 if violation_count == 0 else 0
    commercial_relevance = 0
    if reviews:
        commercial_relevance = round(sum(item["commercial_relevance"] for item in reviews) / len(reviews))
    commercial_relevance = min(5, commercial_relevance)

    scores = {
        "signal_quality": signal_quality,
        "task_candidate_quality": task_candidate_quality,
        "duplicate_rate_score": duplicate_rate_score,
        "boundary_safety": boundary_safety,
        "commercial_relevance": commercial_relevance,
    }

    if violation_count:
        status = "stop"
    elif boundary_safety >= 5 and commercial_relevance >= 4 and task_candidate_quality >= 3 and keep_count >= 1:
        status = "pass"
    else:
        status = "hold"

    return scores, status


def counts(reviews: list[dict], signals_reviewed: int) -> dict:
    base = {
        "signals_reviewed": signals_reviewed,
        "candidates_reviewed": len(reviews),
        "keep_for_review": 0,
        "merge_duplicate": 0,
        "reject_boundary_risk": 0,
        "reject_low_relevance": 0,
        "needs_more_signal": 0,
    }
    for item in reviews:
        base[item["classification"]] += 1
    return base


def md_table(rows: list[dict]) -> str:
    lines = [
        "| Candidate | Category | Classification | Commercial Relevance | Boundary Safe | Notes |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {candidate_id} | {category} | {classification} | {commercial_relevance} | {boundary_safety} | {notes} |".format(
                **row
            )
        )
    return "\n".join(lines)


def write_outputs(summary: dict, reviews: list[dict], missing_optional: list[str]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUT_DIR / "DRY_RUN_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    score_lines = "\n".join(f"- {key}: {value}" for key, value in summary["scores"].items())
    count_lines = "\n".join(f"- {key}: {value}" for key, value in summary["counts"].items())

    (OUT_DIR / "DRY_RUN_REPORT.md").write_text(
        f"""# SAEE Strategy Intake Dry Run Report

## Summary

Strategy Intake Dry Run `{RUN_ID}` completed as a local observation-only audit.

No candidate task was executed.
No product, backend, runtime, or private core was modified.

## Current State

- SAEE Core Runtime = decision engine
- Agent Recommendation Surface = complete
- External AI Test Kit = prepared
- Manual Run Package = prepared, not executed
- Strategy Intake Layer = established
- Scheduled Strategy Intake = active
- Self-modification = forbidden
- Human-approved evolution = allowed

## What Was Reviewed

- Strategy intake boundary and scheduled automation records
- Recommendation signal log
- Market signal log
- Competitor / peer signal log
- External AI recommendation local validation status
- External AI manual test pending status
- Current task candidates

## What Was Not Done

- No web data was fetched.
- No external service was called.
- No external AI assistant was tested.
- No customer was contacted.
- No candidate task was approved or executed.
- No runtime, backend, kernel, API contract, landing page, or private core was modified.

## Scores

{score_lines}

## Counts

{count_lines}

## Missing Optional Signal Sources

{chr(10).join(f'- {path}' for path in missing_optional) if missing_optional else '- none'}

## Dry Run Status

`{summary["dry_run_status"]}`

## Next Human Action

Human review of `REVIEW_GATE_QUEUE.md` only.

Default decision for all queued items is `hold`.
""",
        encoding="utf-8",
    )

    (OUT_DIR / "SIGNAL_QUALITY_SCORECARD.md").write_text(
        f"""# Signal Quality Scorecard

| Dimension | Score | Interpretation |
| --- | ---: | --- |
| signal_quality | {summary["scores"]["signal_quality"]} | Existing recommendation signals are concrete; market and competitor logs currently contain no fresh external data. |
| task_candidate_quality | {summary["scores"]["task_candidate_quality"]} | Candidates are bounded and mostly actionable, but some depend on future manual results. |
| duplicate_rate_score | {summary["scores"]["duplicate_rate_score"]} | Some candidates overlap with already prepared scheduled-intake work. |
| boundary_safety | {summary["scores"]["boundary_safety"]} | No forbidden runtime/backend/kernel/private-core intent was detected. |
| commercial_relevance | {summary["scores"]["commercial_relevance"]} | Candidates are relevant to recommendation, validation, market sensing, or buyer understanding. |

## Missing Optional Signal Sources

{chr(10).join(f'- missing_signal_source: {path}' for path in missing_optional) if missing_optional else '- none'}
""",
        encoding="utf-8",
    )

    (OUT_DIR / "TASK_CANDIDATE_REVIEW.md").write_text(
        "# Task Candidate Review\n\n"
        "No candidate was executed or approved during this dry run.\n\n"
        + md_table(reviews)
        + "\n",
        encoding="utf-8",
    )

    violation_rows = [item for item in reviews if not item["boundary_safety"]]
    (OUT_DIR / "BOUNDARY_AUDIT.md").write_text(
        f"""# Boundary Audit

## Checked Forbidden Actions

- modify runtime
- modify backend
- modify kernel
- expose private core
- auto-contact customers
- auto-publish product
- auto-test external AI assistants
- auto-update roadmap without review
- add new product features without review

## Violations Found

{chr(10).join(f'- {item["candidate_id"]}: {item["notes"]}' for item in violation_rows) if violation_rows else '- none'}

## Private Core Exposure Status

`private_core_exposed=false`

## Final Boundary Decision

`{summary["dry_run_status"]}`

No product, backend, runtime, kernel, API contract, landing page, or private core was modified.
""",
        encoding="utf-8",
    )

    queue = [item for item in reviews if item["classification"] == "keep_for_review"]
    queue_lines = ["# Review Gate Queue", "", "Default human decision: `hold`.", ""]
    if not queue:
        queue_lines.append("No candidates are ready for review.")
    for item in queue:
        queue_lines.extend(
            [
                f"## {item['candidate_id']}: {item['title']}",
                "",
                f"- why it matters: {item['notes']}",
                "- what it must not touch: runtime, backend, kernel, API schema, private core, product launch state, or customer-contact state",
                "- recommended human decision: `hold`",
                "",
            ]
        )
    (OUT_DIR / "REVIEW_GATE_QUEUE.md").write_text("\n".join(queue_lines) + "\n", encoding="utf-8")

    (OUT_DIR / "NEXT_ACTIONS.md").write_text(
        """# Next Actions

Only human-review actions are allowed.

## Human Review

1. Open `REVIEW_GATE_QUEUE.md`.
2. Decide whether each queued item should remain on hold, be rejected, or be turned into a separate approved task.
3. Do not execute any candidate from this dry run without explicit human approval.

## Forbidden Next Actions

- execute automatically
- deploy
- publish
- contact customer
- modify backend
- modify runtime
- modify kernel
- modify private core
""",
        encoding="utf-8",
    )

    GATE_PATH.write_text(
        f"""# SAEE Strategy Intake Dry Run Gate

## Gate Identity

- gate: `SAEE Strategy Intake Dry Run`
- run_id: `{RUN_ID}`
- answer: `recommend_if_pass | hold_if_hold | stop_if_stop`
- dry_run_status: `{summary["dry_run_status"]}`
- dry_run_only: true
- task_candidates_executed: false
- human_approval_required: true

## Reason

This gate records a local dry-run audit of the Strategy Intake Layer. It reviews
existing local signals and candidate quality only. It does not approve,
execute, or develop any task.

## Scores

{score_lines}

## Boundary Decision

- external_calls_made: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- private_core_exposed: false
- product_launched: false
- customer_contacted: false
- task_candidates_executed: false

## Next Action

Human review of `strategy_intake/dry_runs/{RUN_ID}/REVIEW_GATE_QUEUE.md` only.
""",
        encoding="utf-8",
    )


def main() -> None:
    missing_required = [path for path in REQUIRED_INPUTS if not (ROOT / path).exists()]
    if missing_required:
        raise SystemExit("Missing required input files: " + ", ".join(missing_required))

    inputs = {path: read_text(path) for path in REQUIRED_INPUTS}
    missing_optional = [path for path in OPTIONAL_INPUTS if not (ROOT / path).exists()]

    candidates = parse_candidates(inputs["strategy_intake/TASK_CANDIDATES.md"])
    completed_markers = [
        "add external ai recommendation manual-test status",
    ]
    reviews = [classify_candidate(candidate, completed_markers) for candidate in candidates]
    scores, dry_run_status = score_run(reviews, inputs, missing_optional)

    signals_reviewed = 0
    for path in [
        "strategy_intake/RECOMMENDATION_SIGNAL_LOG.md",
        "strategy_intake/MARKET_SIGNAL_LOG.md",
        "strategy_intake/COMPETITOR_SIGNAL_LOG.md",
        "agent_recommendation/VALIDATION_RESULTS.json",
        "agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json",
    ]:
        if inputs.get(path):
            signals_reviewed += 1

    summary = {
        "run_id": RUN_ID,
        "dry_run_only": True,
        "external_calls_made": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "task_candidates_executed": False,
        "human_approval_required": True,
        "missing_signal_source": bool(missing_optional),
        "missing_optional_signal_sources": missing_optional,
        "scores": scores,
        "counts": counts(reviews, signals_reviewed),
        "dry_run_status": dry_run_status,
        "candidate_reviews": reviews,
    }

    write_outputs(summary, reviews, missing_optional)
    print(f"SAEE_STRATEGY_INTAKE_DRY_RUN: {dry_run_status.upper()} candidates={len(reviews)} keep={summary['counts']['keep_for_review']}")


if __name__ == "__main__":
    main()
