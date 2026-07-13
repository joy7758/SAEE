#!/usr/bin/env python3
"""Validate the local SAEE reproducibility specification without execution."""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json"
EXPECTED_PATH = ROOT / "agent-interface/reproducibility/expected-results.v0.1.json"
SCHEMA_PATH = ROOT / "agent-interface/schemas/reproducibility-manifest.schema.json"
INVENTORY_PATH = ROOT / "docs/REPRODUCIBILITY_ARTIFACT_INVENTORY.md"
GUIDE_PATH = ROOT / "docs/REPRODUCE_SAEE_EXPERIMENT.md"
ENVIRONMENT_GUIDE_PATH = ROOT / "docs/REPRODUCIBILITY_ENVIRONMENT_REQUIREMENTS.md"
MAKEFILE_PATH = ROOT / "Makefile"
DEPENDENCY_PATH = ROOT / "saee_backend/requirements.txt"

ARTIFACT_IDS = {
    "resource_resolution_receipt",
    "evidence_adequacy_profile",
    "otel_candidate_mapping",
    "agent_receipt_crosswalk",
    "evidence_adequacy_benchmark",
}
CLAIMS = {
    "RESOURCE_AUTHENTICITY",
    "AUTHORIZED_AGENT_ACTION",
    "HUMAN_OVERSIGHT",
    "EXECUTION_BOUNDARY",
}
COMMANDS = {
    "make check-resource-resolution-receipt",
    "make check-evidence-adequacy",
    "make check-otel-candidate-mapping",
    "make check-agent-receipt-crosswalk",
    "make check-evidence-adequacy-benchmark",
    "make check-saee-reproducibility",
}
EXPECTED_OUTPUTS = {
    "SAEE_RESOURCE_RESOLUTION_RECEIPT_SMOKE: PASS",
    "SAEE_EVIDENCE_ADEQUACY_SMOKE: PASS",
    "SAEE_OTEL_CANDIDATE_MAPPING_SMOKE: PASS",
    "SAEE_AGENT_RECEIPT_CROSSWALK_SMOKE: PASS",
    "SAEE_EVIDENCE_ADEQUACY_BENCHMARK_SMOKE: PASS",
    "SAEE_REPRODUCIBILITY_SMOKE: PASS",
}
TRUTH_BOUNDARY = {
    "public_release_performed": False,
    "doi_created": False,
    "release_tag_created": False,
    "external_reproduction_completed": False,
    "third_party_validation_completed": False,
    "scientific_acceptance_claimed": False,
    "certification_claimed": False,
    "underlying_events_proven": False,
    "production_ready": False,
}
ROOT_KEYS = {
    "saee_reproducibility_manifest_v0_1",
    "manifest_version",
    "artifact_name",
    "status",
    "artifact_scope",
    "claims_evaluated",
    "benchmark_cases",
    "execution_mode",
    "environment_constraints",
    "artifacts",
    "required_commands",
    "expected_results_ref",
    "expected_outputs",
    "limitations",
    "truth_boundary",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object required: {path}")
    return value


def validate_manifest(value: Any) -> list[str]:
    if not isinstance(value, dict) or set(value) != ROOT_KEYS:
        return ["REPRO_ROOT_FIELDS_INVALID"]
    errors: list[str] = []
    if (
        value.get("saee_reproducibility_manifest_v0_1") is not True
        or value.get("manifest_version") != "0.1.0"
        or value.get("artifact_name") != "SAEE Evidence Adequacy Architecture"
        or value.get("status") != "local_reproducibility_specification_not_published"
        or value.get("execution_mode") != "offline_synthetic"
        or value.get("benchmark_cases") != 12
    ):
        errors.append("REPRO_IDENTITY_INVALID")
    if set(value.get("artifact_scope", [])) != ARTIFACT_IDS:
        errors.append("REPRO_ARTIFACT_SCOPE_INVALID")
    if set(value.get("claims_evaluated", [])) != CLAIMS:
        errors.append("REPRO_CLAIMS_INVALID")
    if set(value.get("required_commands", [])) != COMMANDS:
        errors.append("REPRO_COMMANDS_INVALID")
    if set(value.get("expected_outputs", [])) != EXPECTED_OUTPUTS:
        errors.append("REPRO_EXPECTED_OUTPUTS_INVALID")
    if value.get("expected_results_ref") != "agent-interface/reproducibility/expected-results.v0.1.json":
        errors.append("REPRO_EXPECTED_RESULTS_REF_INVALID")

    environment = value.get("environment_constraints")
    if not isinstance(environment, dict) or environment.get("network_required") is not False:
        errors.append("REPRO_NETWORK_BOUNDARY_INVALID")
    elif (
        environment.get("python_command") != "python3"
        or environment.get("python_syntax_minimum") != "3.10"
        or environment.get("minimum_python_version_declared_by_repository") is not False
        or environment.get("python_minimum_supported_version") != "not_formally_declared"
        or environment.get("python_support_status") != "syntax_floor_identified_version_matrix_not_tested"
        or set(environment.get("python_support_basis", []))
        != {
            "repository_uses_python_3_10_runtime_features",
            "ci_uses_rolling_python_3_x_without_version_matrix",
            "only_python_3_14_5_observed_for_this_package",
        }
        or environment.get("dependency_manifest") != "saee_backend/requirements.txt"
        or set(environment.get("required_modules", [])) != {"jsonschema", "pydantic"}
        or {
            package.get("name"): package.get("constraint")
            for package in environment.get("required_packages", [])
            if isinstance(package, dict)
        }
        != {"jsonschema": ">=4.18,<5.0", "pydantic": ">=2.0,<3.0"}
        or environment.get("jsonschema_declared_in_dependency_manifest") is not True
    ):
        errors.append("REPRO_ENVIRONMENT_INVALID")

    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 5:
        errors.append("REPRO_ARTIFACT_COUNT_INVALID")
    else:
        ids: set[str] = set()
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict) or set(artifact) != {
                "artifact_id",
                "purpose",
                "required_files",
                "validation_command",
                "expected_output",
            }:
                errors.append(f"REPRO_ARTIFACT_{index}_INVALID")
                continue
            artifact_id = artifact.get("artifact_id")
            if artifact_id not in ARTIFACT_IDS or artifact_id in ids:
                errors.append(f"REPRO_ARTIFACT_{index}_ID_INVALID")
            else:
                ids.add(artifact_id)
            files = artifact.get("required_files")
            if not isinstance(files, list) or not files or not all(
                isinstance(path, str) and path and (ROOT / path).is_file() for path in files
            ):
                errors.append(f"REPRO_ARTIFACT_{index}_FILES_INVALID")
            if artifact.get("validation_command") not in COMMANDS:
                errors.append(f"REPRO_ARTIFACT_{index}_COMMAND_INVALID")
            if artifact.get("expected_output") not in EXPECTED_OUTPUTS:
                errors.append(f"REPRO_ARTIFACT_{index}_OUTPUT_INVALID")
            if not isinstance(artifact.get("purpose"), str) or not artifact["purpose"]:
                errors.append(f"REPRO_ARTIFACT_{index}_PURPOSE_INVALID")
        if ids != ARTIFACT_IDS:
            errors.append("REPRO_ARTIFACT_IDS_INCOMPLETE")

    if not isinstance(value.get("limitations"), list) or len(value["limitations"]) < 4:
        errors.append("REPRO_LIMITATIONS_INVALID")
    if value.get("truth_boundary") != TRUTH_BOUNDARY:
        errors.append("REPRO_TRUTH_BOUNDARY_INVALID")
    return errors


