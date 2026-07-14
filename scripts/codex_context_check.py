#!/usr/bin/env python3
"""Validate the local SAEE Codex efficiency context layer."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ".codex/context.md",
    ".codex/architecture.md",
    ".codex/current_state.md",
    ".codex/rules.md",
    ".codex/task_template.md",
    ".codex/validation_commands.md",
    ".codex/change_policy.md",
    ".codex/task_queue/README.md",
    "scripts/codex_prepare_task.py",
    "docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
    "governance/README.md",
    "capability-package/manifest.json",
    "AGENTS.md",
    "README.md",
    "llms.txt",
]

REQUIRED_DIRS = [
    ".codex/task_queue",
    "governance/registry",
]

REQUIRED_TOKENS = {
    ".codex/context.md": [
        "SAEE Project Context",
        "SAEE Development Constitution v1.1",
        "Architecture-governed AI engineering assistant",
        "受架构治理",
        "AI 工程助手",
        "Silicon-Amplified Evolutionary Ecology",
        "Digital Biosphere Evolution Engine",
        "Agent Readiness is an external capability",
        "Development authority:",
        "governance/README.md",
        "capability-package/manifest.json#canonical_inventory",
        "not a second capability fact",
        "automatic approval",
        "automatic deployment",
        "automatic decision authority",
        "Input",
        "Simulation",
        "Competition",
        "Scoring",
        "Decision",
        "Do not confuse SAEE with",
        "tracing tool",
        "prompt evaluation tool",
        "monitoring dashboard",
    ],
    ".codex/architecture.md": [
        "System Architecture",
        "saee_backend/",
        "phase_b_product/",
        "docs/",
        "Never modify without explicit instruction",
        "private core",
        "hidden evaluation logic",
    ],
    ".codex/current_state.md": [
        "SAEE Current State",
        "External canonical sync completed",
        "recommendation surface",
        "production_ready=false",
        "customer_validated=false",
        "private_core_exposed=false",
    ],
    ".codex/rules.md": [
        "SAEE Codex Rules",
        "Allowed",
        "Forbidden",
        "Never claim",
        "production ready",
        "customer validated",
        "external validated",
    ],
    ".codex/task_template.md": [
        "Task ID",
        "Objective",
        "Files allowed to modify",
        "Files forbidden",
        "Validation command",
        "Boundary",
    ],
    ".codex/validation_commands.md": [
        "make check",
        "python3 scripts/mainline_guard.py",
        "python3 scripts/<specific_smoke_test>.py",
    ],
    ".codex/change_policy.md": [
        "Small change first",
        "One task",
        "One objective",
    ],
    "AGENTS.md": [
        "SAEE Development Constitution v1.1",
        "Read the constitution first, the governance registries second, and the",
        "canonical capability inventory third",
        "not a second",
        "capability fact source",
    ],
    "README.md": [
        "SAEE Development Constitution v1.1",
        "Phase 0 治理入口",
        "capability-package/manifest.json#canonical_inventory",
        "不是第二个能力事实真源",
    ],
    "llms.txt": [
        "Development constitution: docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
        "Phase 0 governance entry: governance/README.md",
        "Governance startup rule: read the development constitution, then governance registries, then capability-package/manifest.json#canonical_inventory",
        "not a second capability fact source",
    ],
}

DEPRECATED_CONTEXT_PHRASES = [
    "AI agent long-term stability evaluation",
    "SAEE is an Agent Readiness Infrastructure",
]

SINGLETON_AUTHORITY_MARKERS = [
    "Development authority:",
    "Canonical capability facts:",
    "Governance mapping boundary:",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_CODEX_CONTEXT_CHECK: FAIL: {message}")


def validate_context_contract(text: str) -> None:
    """Validate identity boundaries that token-presence checks cannot express."""
    deprecated = [phrase for phrase in DEPRECATED_CONTEXT_PHRASES if phrase in text]
    if deprecated:
        fail(".codex/context.md contains deprecated identity phrases: " + ", ".join(deprecated))

    duplicated = [
        marker for marker in SINGLETON_AUTHORITY_MARKERS if text.count(marker) != 1
    ]
    if duplicated:
        fail(
            ".codex/context.md authority markers must occur exactly once: "
            + ", ".join(duplicated)
        )


def main() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing {rel}")

    missing_dirs = [rel for rel in REQUIRED_DIRS if not (ROOT / rel).is_dir()]
    if missing_dirs:
        fail("missing directories: " + ", ".join(missing_dirs))

    for rel, tokens in REQUIRED_TOKENS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        missing = [token for token in tokens if token not in text]
        if missing:
            fail(f"{rel} missing tokens: {', '.join(missing)}")

    validate_context_contract((ROOT / ".codex/context.md").read_text(encoding="utf-8"))

    prepare_script = (ROOT / "scripts/codex_prepare_task.py").read_text(encoding="utf-8")
    forbidden = ["requests.", "urllib.request", "httpx.", "webbrowser", "selenium"]
    for token in forbidden:
        if token in prepare_script:
            fail(f"codex_prepare_task.py must not call external services: {token}")

    index_path = ROOT / "agent-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = index.get("codex_efficiency_layer_v1_0")
    if not isinstance(entry, dict):
        fail("agent-index.json missing codex_efficiency_layer_v1_0")
    expected_false = {
        "product_functionality_changed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_behavior_modified": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
        "customer_validated_claim": False,
        "external_validation_claim": False,
    }
    for key, value in expected_false.items():
        if entry.get(key) is not value:
            fail(f"agent-index.json codex_efficiency_layer_v1_0 {key} must be {value}")

    print("SAEE_CODEX_CONTEXT_CHECK: PASS")


if __name__ == "__main__":
    main()
