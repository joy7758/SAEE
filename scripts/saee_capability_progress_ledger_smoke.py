#!/usr/bin/env python3
"""Keep SAEE capability progress and duplicate-build guidance synchronized."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.capability_runtime.canonical_capability_inventory import (  # noqa: E402
    CANONICAL_SOURCE,
    load_canonical_inventory,
)

START_FILE = "AGENTS.md"
INDEX_FILE = "agent-index.json"
LLMS_FILE = "llms.txt"
REPORT_FILE = "reports/SAEE_CAPABILITY_ASSESSMENT_REPORT.md"
GATE_FILE = "docs/strategy/SAEE_CAPABILITY_PROGRESS_LEDGER_RECOMMENDATION_GATE.md"
VALIDATOR_FILE = "scripts/saee_capability_progress_ledger_smoke.py"
CURRENT_PR = "Canonical Capability Inventory, Routing and Deprecation Map v1"
ROADMAP_REFERENCE = "reports/SAEE_CAPABILITY_ASSESSMENT_REPORT.md#recommended-next-prs"

LEGACY_OTEL_NEXT_PRS = {
    "Add OpenTelemetry-to-SAEE Evidence Adequacy Mapping",
    "Add OpenTelemetry-to-SAEE resource event mapping",
}

def load_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def active_recommendations(value: Any, path: str = "root") -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "recommended_next_pr" and isinstance(child, str):
                results.append((child_path, child))
            results.extend(active_recommendations(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            results.extend(active_recommendations(child, f"{path}[{index}]"))
    return results


def validate(
    index: dict[str, Any],
    agents: str,
    llms: str,
    report: str,
    gate: str,
) -> list[str]:
    errors: list[str] = []
    ledger = index.get("capability_progress_ledger_v1")
    if not isinstance(ledger, dict):
        return ["agent-index.json missing capability_progress_ledger_v1"]

    expected_ledger_values = {
        "agent_start_file": START_FILE,
        "assessment_report": REPORT_FILE,
        "canonical_source": CANONICAL_SOURCE,
        "completed_governance_change": CURRENT_PR,
        "duplicate_build_prevention": True,
        "recommendation_gate": GATE_FILE,
        "smoke_command": f"python3 {VALIDATOR_FILE}",
        "status": "active_canonical_machine_ledger",
    }
    for key, expected in expected_ledger_values.items():
        if ledger.get(key) != expected:
            errors.append(f"ledger.{key} must equal {expected!r}")

    ledger_updated = ledger.get("ledger_updated")
    if not isinstance(ledger_updated, str) or not ledger_updated:
        errors.append("ledger.ledger_updated must be a non-empty date string")
    else:
        if f"ledger_updated={ledger_updated}" not in agents:
            errors.append("AGENTS.md ledger_updated does not match machine ledger")
        if f"Capability progress ledger updated: {ledger_updated}" not in llms:
            errors.append("llms.txt ledger date does not match machine ledger")

    assessment_base_commit = ledger.get("assessment_base_commit")
    if not isinstance(assessment_base_commit, str) or not assessment_base_commit:
        errors.append("ledger.assessment_base_commit must be a non-empty commit id")
    elif f"assessment_base_commit={assessment_base_commit}" not in agents:
        errors.append("AGENTS.md assessment base does not match machine ledger")

    canonical = load_canonical_inventory()
    expected_status_projection = {
        item["capability_id"]: {
            "implementation_status": item["implementation_status"],
            "lifecycle_status": item["lifecycle_status"],
        }
        for item in canonical["capabilities"]
    }
    if ledger.get("capability_status_projection") != expected_status_projection:
        errors.append("ledger.capability_status_projection must match canonical inventory")
    roadmap_policy = ledger.get("roadmap_policy", {})
    if roadmap_policy != {
        "capability_facts_authority": CANONICAL_SOURCE,
        "recommended_next_pr_field": "deprecated_compatibility_only",
        "replacement": ROADMAP_REFERENCE,
        "roadmap_authority": False,
    }:
        errors.append("ledger.roadmap_policy must separate capability facts from roadmap advice")

    truth_boundary = ledger.get("truth_boundary", {})
    for key in (
        "customer_validated",
        "external_integration_validated",
        "product_launched",
        "production_ready",
        "public_service",
    ):
        if truth_boundary.get(key) is not False:
            errors.append(f"ledger.truth_boundary.{key} must remain false")

    superseded = set(ledger.get("superseded_active_next_pr_instructions", []))
    if superseded != LEGACY_OTEL_NEXT_PRS:
        errors.append("ledger superseded OTEL next-PR set is incomplete or changed")

    for path, recommendation in active_recommendations(index):
        if recommendation in LEGACY_OTEL_NEXT_PRS | {CURRENT_PR}:
            errors.append(f"completed work is active at {path}")

    evidence_profile = index.get("evidence_adequacy_profile_v0_1", {})
    resource_receipt = index.get("external_resource_resolution_receipt_v0_1", {})
    otel_mapping = index.get("otel_candidate_evidence_mapping_v0_1", {})
    expected_superseded = (
        (evidence_profile, "Add OpenTelemetry-to-SAEE Evidence Adequacy Mapping"),
        (resource_receipt, "Add OpenTelemetry-to-SAEE resource event mapping"),
    )
    for record, expected in expected_superseded:
        if record.get("superseded_recommended_next_pr") != expected:
            errors.append(f"missing superseded OTEL history: {expected}")
        if record.get("recommended_next_pr") != ROADMAP_REFERENCE:
            errors.append(f"superseded OTEL record must route to roadmap: {expected}")
        if record.get("recommended_next_pr_status") != "deprecated_compatibility_only":
            errors.append(f"superseded OTEL roadmap field must be deprecated: {expected}")

    if otel_mapping.get("recommended_next_pr") != ROADMAP_REFERENCE:
        errors.append("canonical OTEL mapping roadmap field must route to roadmap")
    if otel_mapping.get("recommended_next_pr_status") != "deprecated_compatibility_only":
        errors.append("canonical OTEL mapping roadmap field must be deprecated")
    if otel_mapping.get("status") != "implemented_local_offline_synthetic_candidate_mapping_only":
        errors.append("canonical OTEL mapping implementation status drifted")
    if otel_mapping.get("opentelemetry_sdk_imported") is not False:
        errors.append("OTEL SDK must not be claimed as imported")
    if otel_mapping.get("trace_is_evidence") is not False:
        errors.append("trace must not be claimed as evidence")

    required_agent_tokens = (
        "## Capability Progress Ledger And Duplicate-Build Prevention",
        f"canonical_capability_source={CANONICAL_SOURCE}",
        f"machine_ledger_projection={INDEX_FILE}#capability_progress_ledger_v1",
        f"ledger_validator={VALIDATOR_FILE}",
        f"completed_governance_change={CURRENT_PR}",
        f"roadmap_reference={ROADMAP_REFERENCE}",
        "do_not_rebuild=synthetic OpenTelemetry-style candidate evidence mapping",
        "Mandatory ledger synchronization",
    )
    for token in required_agent_tokens:
        if token not in agents:
            errors.append(f"AGENTS.md missing ledger token: {token}")

    required_llms_tokens = (
        f"Canonical capability source: {CANONICAL_SOURCE}",
        f"Machine capability ledger projection: {INDEX_FILE}#capability_progress_ledger_v1",
        f"Detailed capability assessment: {REPORT_FILE}",
        f"Capability ledger recommendation gate: {GATE_FILE}",
        f"Capability ledger validation: python3 {VALIDATOR_FILE}",
        f"Completed governance change: {CURRENT_PR}.",
        "Duplicate-build prohibition: do not rebuild synthetic OpenTelemetry-style candidate evidence mapping",
    )
    for token in required_llms_tokens:
        if token not in llms:
            errors.append(f"llms.txt missing ledger token: {token}")

    required_report_tokens = (
        "# SAEE Architecture Capability Assessment Report",
        "Post-assessment ledger sync:",
        CURRENT_PR,
    )
    for token in required_report_tokens:
        if token not in report:
            errors.append(f"assessment report missing ledger token: {token}")

    for token in ("## Initial Result", "## Final Result", "`recommend`"):
        if token not in gate:
            errors.append(f"recommendation gate missing token: {token}")

    return errors


def main() -> int:
    required_paths = (START_FILE, INDEX_FILE, LLMS_FILE, REPORT_FILE, GATE_FILE)
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    if missing:
        print("SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: FAIL")
        for path in missing:
            print(f"- missing required surface: {path}")
        return 1

    index = json.loads(load_text(INDEX_FILE))
    agents = load_text(START_FILE)
    llms = load_text(LLMS_FILE)
    report = load_text(REPORT_FILE)
    gate = load_text(GATE_FILE)

    errors = validate(index, agents, llms, report, gate)
    if errors:
        print("SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    negative_cases: list[tuple[str, dict[str, Any], str, str, str, str]] = []
    duplicate_disabled = copy.deepcopy(index)
    duplicate_disabled["capability_progress_ledger_v1"]["duplicate_build_prevention"] = False
    negative_cases.append(("duplicate prevention disabled", duplicate_disabled, agents, llms, report, gate))

    false_otlp_claim = copy.deepcopy(index)
    false_otlp_claim["capability_progress_ledger_v1"]["capability_status_projection"]["saee.otel_sdk_or_otlp_ingestion"]["implementation_status"] = "implemented"
    negative_cases.append(("false OTLP claim", false_otlp_claim, agents, llms, report, gate))

    legacy_active = copy.deepcopy(index)
    legacy_active["evidence_adequacy_profile_v0_1"]["recommended_next_pr"] = "Add OpenTelemetry-to-SAEE Evidence Adequacy Mapping"
    negative_cases.append(("legacy OTEL next PR active", legacy_active, agents, llms, report, gate))

    negative_cases.append(("AGENTS startup token removed", index, agents.replace("ledger_validator=", "validator_removed="), llms, report, gate))
    negative_cases.append(("llms ledger route removed", index, agents, llms.replace("Canonical capability source:", "Removed source:"), report, gate))

    undetected = [name for name, *state in negative_cases if not validate(*state)]
    if undetected:
        print("SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: FAIL")
        for name in undetected:
            print(f"- negative case was not rejected: {name}")
        return 1

    print("SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: PASS")
    print("surfaces=5/5")
    capability_count = len(load_canonical_inventory()["capabilities"])
    print(f"capability_statuses={capability_count}/{capability_count}")
    print("active_legacy_otel_next_pr=0")
    print(f"superseded_legacy_otel_next_pr={len(LEGACY_OTEL_NEXT_PRS)}/{len(LEGACY_OTEL_NEXT_PRS)}")
    print(f"negative_cases={len(negative_cases)}/{len(negative_cases)}")
    print("duplicate_build_prevention=true")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