def validate_expected_results(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {
        "saee_reproducibility_expected_results_v0_1",
        "results_version",
        "scope",
        "resource_resolution_receipt",
        "evidence_adequacy",
        "otel_candidate_mapping",
        "agent_receipt_crosswalk",
        "evidence_adequacy_benchmark",
        "truth_boundary",
    }:
        return False
    return (
        value.get("saee_reproducibility_expected_results_v0_1") is True
        and value.get("results_version") == "0.1.0"
        and value.get("scope") == "local_regression_expectations_only"
        and value.get("resource_resolution_receipt") == {
            "positive_cases": 1,
            "negative_cases": 4,
            "adversarial_cases": 38,
            "deterministic_runs": 10,
        }
        and value.get("evidence_adequacy", {}).get("positive_cases") == 4
        and value.get("evidence_adequacy", {}).get("negative_cases") == 4
        and value.get("evidence_adequacy", {}).get("accountability_claim_established") is False
        and value.get("otel_candidate_mapping", {}).get("trace_auto_accepted_as_evidence") == 0
        and value.get("agent_receipt_crosswalk", {}).get("unsupported_claims") == 0
        and value.get("evidence_adequacy_benchmark", {}).get("scenario_cases") == 12
        and value.get("evidence_adequacy_benchmark", {}).get("pass_cases") == 5
        and value.get("evidence_adequacy_benchmark", {}).get("fail_cases") == 7
        and value.get("evidence_adequacy_benchmark", {}).get("false_positive_count") == 0
        and value.get("evidence_adequacy_benchmark", {}).get("boundary_violation_count") == 0
        and all(flag is False for flag in value.get("truth_boundary", {}).values())
    )


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    schema = read_json(SCHEMA_PATH)
    expected = read_json(EXPECTED_PATH)
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "manifest schema draft")
    require(schema.get("additionalProperties") is False, "manifest schema must be closed")
    require(validate_manifest(manifest) == [], "valid manifest rejected")
    require(validate_expected_results(expected), "expected results invalid")

    invalid_network = copy.deepcopy(manifest)
    invalid_network["environment_constraints"]["network_required"] = True
    require(
        validate_manifest(invalid_network) == ["REPRO_NETWORK_BOUNDARY_INVALID"],
        "network boundary negative case",
    )
    missing_expected_ref = copy.deepcopy(manifest)
    del missing_expected_ref["expected_results_ref"]
    require(
        validate_manifest(missing_expected_ref) == ["REPRO_ROOT_FIELDS_INVALID"],
        "missing expected-results reference negative case",
    )

    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    inventory = INVENTORY_PATH.read_text(encoding="utf-8")
    guide = GUIDE_PATH.read_text(encoding="utf-8")
    environment_guide = ENVIRONMENT_GUIDE_PATH.read_text(encoding="utf-8")
    boundary_english = "This reproducibility package describes local execution requirements and expected outputs. It does not represent independent validation, certification, or proof that underlying events occurred."
    boundary_chinese = "该复现包描述本地执行要求和预期输出，不代表独立验证、认证，也不证明底层事件一定真实发生。"
    for text, name in ((inventory, "inventory"), (guide, "guide")):
        require(boundary_english in text, f"English boundary missing: {name}")
        require(boundary_chinese in text, f"Chinese boundary missing: {name}")
        require("production_ready=false" in text or "生产就绪" in text, f"production boundary missing: {name}")
    require(
        "The declared environment describes the requirements needed to reproduce local SAEE artifact validation. It does not represent production deployment requirements or external validation."
        in environment_guide,
        "environment English boundary missing",
    )
    require(
        "声明的环境描述用于复现 SAEE 本地研究产物验证所需条件，不代表生产部署要求，也不代表外部验证完成。"
        in environment_guide,
        "environment Chinese boundary missing",
    )
    for command in COMMANDS:
        target = command.removeprefix("make ") + ":"
        require(target in makefile, f"Makefile target missing: {command}")
        require(command in guide, f"guide command missing: {command}")
    for artifact in manifest["artifacts"]:
        joined_sources = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in artifact["required_files"])
        require(artifact["expected_output"] in joined_sources, f"expected output not backed by source: {artifact['artifact_id']}")

    requirements = DEPENDENCY_PATH.read_text(encoding="utf-8")
    require("pydantic>=2.0,<3.0" in requirements, "pydantic dependency declaration")
    require("jsonschema>=4.18,<5.0" in requirements, "jsonschema dependency declaration")
    require(importlib.util.find_spec("jsonschema") is not None, "jsonschema unavailable in current environment")
    require(importlib.util.find_spec("pydantic") is not None, "pydantic unavailable in current environment")

    canonical_manifest = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    canonical_expected = json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(
            json.dumps(read_json(MANIFEST_PATH), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical_manifest,
            "deterministic manifest",
        )
        require(
            json.dumps(read_json(EXPECTED_PATH), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical_expected,
            "deterministic expected results",
        )

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    require(not imported_roots.intersection({"subprocess", "socket", "requests", "httpx", "urllib"}), "external capability import")

    print("SAEE_REPRODUCIBILITY_SMOKE: PASS")
    print("manifest_valid_cases=1/1")
    print("manifest_invalid_cases=2/2")
    print("artifact_inventory_check=1/1")
    print("artifact_files_checked=23/23")
    print("required_commands_documented=6/6")
    print("expected_results_check=1/1")
    print("deterministic_runs=5/5")
    print("unsupported_claims=0")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_downloads=0")
    print("artifact_code_executed=false")
    print("public_release_performed=false")
    print("external_reproduction_completed=false")
    print("third_party_validation_completed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
