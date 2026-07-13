#!/usr/bin/env python3
"""Validate SAEE local reproducibility environment declarations offline."""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
import re
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json"
REQUIREMENTS_PATH = ROOT / "saee_backend/requirements.txt"
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REQUIRED_PACKAGES = {
    "jsonschema": ">=4.18,<5.0",
    "pydantic": ">=2.0,<3.0",
}
REQUIRED_ENVIRONMENT_KEYS = {
    "python_command",
    "python_version_observed",
    "python_syntax_minimum",
    "minimum_python_version_declared_by_repository",
    "python_minimum_supported_version",
    "python_support_status",
    "python_support_basis",
    "dependency_manifest",
    "required_modules",
    "required_packages",
    "jsonschema_declared_in_dependency_manifest",
    "network_required",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def version_tuple(value: str) -> tuple[int, int, int]:
    require(bool(VERSION_PATTERN.fullmatch(value)), f"invalid version: {value}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def declared_requirement_lines(text: str) -> set[str]:
    return {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def validate_environment(manifest: Any, requirements_text: str) -> list[str]:
    if not isinstance(manifest, dict) or "environment_constraints" not in manifest:
        return ["ENVIRONMENT_SECTION_REQUIRED"]
    environment = manifest["environment_constraints"]
    if not isinstance(environment, dict) or set(environment) != REQUIRED_ENVIRONMENT_KEYS:
        return ["ENVIRONMENT_FIELDS_INVALID"]

    errors: list[str] = []
    observed = environment.get("python_version_observed")
    syntax_minimum = environment.get("python_syntax_minimum")
    if not isinstance(observed, str) or not VERSION_PATTERN.fullmatch(observed):
        errors.append("PYTHON_VERSION_INVALID")
    if syntax_minimum != "3.10":
        errors.append("PYTHON_SYNTAX_FLOOR_INVALID")
    if (
        environment.get("minimum_python_version_declared_by_repository") is not False
        or environment.get("python_minimum_supported_version") != "not_formally_declared"
        or environment.get("python_support_status")
        != "syntax_floor_identified_version_matrix_not_tested"
    ):
        errors.append("PYTHON_SUPPORT_CLAIM_INVALID")

    packages = environment.get("required_packages")
    package_map = {
        item.get("name"): item.get("constraint")
        for item in packages
        if isinstance(packages, list) and isinstance(item, dict)
    } if isinstance(packages, list) else {}
    if package_map != REQUIRED_PACKAGES or set(environment.get("required_modules", [])) != set(REQUIRED_PACKAGES):
        errors.append("REQUIRED_PACKAGES_INVALID")

    requirement_lines = declared_requirement_lines(requirements_text)
    missing_lines = {
        f"{name}{constraint}"
        for name, constraint in REQUIRED_PACKAGES.items()
        if f"{name}{constraint}" not in requirement_lines
    }
    if missing_lines or environment.get("jsonschema_declared_in_dependency_manifest") is not True:
        errors.append("DEPENDENCY_DECLARATION_MISSING")
    if environment.get("dependency_manifest") != "saee_backend/requirements.txt":
        errors.append("DEPENDENCY_SOURCE_INVALID")
    if environment.get("network_required") is not False:
        errors.append("ENVIRONMENT_NETWORK_BOUNDARY_INVALID")
    return errors


def validate_current_runtime() -> None:
    require(sys.version_info[:2] >= (3, 10), "current Python is below the documented syntax floor")
    for package, constraint in REQUIRED_PACKAGES.items():
        require(importlib.util.find_spec(package) is not None, f"required package unavailable: {package}")
        try:
            installed = version(package)
        except PackageNotFoundError as exc:
            raise AssertionError(f"required package metadata unavailable: {package}") from exc
        installed_tuple = version_tuple(installed)
        if package == "jsonschema":
            require((4, 18, 0) <= installed_tuple < (5, 0, 0), f"jsonschema outside {constraint}")
        elif package == "pydantic":
            require((2, 0, 0) <= installed_tuple < (3, 0, 0), f"pydantic outside {constraint}")


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")
    require(validate_environment(manifest, requirements) == [], "valid environment rejected")
    validate_current_runtime()

    missing_dependency = requirements.replace("jsonschema>=4.18,<5.0\n", "")
    require(
        validate_environment(manifest, missing_dependency) == ["DEPENDENCY_DECLARATION_MISSING"],
        "missing dependency negative case",
    )
    malformed_version = copy.deepcopy(manifest)
    malformed_version["environment_constraints"]["python_version_observed"] = "3.14"
    require(
        validate_environment(malformed_version, requirements) == ["PYTHON_VERSION_INVALID"],
        "malformed version negative case",
    )
    missing_environment = copy.deepcopy(manifest)
    del missing_environment["environment_constraints"]
    require(
        validate_environment(missing_environment, requirements) == ["ENVIRONMENT_SECTION_REQUIRED"],
        "missing environment negative case",
    )

    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        current = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        require(validate_environment(current, requirements) == [], "deterministic validation")
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
        not imported_roots.intersection({"subprocess", "socket", "requests", "httpx", "urllib", "venv"}),
        "forbidden environment capability import",
    )

    print("SAEE_ENVIRONMENT_REQUIREMENTS_SMOKE: PASS")
    print("valid_environment_cases=1/1")
    print("invalid_environment_cases=3/3")
    print("deterministic_runs=5/5")
    print("required_packages=2/2")
    print("python_syntax_minimum=3.10")
    print("python_minimum_supported_version=not_formally_declared")
    print(f"python_version_observed={manifest['environment_constraints']['python_version_observed']}")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_downloads=0")
    print("virtual_environment_created=false")
    print("external_reproduction_completed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
