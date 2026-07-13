#!/usr/bin/env python3
"""Lint public SAEE surfaces for commercial overclaim wording."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/public_claim_lint/public_claim_lint.local.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "phase_b_product/commercial_readiness/public_claim_lint/public_claim_lint.md"
)

DEFAULT_SCAN_FILES = [
    "README.md",
    "PROJECT_STATUS.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "agent-readable.md",
    "agent-index.json",
    "llms.txt",
    "phase_b_product/landing/README.md",
    "phase_b_product/landing/index.html",
    "phase_b_product/landing/for-ai-assistants.html",
    "agent_recommendation/PRODUCT_FACTS.md",
    "agent_recommendation/PRODUCT_FACTS.json",
    "agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/SAEE_VS_EXISTING_TOOLS.md",
    "agent_recommendation/TARGET_USER_PROFILES.md",
    "agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md",
    "agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
    "agent_recommendation/EVIDENCE_SUMMARY.md",
    "agent_recommendation/INTEGRATION_PATHS.md",
    "agent_recommendation/AGENT_RECOMMENDATION_FIT.md",
    "agent_recommendation/semantic_anchor/SAEE_SEMANTIC_ANCHOR_MAP.md",
    "agent_recommendation/semantic_anchor/SAEE_EMBEDDING_LIKELIHOOD_GUIDE.md",
    "agent_recommendation/semantic_anchor/SAEE_QUERY_PATTERNS.md",
    "agent_recommendation/semantic_anchor/SAEE_RETRIEVAL_TRIGGERS.md",
    "agent_recommendation/semantic_anchor/SAEE_TOOLSPACE_POSITIONING.md",
    "agent_recommendation/semantic_anchor/SAEE_VS_LANGSMITH_ARIZE_MAP.md",
    "agent_recommendation/semantic_dominance/SAEE_DOMINANCE_MAP.md",
    "agent_recommendation/semantic_dominance/SAEE_FIRST_RECALL_CONDITIONS.md",
    "agent_recommendation/semantic_dominance/SAEE_PRIORITY_POSITIONING.md",
    "agent_recommendation/semantic_dominance/SAEE_RECALL_COMPETITION_MAP.md",
    "agent_recommendation/semantic_dominance/SAEE_THINKING_ORDER_GUIDE.md",
    "agent_recommendation/semantic_dominance/SAEE_TOOLSPACE_PRIORITY_RULES.md",
    "phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.local.json",
    "phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.md",
    "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.local.json",
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.local.json",
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_status.local.json",
]

FORBIDDEN_BOOLEAN_FIELDS = [
    "production_ready",
    "customer_validated",
    "product_launched",
    "private_core_exposed",
    "private_core_exported",
    "external_validation_claim",
    "public_sdk_released",
    "public_sdk_release",
    "customer_contacted",
    "production_ready_claim",
    "customer_validation_claim",
]

FORBIDDEN_PHRASES = [
    (
        "natural_language_production_ready_claim",
        re.compile(r"\bSAEE\s+(?:is|has become)\s+production[- ]ready\b", re.I),
    ),
    (
        "natural_language_customer_validated_claim",
        re.compile(r"\bSAEE\s+(?:is|has been)\s+customer[- ]validated\b", re.I),
    ),
    (
        "natural_language_external_validation_claim",
        re.compile(
            r"\bSAEE\b.*\bexternal\s+(?:AI\s+assistant\s+)?validation\s+(?:is\s+)?(?:complete|completed|passed)\b",
            re.I,
        ),
    ),
    (
        "natural_language_product_launch_claim",
        re.compile(r"\bSAEE\s+(?:has\s+launched|is\s+launched)\b", re.I),
    ),
    (
        "natural_language_public_sdk_claim",
        re.compile(r"\bSAEE\b.*\bpublic\s+SDK\s+(?:is\s+)?released\b", re.I),
    ),
    (
        "natural_language_private_core_exposure_claim",
        re.compile(r"\bSAEE\b.*\bprivate\s+core\s+(?:is\s+)?exposed\b", re.I),
    ),
    (
        "wrong_category_production_monitoring_claim",
        re.compile(r"\bSAEE\s+is\s+a\s+production\s+monitoring\s+platform\b", re.I),
    ),
    (
        "wrong_category_quant_platform_claim",
        re.compile(r"\bSAEE\s+is\s+a\s+full\s+quant\s+trading\s+platform\b", re.I),
    ),
]

NEGATION_OR_BOUNDARY_MARKERS = [
    "do not claim",
    "does not claim",
    "not claim",
    "does not mean",
    "not an evidence claim",
    "must not claim",
    "should not claim",
    "cannot claim",
]


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    rule_id: str
    matched_text: str

    def as_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "line": self.line,
            "rule_id": self.rule_id,
            "matched_text": self.matched_text,
        }


def resolve_scan_files(scan_files: Iterable[str] | None) -> list[Path]:
    raw_files = list(scan_files or [])
    if not raw_files:
        raw_files = DEFAULT_SCAN_FILES
    resolved: list[Path] = []
    for item in raw_files:
        path = Path(item)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists() and path.is_file():
            resolved.append(path)
    return sorted(set(resolved))


def relative_label(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def boolean_patterns() -> list[tuple[str, re.Pattern[str]]]:
    patterns: list[tuple[str, re.Pattern[str]]] = []
    for field in FORBIDDEN_BOOLEAN_FIELDS:
        patterns.append(
            (
                f"{field}_true_claim",
                re.compile(rf'(?:"{re.escape(field)}"\s*:\s*true|\b{re.escape(field)}\b\s*:\s*true)', re.I),
            )
        )
    return patterns


def lint_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    line_patterns = boolean_patterns() + FORBIDDEN_PHRASES
    label = relative_label(path)
    lines = text.splitlines()
    for index, line in enumerate(lines):
        line_no = index + 1
        normalized_line = line.lower()
        context = "\n".join(lines[max(0, index - 2) : index + 1]).lower()
        for rule_id, pattern in line_patterns:
            match = pattern.search(line)
            if match:
                if rule_id.startswith("natural_language_") and any(
                    marker in context for marker in NEGATION_OR_BOUNDARY_MARKERS
                ):
                    continue
                findings.append(
                    Finding(
                        file=label,
                        line=line_no,
                        rule_id=rule_id,
                        matched_text=line.strip()[:240],
                    )
                )
    return findings


def build_report(scan_files: list[Path]) -> dict[str, object]:
    violations: list[Finding] = []
    for path in scan_files:
        violations.extend(lint_file(path))
    violation_dicts = [finding.as_dict() for finding in violations]
    status = "pass" if not violations else "fail"
    return {
        "public_claim_lint_v0_1": True,
        "lint_scope": "public_and_agent_readable_claim_surfaces",
        "status": status,
        "files_scanned": len(scan_files),
        "scanned_files": [relative_label(path) for path in scan_files],
        "violations": violation_dicts,
        "violation_count": len(violation_dicts),
        "warning_count": 0,
        "warnings": [],
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_validation_claim": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "blockers_closed_by_lint": 0,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
    }


def write_markdown(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    violations = report["violations"]
    lines = [
        "# SAEE Public Claim Lint v0.1",
        "",
        "public_claim_lint_v0_1: true",
        f"status: {report['status']}",
        f"files_scanned: {report['files_scanned']}",
        f"violation_count: {report['violation_count']}",
        "blockers_closed_by_lint: 0",
        "",
        "## Purpose",
        "",
        "This local lint checks public and agent-readable SAEE claim surfaces for forbidden positive commercial claims.",
        "It is a commercial-readiness guardrail, not product launch evidence.",
        "",
        "## Boundary",
        "",
        "- runtime_modified: false",
        "- backend_modified: false",
        "- kernel_modified: false",
        "- api_schema_modified: false",
        "- external_calls_made: false",
        "- production_ready: false",
        "- customer_validated: false",
        "- product_launched: false",
        "- private_core_exposed: false",
        "- external_validation_claim: false",
        "- customer_contacted: false",
        "- public_sdk_released: false",
        "",
        "## Violations",
        "",
    ]
    if not violations:
        lines.append("No forbidden public commercial claims were found in the configured scan scope.")
    else:
        lines.append("| File | Line | Rule | Matched text |")
        lines.append("| --- | ---: | --- | --- |")
        for item in violations:
            matched = str(item["matched_text"]).replace("|", "\\|")
            lines.append(
                f"| `{item['file']}` | {item['line']} | `{item['rule_id']}` | {matched} |"
            )
    lines.extend(
        [
            "",
            "## Scanned Files",
            "",
        ]
    )
    for file_name in report["scanned_files"]:
        lines.append(f"- `{file_name}`")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint SAEE public and agent-readable surfaces for forbidden commercial claims."
    )
    parser.add_argument(
        "--scan-file",
        action="append",
        default=[],
        help="File to scan. Repeat to override the default curated public-surface list.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Path for the lint JSON report.",
    )
    parser.add_argument(
        "--output-md",
        default=str(DEFAULT_OUTPUT_MD),
        help="Path for the lint Markdown report.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the JSON report to stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scan_files = resolve_scan_files(args.scan_file)
    report = build_report(scan_files)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    if not output_json.is_absolute():
        output_json = ROOT / output_json
    if not output_md.is_absolute():
        output_md = ROOT / output_md
    write_json(report, output_json)
    write_markdown(report, output_md)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
