#!/usr/bin/env python3
"""Validate the bounded local SAEE academic paper draft without execution."""

from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT_PATH = ROOT / "docs/paper-draft/SAEE_ACADEMIC_PAPER_DRAFT_v0.1.md"
FIGURE_REFERENCES_PATH = ROOT / "docs/paper-draft/FIGURE_REFERENCES.md"
CLAIMS_BOUNDARY_PATH = ROOT / "docs/paper-draft/PAPER_CLAIMS_BOUNDARY.md"
MAKEFILE_PATH = ROOT / "Makefile"
REQUIRED_SECTIONS = {
    "## Abstract",
    "## 1 Introduction",
    "## 2 Related Work",
    "## 3 SAEE Framework",
    "## 4 Evidence Adequacy Model",
    "## 5 Evaluation",
    "## 6 Results",
    "## 7 Limitations",
    "## 8 Discussion and Future Work",
    "## 9 Conclusion",
    "## Artifact References",
    "## Citation Placeholders",
}
REQUIRED_PLACEHOLDERS = {
    "[FIGURE 1 PLACEHOLDER:",
    "[FIGURE 2 PLACEHOLDER:",
    "[FIGURE 3 PLACEHOLDER:",
    "[FIGURE 4 PLACEHOLDER:",
    "[TABLE 1 PLACEHOLDER:",
    "[TABLE 2 PLACEHOLDER:",
}
REQUIRED_CITATIONS = {
    "[REF-OBSERVABILITY]",
    "[REF-GOVERNANCE]",
    "[REF-PROVENANCE]",
    "[REF-AUDIT-EVIDENCE]",
    "[REF-OTEL]",
}
ARTIFACT_REFERENCES = {
    "agent-interface/research-artifact/saee-artifact-manifest.v0.1.json",
    "docs/research-artifact/SAEE_RESEARCH_ARTIFACT_OVERVIEW.md",
    "docs/research-artifact/SAEE_ARCHITECTURE.md",
    "docs/research-artifact/SAEE_EXPERIMENT_SUMMARY.md",
    "docs/EVIDENCE_ADEQUACY_BENCHMARK.md",
    "agent-interface/benchmarks/evidence-adequacy/benchmark.v0.1.json",
    "agent-interface/reproducibility/expected-results.v0.1.json",
    "docs/REPRODUCE_SAEE_EXPERIMENT.md",
    "docs/REPRODUCIBILITY_ENVIRONMENT_REQUIREMENTS.md",
}
FORBIDDEN_POSITIVE_CLAIMS = {
    "saee solves ai governance",
    "saee guarantees accountability",
    "saee legally proves events",
    "saee complies with standards",
    "saee is production ready",
    "saee is externally validated",
    "saee outperforms",
    "state-of-the-art performance",
    "paper accepted",
    "paper has been submitted",
    "论文已录用",
    "论文已提交",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def abstract_word_count(text: str) -> int:
    match = re.search(r"^## Abstract\s*\n(.*?)(?=^## 1 Introduction)", text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return 0
    return len(re.findall(r"\b[A-Za-z0-9][A-Za-z0-9'-]*\b", match.group(1)))


def validate_draft(text: str, *, check_paths: bool = True) -> list[str]:
    errors: list[str] = []
    expected_title = "# From Agent Traces to Accountability Claims: A Verifiable Evidence Adequacy Framework for Agentic Systems"
    if not text.startswith(expected_title) or "local_research_discussion_draft_not_submitted" not in text:
        errors.append("PAPER_DRAFT_IDENTITY_INVALID")
    if not REQUIRED_SECTIONS.issubset(set(text.splitlines())):
        errors.append("PAPER_REQUIRED_SECTION_MISSING")
    count = abstract_word_count(text)
    if not 200 <= count <= 300:
        errors.append("PAPER_ABSTRACT_LENGTH_INVALID")
    if not all(placeholder in text for placeholder in REQUIRED_PLACEHOLDERS):
        errors.append("PAPER_PLACEHOLDER_MISSING")
    if not REQUIRED_CITATIONS.issubset(set(re.findall(r"\[REF-[A-Z-]+\]", text))):
        errors.append("PAPER_CITATION_PLACEHOLDER_MISSING")
    lowered = text.lower()
    if any(claim in lowered for claim in FORBIDDEN_POSITIVE_CLAIMS):
        errors.append("PAPER_UNSUPPORTED_CLAIM")
    if "12 curated scenarios" not in text or "false_positive_count=0" not in text or "boundary_violation_count=0" not in text:
        errors.append("PAPER_RESULT_FACTS_MISSING")
    if check_paths:
        if not all((ROOT / path).is_file() and f"`{path}`" in text for path in ARTIFACT_REFERENCES):
            errors.append("PAPER_ARTIFACT_REFERENCE_INVALID")
    return errors


def main() -> None:
    draft = DRAFT_PATH.read_text(encoding="utf-8")
    figures = FIGURE_REFERENCES_PATH.read_text(encoding="utf-8")
    claims = CLAIMS_BOUNDARY_PATH.read_text(encoding="utf-8")
    require(validate_draft(draft) == [], "valid paper draft rejected")

    missing_section = draft.replace("## 9 Conclusion\n", "", 1)
    require(
        validate_draft(missing_section, check_paths=False) == ["PAPER_REQUIRED_SECTION_MISSING"],
        "missing section negative case",
    )
    missing_citation = draft.replace("[REF-OBSERVABILITY]", "[CITATION-PENDING]")
    require(
        validate_draft(missing_citation, check_paths=False) == ["PAPER_CITATION_PLACEHOLDER_MISSING"],
        "missing citation placeholder negative case",
    )
    unsupported_claim = draft + "\nSAEE guarantees accountability.\n"
    require(
        validate_draft(unsupported_claim, check_paths=False) == ["PAPER_UNSUPPORTED_CLAIM"],
        "unsupported claim negative case",
    )

    for figure in range(1, 5):
        require(f"## Figure {figure}:" in figures, f"Figure {figure} reference missing")
    for field in (
        "paper_submitted=false",
        "paper_accepted=false",
        "external_validation=false",
        "production_ready=false",
    ):
        require(field in claims, f"claims boundary missing: {field}")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    require("check-saee-paper-draft:" in makefile, "paper draft Makefile target missing")

    for _ in range(5):
        current = DRAFT_PATH.read_text(encoding="utf-8")
        require(current == draft, "deterministic paper bytes")
        require(validate_draft(current) == [], "deterministic paper validation")

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    require(
        not imported_roots.intersection({"subprocess", "socket", "requests", "httpx", "urllib"}),
        "forbidden external capability import",
    )

    print("SAEE_PAPER_DRAFT_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=3/3")
    print("deterministic_runs=5/5")
    print(f"required_sections={len(REQUIRED_SECTIONS)}/{len(REQUIRED_SECTIONS)}")
    print(f"abstract_words={abstract_word_count(draft)}")
    print("figure_placeholders=4/4")
    print("table_placeholders=2/2")
    print(f"artifact_references={len(ARTIFACT_REFERENCES)}/{len(ARTIFACT_REFERENCES)}")
    print("unsupported_claims=0")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("paper_submitted=false")
    print("external_validation=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
