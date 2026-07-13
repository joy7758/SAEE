"""Offline validator for the SAEE Alpha positioning release package.

This module validates repository-local files only. It never resolves URLs,
executes examples, or upgrades release truth.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = ROOT / "release/saee-agent-reliability-framework-alpha-v0.1"
EXPECTED_TITLE = "SAEE Agent Reliability Framework Alpha v0.1"
EXPECTED_SUBTITLE = (
    "A framework for controlled rehearsal, reliability assessment, and "
    "evidence-grounded analysis of autonomous agents."
)
REQUIRED_PACKAGE_FILES = {
    "README.md",
    "VERSION",
    "capabilities.json",
    "architecture.md",
    "quick-start.md",
    "limitations.md",
    "changelog.md",
    "examples/README.md",
}
REQUIRED_TRUTH = {
    "alpha_release_preparation": True,
    "public_release_package": True,
    "public_release_executed": False,
    "production_ready": False,
    "commercial_service": False,
    "marketplace_listed": False,
    "customer_validated": False,
    "adoption_validated": False,
    "external_validation": False,
}
FORBIDDEN_CLAIMS = (
    "industry standard",
    "certified",
    "production ready",
    "trusted by all agents",
    "market leader",
    "official standard",
)
NEGATION_MARKERS = ("not ", "not a ", "does not", "do not", "false", "reject", "禁止", "不是", "不提供", "未")


def _result(valid: bool, reasons: list[str], *, documents: int = 0) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reasons,
        "title_consistent": valid,
        "limitations_present": valid,
        "research_claims_bounded": valid,
        "commercial_claims_absent": valid,
        "document_count": documents,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "public_release_executed": False,
        "production_ready": False,
    }


def _local_file(ref: str) -> Path | None:
    if not isinstance(ref, str) or not ref or "://" in ref:
        return None
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def find_forbidden_claims(text: str) -> list[str]:
    """Return affirmative unsupported positioning claims from plain text."""

    found: list[str] = []
    for line in text.splitlines():
        normalized = re.sub(r"\s+", " ", line.strip().lower())
        for phrase in FORBIDDEN_CLAIMS:
            if phrase not in normalized:
                continue
            prefix = normalized[: normalized.index(phrase)]
            if any(marker in prefix[-32:] for marker in NEGATION_MARKERS):
                continue
            found.append(phrase)
    return sorted(set(found))


def validate_capabilities(value: Any) -> dict[str, Any]:
    """Validate the machine-readable positioning contract."""

    if not isinstance(value, dict):
        return _result(False, ["ALPHA_CAPABILITIES_INVALID"])
    if value.get("title") != EXPECTED_TITLE or value.get("subtitle") != EXPECTED_SUBTITLE:
        return _result(False, ["ALPHA_TITLE_INCONSISTENT"])
    if not isinstance(value.get("capabilities"), list) or len(value["capabilities"]) < 4:
        return _result(False, ["ALPHA_CAPABILITIES_INCOMPLETE"])
    refs = [item.get("canonical_ref") for item in value["capabilities"]]
    composition = value.get("composition", {})
    refs.extend(composition.values() if isinstance(composition, dict) else [])
    entrypoints = value.get("entrypoints", {})
    refs.extend(entrypoints.values() if isinstance(entrypoints, dict) else [])
    refs.append(value.get("limitations_ref"))
    if not refs or any(_local_file(ref) is None for ref in refs):
        return _result(False, ["ALPHA_REFERENCE_INVALID"])
    if value.get("truth_boundary") != REQUIRED_TRUTH:
        return _result(False, ["ALPHA_TRUTH_BOUNDARY_INVALID"])
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if find_forbidden_claims(serialized):
        return _result(False, ["ALPHA_UNSUPPORTED_CLAIM"])
    return _result(True, [], documents=len(REQUIRED_PACKAGE_FILES))


def validate_release_package(package_root: Path = RELEASE_ROOT) -> dict[str, Any]:
    """Validate the checked-in release package and positioning documents."""

    if not package_root.is_dir():
        return _result(False, ["ALPHA_RELEASE_PACKAGE_MISSING"])
    missing = [name for name in sorted(REQUIRED_PACKAGE_FILES) if not (package_root / name).is_file()]
    if missing:
        return _result(False, ["ALPHA_RELEASE_DOCUMENT_MISSING"])
    try:
        value = json.loads((package_root / "capabilities.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _result(False, ["ALPHA_CAPABILITIES_INVALID"])
    result = validate_capabilities(value)
    if not result["valid"]:
        return result
    required_surfaces = (
        ROOT / "docs/release/SAEE_ALPHA_ASSET_MAP.md",
        ROOT / "docs/public/SAEE_ALPHA_RELEASE_README.md",
        ROOT / "docs/public/SAEE_AGENT_RELIABILITY_FRAMEWORK_OVERVIEW.md",
        ROOT / "examples/public-demo/README.md",
        ROOT / "docs/research/SAEE_RESEARCH_ARTIFACT_INDEX.md",
        ROOT / "docs/release/SAEE_GITHUB_ALPHA_RELEASE_CHECKLIST.md",
    )
    if not all(path.is_file() for path in required_surfaces):
        return _result(False, ["ALPHA_PUBLIC_SURFACE_MISSING"])
    texts = [(package_root / name).read_text(encoding="utf-8") for name in REQUIRED_PACKAGE_FILES if name.endswith(".md")]
    texts.extend(path.read_text(encoding="utf-8") for path in required_surfaces[:5])
    if find_forbidden_claims("\n".join(texts)):
        return _result(False, ["ALPHA_UNSUPPORTED_CLAIM"])
    limitations = (package_root / "limitations.md").read_text(encoding="utf-8")
    if "production_ready=false" not in limitations and "不是生产服务" not in limitations:
        return _result(False, ["ALPHA_LIMITATIONS_MISSING"])
    return _result(True, [], documents=len(REQUIRED_PACKAGE_FILES))

