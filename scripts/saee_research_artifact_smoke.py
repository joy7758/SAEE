#!/usr/bin/env python3
"""Validate the local SAEE research artifact paper-support package."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "agent-interface/research-artifact/saee-artifact-manifest.v0.1.json"
MAKEFILE_PATH = ROOT / "Makefile"
REQUIRED_DOCUMENTS = {
    "docs/research-artifact/SAEE_RESEARCH_ARTIFACT_OVERVIEW.md",
    "docs/research-artifact/SAEE_ARTIFACT_STRUCTURE.md",
    "docs/research-artifact/SAEE_ARCHITECTURE.md",
    "docs/research-artifact/SAEE_EXPERIMENT_SUMMARY.md",
    "docs/research-artifact/FIGURE_SPECIFICATIONS.md",
    "docs/research-artifact/PAPER_ARTIFACT_CHECKLIST.md",
}
ARTIFACT_SCOPE = {
    "evidence_objects",
    "adequacy_profiles",
    "trace_candidate_mapping",
    "benchmark",
    "reproducibility",
}
CONTRIBUTIONS = {
    "evidence_object_layer",
    "evidence_adequacy_layer",
    "candidate_trace_mapping_layer",
    "reproducibility_layer",
}
COMPONENT_IDS = {
    "resource_resolution_receipt",
    "evidence_adequacy_profile",
    "otel_candidate_mapping",
    "agent_receipt_crosswalk",
    "evidence_adequacy_benchmark",
    "reproducibility_package",
}
VALIDATION_COMMANDS = {
    "make check-saee-research-artifact",
    "make check-saee-reproducibility",
    "make check-saee-environment-requirements",
    "make check-evidence-adequacy-benchmark",
    "make check-evidence-adequacy",
    "make check-otel-candidate-mapping",
    "make check-resource-resolution-receipt",
    "make check-agent-receipt-crosswalk",
    "python3 scripts/saee_agent_interface_smoke.py",
    "python3 scripts/mainline_guard.py",
}
ROOT_KEYS = {
    "saee_research_artifact_manifest_v0_1",
    "artifact_version",
    "artifact_id",
    "status",
    "research_question",
    "artifact_scope",
    "evaluation_type",
    "contributions",
    "components",
    "documentation",
    "validation_commands",
    "benchmark_summary",
    "environment_ref",
    "limitations",
    "external_validation",
    "publication_status",
    "truth_boundary",
    "production_ready",
}
TRUTH_KEYS = {
    "paper_submitted",
    "paper_accepted",
    "arxiv_uploaded",
    "doi_created",
    "github_release_created",
    "publication_tag_created",
    "external_reproduction_completed",
    "third_party_validation_completed",
    "superiority_claimed",
    "regulatory_compliance_claimed",
    "legal_validity_claimed",
    "certification_claimed",
    "production_ready",
}
FORBIDDEN_POSITIVE_CLAIMS = {
    "saee is compliant with",
    "saee complies with",
    "saee is certified",
    "saee outperforms",
    "saee is superior to",
    "has been externally validated",
    "is externally validated",
    "paper accepted",
    "论文已录用",
    "已通过外部验证",
    "已获得认证",
    "production_ready=true",
    '"production_ready": true',
    '"external_validation": true',
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def safe_repo_path(value: Any) -> Path | None:
    if not isinstance(value, str) or not value or value.startswith("/") or ".." in Path(value).parts:
        return None
    return ROOT / value


def validate_manifest(value: Any, *, check_files: bool = True) -> list[str]:
    if not isinstance(value, dict) or set(value) != ROOT_KEYS:
        return ["ARTIFACT_ROOT_FIELDS_INVALID"]
    errors: list[str] = []
    if (
        value.get("saee_research_artifact_manifest_v0_1") is not True
        or value.get("artifact_version") != "0.1"
        or value.get("artifact_id") != "saee-research-artifact-paper-package-v0.1"
        or value.get("status") != "local_paper_support_package_not_submitted"
        or value.get("evaluation_type") != "synthetic_offline"
    ):
        errors.append("ARTIFACT_IDENTITY_INVALID")
    if value.get("publication_status") != "not_submitted":
        errors.append("ARTIFACT_PUBLICATION_BOUNDARY_INVALID")
    if value.get("external_validation") is not False or value.get("production_ready") is not False:
        errors.append("ARTIFACT_TRUTH_BOUNDARY_INVALID")
    truth = value.get("truth_boundary")
    if not isinstance(truth, dict) or set(truth) != TRUTH_KEYS or any(item is not False for item in truth.values()):
        errors.append("ARTIFACT_TRUTH_BOUNDARY_INVALID")
    if set(value.get("artifact_scope", [])) != ARTIFACT_SCOPE:
        errors.append("ARTIFACT_SCOPE_INVALID")
    if set(value.get("contributions", [])) != CONTRIBUTIONS:
        errors.append("ARTIFACT_CONTRIBUTIONS_INVALID")
    if set(value.get("documentation", [])) != REQUIRED_DOCUMENTS:
        errors.append("ARTIFACT_DOCUMENTATION_INVALID")
    if set(value.get("validation_commands", [])) != VALIDATION_COMMANDS:
        errors.append("ARTIFACT_COMMANDS_INVALID")

    components = value.get("components")
    referenced: list[str] = list(value.get("documentation", []))
    if not isinstance(components, list) or len(components) != 6:
        errors.append("ARTIFACT_COMPONENTS_INVALID")
    else:
        ids: set[str] = set()
        for component in components:
            if not isinstance(component, dict) or set(component) != {
                "component_id",
                "purpose",
                "artifact_files",
                "validation_command",
                "expected_output",
                "result_summary",
            }:
                errors.append("ARTIFACT_COMPONENT_FIELDS_INVALID")
                continue
            component_id = component.get("component_id")
            if component_id not in COMPONENT_IDS or component_id in ids:
                errors.append("ARTIFACT_COMPONENT_ID_INVALID")
            else:
                ids.add(component_id)
            files = component.get("artifact_files")
            if not isinstance(files, list) or not files or len(files) != len(set(files)):
                errors.append("ARTIFACT_COMPONENT_FILES_INVALID")
            else:
                referenced.extend(files)
            if not isinstance(component.get("purpose"), str) or not component["purpose"]:
                errors.append("ARTIFACT_COMPONENT_PURPOSE_INVALID")
            if not isinstance(component.get("result_summary"), str) or not component["result_summary"]:
                errors.append("ARTIFACT_COMPONENT_RESULT_INVALID")
            if component.get("validation_command") not in VALIDATION_COMMANDS:
                errors.append("ARTIFACT_COMPONENT_COMMAND_INVALID")
            if not isinstance(component.get("expected_output"), str) or not component["expected_output"].startswith("SAEE_"):
                errors.append("ARTIFACT_COMPONENT_OUTPUT_INVALID")
        if ids != COMPONENT_IDS:
            errors.append("ARTIFACT_COMPONENTS_INCOMPLETE")

    environment_ref = value.get("environment_ref")
    referenced.append(environment_ref)
    if check_files:
        for item in referenced:
            path = safe_repo_path(item)
            if path is None or not path.is_file():
                errors.append("ARTIFACT_REFERENCED_PATH_MISSING")
                break

    benchmark = value.get("benchmark_summary")
    if benchmark != {
        "scenario_count": 12,
        "claim_type_count": 4,
        "evidence_level_count": 4,
        "pass_count": 5,
        "fail_count": 7,
        "false_positive_count": 0,
        "boundary_violation_count": 0,
        "scope": "curated_synthetic_regression_only",
    }:
        errors.append("ARTIFACT_BENCHMARK_SUMMARY_INVALID")
    if not isinstance(value.get("research_question"), str) or not value["research_question"]:
        errors.append("ARTIFACT_RESEARCH_QUESTION_INVALID")
    if not isinstance(value.get("limitations"), list) or len(value["limitations"]) < 6:
        errors.append("ARTIFACT_LIMITATIONS_INVALID")
    return errors


def unsupported_claims(manifest: dict[str, Any]) -> list[str]:
    texts = [json.dumps(manifest, ensure_ascii=False)]
    texts.extend((ROOT / path).read_text(encoding="utf-8") for path in REQUIRED_DOCUMENTS)
    corpus = "\n".join(texts).lower()
    return sorted(claim for claim in FORBIDDEN_POSITIVE_CLAIMS if claim in corpus)


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    require(validate_manifest(manifest) == [], "valid artifact manifest rejected")
    require(unsupported_claims(manifest) == [], "unsupported positive claim found")

    missing_path = copy.deepcopy(manifest)
    missing_path["components"][0]["artifact_files"][0] = "agent-interface/missing-artifact.json"
    require(
        validate_manifest(missing_path) == ["ARTIFACT_REFERENCED_PATH_MISSING"],
        "missing path negative case",
    )
    submitted = copy.deepcopy(manifest)
    submitted["publication_status"] = "submitted"
    require(
        validate_manifest(submitted) == ["ARTIFACT_PUBLICATION_BOUNDARY_INVALID"],
        "publication boundary negative case",
    )
    external_validation = copy.deepcopy(manifest)
    external_validation["external_validation"] = True
    require(
        validate_manifest(external_validation) == ["ARTIFACT_TRUTH_BOUNDARY_INVALID"],
        "external validation negative case",
    )

    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    for command in VALIDATION_COMMANDS:
        if command.startswith("make "):
            require(command.removeprefix("make ") + ":" in makefile, f"Make target missing: {command}")
        else:
            require((ROOT / command.removeprefix("python3 ")).is_file(), f"Script missing: {command}")

    architecture = (ROOT / "docs/research-artifact/SAEE_ARCHITECTURE.md").read_text(encoding="utf-8")
    require("Trace does not become evidence automatically." in architecture, "trace boundary missing")
    overview = (ROOT / "docs/research-artifact/SAEE_RESEARCH_ARTIFACT_OVERVIEW.md").read_text(encoding="utf-8")
    require("Research Artifact Package ≠ Paper Acceptance" in overview, "publication boundary missing")
    checklist = (ROOT / "docs/research-artifact/PAPER_ARTIFACT_CHECKLIST.md").read_text(encoding="utf-8")
    require("publication_status=not_submitted" in checklist, "checklist status missing")

    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        current = read_json(MANIFEST_PATH)
        require(validate_manifest(current) == [], "deterministic validation")
        require(unsupported_claims(current) == [], "deterministic claim scan")
        require(
            json.dumps(current, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "deterministic manifest",
        )

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

    referenced_paths = {
        path
        for component in manifest["components"]
        for path in component["artifact_files"]
    } | set(manifest["documentation"]) | {manifest["environment_ref"]}
    print("SAEE_RESEARCH_ARTIFACT_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=3/3")
    print("deterministic_runs=5/5")
    print(f"components={len(manifest['components'])}/6")
    print(f"required_documents={len(manifest['documentation'])}/6")
    print(f"referenced_paths={len(referenced_paths)}/{len(referenced_paths)}")
    print("unsupported_claims=0")
    print("network_calls=0")
    print("subprocess_started=false")
    print("artifact_code_executed=false")
    print("paper_submitted=false")
    print("publication_performed=false")
    print("external_validation=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
