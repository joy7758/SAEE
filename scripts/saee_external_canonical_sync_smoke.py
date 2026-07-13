#!/usr/bin/env python3
"""Smoke check for SAEE repository-layer external canonical sync."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DEFINITION = (
    "SAEE is an AI agent long-term stability evaluation and decision infrastructure system."
)

REQUIRED_CANONICAL_FILES = [
    "README.md",
    "CITATION.cff",
    ".zenodo.json",
    "llms.txt",
    "docs/canonical/SAEE_CANONICAL_METADATA.yaml",
    "docs/canonical/SAEE_EXTERNAL_CANONICAL_SYNC_REPORT.md",
    "docs/release/GITHUB_ABOUT_COPY.md",
    "docs/release/ZENODO_METADATA_COPY.md",
    "docs/release/LANDING_META_COPY.md",
    "docs/release/PROFILE_README_SNIPPET.md",
    "agent-index.json",
]

HTML_FILES = [
    "phase_b_product/landing/index.html",
    "phase_b_product/landing/for-ai-assistants.html",
]

EXTERNAL_SURFACES = REQUIRED_CANONICAL_FILES + HTML_FILES + [
    "docs/strategy/SAEE_EXTERNAL_CANONICAL_SYNC_RECOMMENDATION_GATE.md",
]

PRIVATE_CORE_SCAN_SURFACES = [
    "CITATION.cff",
    ".zenodo.json",
    "docs/canonical/SAEE_CANONICAL_METADATA.yaml",
    "docs/canonical/SAEE_EXTERNAL_CANONICAL_SYNC_REPORT.md",
    "docs/release/GITHUB_ABOUT_COPY.md",
    "docs/release/ZENODO_METADATA_COPY.md",
    "docs/release/LANDING_META_COPY.md",
    "docs/release/PROFILE_README_SNIPPET.md",
] + HTML_FILES

FORBIDDEN_PRIVATE_CORE_TOKENS = [
    "saee_core_private/",
    "PRIVATE_CORE_MANIFEST",
    "kernel_logic_included",
    "fitness_mechanism_included",
    "selection_mechanism_included",
    "mutation_mechanism_included",
    "lineage_internals_included",
]

FORBIDDEN_OVERCLAIM_TOKENS = [
    "external_validation_claim=true",
    "external_validation_claim: true",
    '"external_validation_claim": true',
    "external_validation_success_claim=true",
    "external_validation_success_claim: true",
    '"external_validation_success_claim": true',
    "production_ready=true",
    "production_ready: true",
    '"production_ready": true',
    "production-ready: true",
    "customer_validated=true",
    "customer_validated: true",
    '"customer_validated": true',
    "product_launched=true",
    "product_launched: true",
    '"product_launched": true',
    "public_sdk_release=true",
    "public_sdk_release: true",
    '"public_sdk_release": true',
]

FORBIDDEN_RUNTIME_PATHS = [
    "kernel/",
    "kernel_v0_2/",
    "saee_v1_0/",
    "saee_backend/",
    "schemas/saee_mvp_api.schema.json",
]


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        raise AssertionError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_json_files() -> None:
    json.loads(read_text(".zenodo.json"))
    json.loads(read_text("agent-index.json"))


def check_canonical_definition() -> None:
    for relative_path in REQUIRED_CANONICAL_FILES:
        text = read_text(relative_path)
        require(
            CANONICAL_DEFINITION in text,
            f"canonical definition missing from {relative_path}",
        )


def check_html_metadata() -> None:
    for relative_path in HTML_FILES:
        text = read_text(relative_path)
        lower = text.lower()
        require("<title>" in lower and "</title>" in lower, f"title missing in {relative_path}")
        require('name="description"' in lower, f"meta description missing in {relative_path}")
        require('rel="canonical"' in lower, f"canonical link missing in {relative_path}")
        require('property="og:title"' in lower, f"og:title missing in {relative_path}")
        if relative_path.endswith("index.html"):
            require(
                'type="application/ld+json"' in lower,
                f"JSON-LD structured data missing in {relative_path}",
            )
            require('"@type": "organization"' in lower, f"Organization JSON-LD missing in {relative_path}")
            require(
                '"@type": "softwareapplication"' in lower,
                f"SoftwareApplication JSON-LD missing in {relative_path}",
            )
        else:
            require("<script" not in lower, f"{relative_path} must remain script-free")
        require(
            CANONICAL_DEFINITION in text,
            f"visible/structured canonical definition missing in {relative_path}",
        )
        require(
            "not tracing, not prompt debugging, not production monitoring" in lower,
            f"visible boundary copy missing in {relative_path}",
        )


def check_no_private_core_exposure() -> None:
    for relative_path in PRIVATE_CORE_SCAN_SURFACES:
        text = read_text(relative_path)
        for token in FORBIDDEN_PRIVATE_CORE_TOKENS:
            require(token not in text, f"forbidden private-core token {token!r} in {relative_path}")


def check_no_overclaim() -> None:
    for relative_path in EXTERNAL_SURFACES:
        compact = read_text(relative_path).replace(" ", "").lower()
        normal = read_text(relative_path).lower()
        for token in FORBIDDEN_OVERCLAIM_TOKENS:
            probe = token.replace(" ", "").lower()
            require(
                probe not in compact and token.lower() not in normal,
                f"forbidden overclaim token {token!r} in {relative_path}",
            )


def check_runtime_paths_not_modified() -> None:
    report = read_text("docs/canonical/SAEE_EXTERNAL_CANONICAL_SYNC_REPORT.md")
    for required_boundary in [
        "`runtime_modified=false`",
        "`backend_modified=false`",
        "`kernel_modified=false`",
        "`api_schema_modified=false`",
    ]:
        require(required_boundary in report, f"missing boundary in report: {required_boundary}")

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--", *FORBIDDEN_RUNTIME_PATHS],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise AssertionError(f"unable to inspect runtime path diff: {exc}") from exc

    changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    require(not changed, f"forbidden runtime/backend/kernel diff detected: {changed}")


def check_external_publish_status() -> None:
    required = "external_canonical_sync_github_pages_release_zenodo_published_profile_social_pending"
    for relative_path in [
        "README.md",
        "PROJECT_STATUS.md",
        "docs/canonical/SAEE_EXTERNAL_CANONICAL_SYNC_REPORT.md",
        "agent-index.json",
    ]:
        require(required in read_text(relative_path), f"final status missing in {relative_path}")


def main() -> int:
    try:
        check_json_files()
        check_canonical_definition()
        check_html_metadata()
        check_no_private_core_exposure()
        check_no_overclaim()
        check_runtime_paths_not_modified()
        check_external_publish_status()
    except AssertionError as exc:
        print(f"SAEE_EXTERNAL_CANONICAL_SYNC_SMOKE: FAIL {exc}")
        return 1

    print("SAEE_EXTERNAL_CANONICAL_SYNC_SMOKE: PASS")
    print("FINAL STATUS STRING:")
    print("external_canonical_sync_github_pages_release_zenodo_published_profile_social_pending")
    return 0


if __name__ == "__main__":
    sys.exit(main())
