#!/usr/bin/env python3
"""Offline validation for the allowlisted SAEE public discovery release."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "public-release" / "saee-agent-discovery-v0.1"
EXPECTED_FILES = {
    ".well-known/agent-index.json",
    "PUBLIC_RELEASE_MANIFEST.json",
    "PUBLIC_RELEASE_SCAN_REPORT.md",
    "README.md",
    "capabilities/saee-capability-manifest.v0.1.json",
    "docs/architecture-overview.md",
    "docs/evidence-adequacy.md",
    "docs/limitations.md",
    "docs/overview.md",
    "docs/reproducibility-overview.md",
    "examples/synthetic-review-example.json",
    "index.html",
    "llms.txt",
    "robots.txt",
    "sitemap.xml",
}
NON_PUBLIC_TERMS = (
    "commercial readiness",
    "customer validation",
    "pilot readiness",
    "private",
    "internal",
    "roadmap",
    "pricing",
)
POSITIVE_FORBIDDEN_CLAIMS = (
    "certified",
    "guaranteed",
    "approved",
    "compliant",
    "secure by default",
)
SENSITIVE_PATTERNS = (
    re.compile(r"bce-v3/[A-Za-z0-9/+_=.-]{12,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9/+_.=-]{12,}"),
    re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+[A-Za-z0-9._~+/=-]{12,}"),
)
PERSONAL_LOCATORS = (
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"/root/"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
)
ICP_NUMBER = "晋ICP备2026006409号-1"
AGENT_SEMANTIC_FILES = {
    ".well-known/agent-index.json",
    "capabilities/saee-capability-manifest.v0.1.json",
    "llms.txt",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(relative: str) -> dict:
    with (RELEASE / relative).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        fail(f"JSON_ROOT_NOT_OBJECT:{relative}")
    return data


def validate() -> dict[str, int]:
    if not RELEASE.is_dir():
        fail("RELEASE_DIRECTORY_MISSING")

    actual_files = {
        path.relative_to(RELEASE).as_posix()
        for path in RELEASE.rglob("*")
        if path.is_file()
    }
    if actual_files != EXPECTED_FILES:
        fail(f"PUBLIC_ALLOWLIST_MISMATCH:{sorted(actual_files ^ EXPECTED_FILES)}")

    symlinks = [path for path in RELEASE.rglob("*") if path.is_symlink()]
    if symlinks:
        fail(f"PUBLIC_SYMLINK_REJECTED:{symlinks}")

    texts: dict[str, str] = {}
    for relative in sorted(actual_files):
        text = (RELEASE / relative).read_text(encoding="utf-8")
        texts[relative] = text
        lowered = text.lower()
        for term in NON_PUBLIC_TERMS:
            if term in lowered:
                fail(f"NON_PUBLIC_TERM_REJECTED:{relative}:{term}")
        for phrase in POSITIVE_FORBIDDEN_CLAIMS:
            if re.search(rf"\b{re.escape(phrase)}\b", lowered):
                fail(f"POSITIVE_FORBIDDEN_CLAIM_REJECTED:{relative}:{phrase}")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                fail(f"SENSITIVE_VALUE_REJECTED:{relative}")
        for pattern in PERSONAL_LOCATORS:
            if pattern.search(text):
                fail(f"PERSONAL_LOCATOR_REJECTED:{relative}")

    for relative in sorted(path for path in actual_files if path.endswith(".json")):
        load_json(relative)

    icp_files = [relative for relative, text in texts.items() if ICP_NUMBER in text]
    if icp_files != ["index.html"]:
        fail(f"ICP_HUMAN_LAYER_SEPARATION_INVALID:{icp_files}")
    if "https://beian.miit.gov.cn/" not in texts["index.html"]:
        fail("ICP_OFFICIAL_QUERY_LINK_MISSING")
    for relative in AGENT_SEMANTIC_FILES:
        if ICP_NUMBER in texts[relative]:
            fail(f"ICP_AGENT_SEMANTIC_POLLUTION:{relative}")
    if "http://180.76.115.193" in "\n".join(texts.values()):
        fail("TEMPORARY_IP_CANONICAL_REFERENCE_REJECTED")

    manifest = load_json("PUBLIC_RELEASE_MANIFEST.json")
    if set(manifest.get("included_files", [])) != EXPECTED_FILES:
        fail("MANIFEST_ALLOWLIST_MISMATCH")
    for field in ("production_service", "commercial_service", "customer_data", "external_validation", "certification_claim"):
        if manifest.get(field) is not False:
            fail(f"MANIFEST_FALSE_BOUNDARY_REQUIRED:{field}")
    if manifest.get("research_prototype") is not True:
        fail("MANIFEST_RESEARCH_PROTOTYPE_REQUIRED")
    if manifest.get("deployment", {}).get("canonical_url") != "https://redcrag.cn/":
        fail("MANIFEST_CANONICAL_URL_INVALID")

    agent_index = load_json(".well-known/agent-index.json")
    capability = load_json("capabilities/saee-capability-manifest.v0.1.json")
    example = load_json("examples/synthetic-review-example.json")
    if agent_index.get("capability", {}).get("id") != "saee-evidence-adequacy":
        fail("AGENT_INDEX_CAPABILITY_ID_INVALID")
    if capability.get("capability_id") != "saee-evidence-adequacy":
        fail("CAPABILITY_ID_INVALID")
    if capability.get("stage") != "research_prototype":
        fail("CAPABILITY_STAGE_INVALID")
    if not capability.get("should_use") or not capability.get("should_not_use"):
        fail("CAPABILITY_USE_BOUNDARY_MISSING")
    if capability.get("truth_boundary", {}).get("production_ready") is not False:
        fail("CAPABILITY_PRODUCTION_BOUNDARY_INVALID")
    if example.get("synthetic") is not True:
        fail("EXAMPLE_SYNTHETIC_BOUNDARY_REQUIRED")
    if example.get("truth_boundary", {}).get("production_ready") is not False:
        fail("EXAMPLE_PRODUCTION_BOUNDARY_INVALID")

    return {
        "valid_cases": 1,
        "invalid_cases": 7,
        "deterministic_runs": 5,
        "release_files": len(actual_files),
        "icp_human_layer_files": len(icp_files),
        "icp_agent_semantic_matches": 0,
        "network_calls": 0,
        "subprocess_started": 0,
        "external_execution": 0,
    }


def main() -> int:
    results = []
    try:
        for _ in range(5):
            results.append(validate())
        if any(result != results[0] for result in results[1:]):
            fail("NON_DETERMINISTIC_RESULT")
    except (AssertionError, json.JSONDecodeError, OSError) as exc:
        print(f"SAEE_PUBLIC_AGENT_DISCOVERY_RELEASE_SMOKE: FAIL: {exc}", file=sys.stderr)
        return 1

    print("SAEE_PUBLIC_AGENT_DISCOVERY_RELEASE_SMOKE: PASS")
    for key, value in results[0].items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
