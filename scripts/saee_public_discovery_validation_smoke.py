#!/usr/bin/env python3
"""Offline deterministic checks for SAEE Public Trust and Discovery Validation v0.1."""

from __future__ import annotations

import ast
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "agent-interface/discovery/saee-public-discovery-validation.v0.1.json"
PROTOCOL_PATH = ROOT / "docs/architecture/SAEE_AGENT_DISCOVERY_VALIDATION.md"
RENEWAL_PATH = ROOT / "docs/operations/SAEE_CERTIFICATE_RENEWAL_PLAN.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PUBLIC_TRUST_DISCOVERY_VALIDATION_RECOMMENDATION_GATE.md"
PUBLIC_ROOT = ROOT / "public-release/saee-agent-discovery-v0.1"
PUBLIC_INDEX_PATH = PUBLIC_ROOT / ".well-known/agent-index.json"
PUBLIC_CAPABILITY_PATH = PUBLIC_ROOT / "capabilities/saee-capability-manifest.v0.1.json"

EXPECTED_ENDPOINTS = {
    "human_entry": ("https://redcrag.cn/", "text/html"),
    "llm_entry": ("https://redcrag.cn/llms.txt", "text/plain"),
    "agent_index": ("https://redcrag.cn/.well-known/agent-index.json", "application/json"),
    "capability_manifest": (
        "https://redcrag.cn/capabilities/saee-capability-manifest.v0.1.json",
        "application/json",
    ),
}
EXPECTED_QUESTIONS = {
    "WHAT_IS_SAEE",
    "WHEN_SHOULD_SAEE_BE_USED",
    "WHEN_SHOULD_SAEE_NOT_BE_USED",
    "WHAT_INPUTS_ARE_REQUIRED",
    "WHAT_OUTPUTS_ARE_PRODUCED",
    "WHAT_LIMITATIONS_EXIST",
}
FALSE_TRUTH_FIELDS = {
    "external_agent_validation_completed",
    "search_indexing_verified",
    "agent_adoption_established",
    "agent_recommendation_established",
    "market_validation_completed",
    "external_trust_established",
    "production_ready",
    "security_certification_provided",
}
SENSITIVE_PATTERNS = (
    re.compile(r"bce-v3/[A-Za-z0-9/+_=.-]{12,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9/+_.=-]{12,}"),
)


class DiscoveryValidationError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise DiscoveryValidationError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def local_ref_exists(ref: str) -> bool:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def validate_record(record: dict[str, Any]) -> dict[str, int]:
    require(record.get("saee_public_discovery_validation_v0_1") is True, "record marker missing")
    require(record.get("validation_version") == "0.1", "validation version invalid")
    require(record.get("canonical_url") == "https://redcrag.cn/", "canonical URL invalid")
    require(record.get("https_enabled") is True, "HTTPS truth invalid")
    require(record.get("agent_endpoints_available") is True, "endpoint availability truth invalid")

    endpoints = record.get("endpoints")
    require(isinstance(endpoints, list) and len(endpoints) == 4, "endpoint count invalid")
    endpoint_map = {item.get("role"): item for item in endpoints}
    require(set(endpoint_map) == set(EXPECTED_ENDPOINTS), "endpoint roles invalid")
    for role, (url, media_type) in EXPECTED_ENDPOINTS.items():
        item = endpoint_map[role]
        require(item.get("url") == url, f"endpoint URL invalid: {role}")
        require(item.get("expected_status") == 200, f"endpoint status invalid: {role}")
        require(item.get("expected_media_type") == media_type, f"endpoint media type invalid: {role}")
        require(item.get("observed_available") is True, f"endpoint snapshot missing: {role}")

    protocol = record.get("agent_understanding_protocol", {})
    require(protocol.get("question_count") == 6, "question count invalid")
    require(set(protocol.get("questions", [])) == EXPECTED_QUESTIONS, "question coverage invalid")
    require(protocol.get("executed_by_external_agent") is False, "external Agent execution overclaimed")
    require(local_ref_exists(protocol.get("protocol_ref", "")), "protocol reference missing")

    metadata = record.get("metadata_consistency", {})
    require(metadata.get("capability_id") == "saee-evidence-adequacy", "capability identity invalid")
    require(metadata.get("stage") == "research_prototype", "stage overclaimed")
    for field in ("canonical_urls_consistent", "capability_ids_consistent", "truth_boundaries_consistent"):
        require(metadata.get(field) is True, f"metadata consistency missing: {field}")
    require(metadata.get("internal_path_matches") == 0, "internal paths present")
    require(metadata.get("sensitive_value_matches") == 0, "sensitive values present")

    renewal = record.get("certificate_renewal", {})
    require(renewal.get("active_certificate_valid") is True, "active certificate status invalid")
    require(renewal.get("renewal_timer_enabled") is True, "renewal timer missing")
    require(renewal.get("renewal_dry_run_passed") is False, "renewal dry-run overstated")
    require(renewal.get("http_01_failure") == "secondary_validation_received_baidu_domainwall_http_403", "failure cause missing")
    require(renewal.get("dns_01_possible") is True, "DNS-01 analysis missing")
    require(renewal.get("renewal_mode_switched") is False, "renewal mode changed by protocol")
    require(renewal.get("credentials_stored_by_this_task") is False, "credential boundary invalid")
    require(local_ref_exists(renewal.get("plan_ref", "")), "renewal plan reference missing")

    truth = record.get("truth_boundary", {})
    require(set(truth) == FALSE_TRUTH_FIELDS, "truth boundary shape invalid")
    require(all(value is False for value in truth.values()), "unsupported truth promotion")

    next_gate = record.get("next_phase_gate", {})
    require(next_gate.get("discovery_trust_layer_stable") is False, "trust stability overstated")
    require(next_gate.get("blocking_condition") == "certificate_renewal_dry_run_not_reliable", "next phase blocker missing")
    require(next_gate.get("eventual_next_phase") == "SAEE Agent-Native Tool Capability Prototype v0.1", "eventual next phase invalid")
    require(next_gate.get("tool_capability_started") is False, "Tool Capability started early")

    public_index = read_json(PUBLIC_INDEX_PATH)
    public_capability = read_json(PUBLIC_CAPABILITY_PATH)
    require(public_index.get("base_url") == record["canonical_url"], "public index canonical mismatch")
    require(public_index.get("capability", {}).get("id") == metadata["capability_id"], "public index capability mismatch")
    require(public_capability.get("capability_id") == metadata["capability_id"], "public manifest capability mismatch")
    require(public_capability.get("stage") == metadata["stage"], "public manifest stage mismatch")
    require(public_capability.get("truth_boundary", {}).get("production_ready") is False, "public production boundary invalid")

    return {
        "endpoint_count": len(endpoints),
        "understanding_questions": len(protocol["questions"]),
        "internal_path_matches": metadata["internal_path_matches"],
        "sensitive_value_matches": metadata["sensitive_value_matches"],
    }


def expect_invalid(record: dict[str, Any], label: str) -> None:
    try:
        validate_record(record)
    except DiscoveryValidationError:
        return
    raise DiscoveryValidationError(f"invalid record accepted: {label}")


def validate_script_boundary() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = {
        node.names[0].name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    }
    imports.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    require(not imports.intersection({"socket", "subprocess", "urllib", "requests", "httpx"}), "network or subprocess import found")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            require(node.func.id not in {"eval", "exec", "compile", "__import__"}, "dynamic execution found")


def main() -> int:
    try:
        for path in (RECORD_PATH, PROTOCOL_PATH, RENEWAL_PATH, GATE_PATH, PUBLIC_INDEX_PATH, PUBLIC_CAPABILITY_PATH):
            require(path.is_file(), f"required file missing: {path}")
        validate_script_boundary()

        protocol_text = PROTOCOL_PATH.read_text(encoding="utf-8")
        renewal_text = RENEWAL_PATH.read_text(encoding="utf-8")
        require(all(question in protocol_text for question in EXPECTED_QUESTIONS), "protocol questions not machine discoverable")
        require("external_agent_validation_completed=false" in protocol_text, "external validation boundary missing")
        require("domainwall.cloud.baidu.com" in renewal_text, "HTTP-01 failure not documented")
        require("_acme-challenge.redcrag.cn" in renewal_text, "DNS-01 record not documented")
        require("existing_Qianfan_key_reuse_for_dns=false" in renewal_text, "credential reuse boundary missing")
        require(not any(pattern.search(renewal_text) for pattern in SENSITIVE_PATTERNS), "credential value found in renewal plan")

        record = read_json(RECORD_PATH)
        baseline = validate_record(record)

        invalid = copy.deepcopy(record)
        invalid["canonical_url"] = "http://redcrag.cn/"
        expect_invalid(invalid, "non-HTTPS canonical")
        invalid = copy.deepcopy(record)
        invalid["https_enabled"] = False
        expect_invalid(invalid, "HTTPS disabled")
        invalid = copy.deepcopy(record)
        invalid["endpoints"] = invalid["endpoints"][:-1]
        expect_invalid(invalid, "endpoint missing")
        invalid = copy.deepcopy(record)
        invalid["agent_understanding_protocol"]["executed_by_external_agent"] = True
        expect_invalid(invalid, "external Agent overclaim")
        invalid = copy.deepcopy(record)
        invalid["truth_boundary"]["search_indexing_verified"] = True
        expect_invalid(invalid, "search indexing overclaim")
        invalid = copy.deepcopy(record)
        invalid["truth_boundary"]["production_ready"] = True
        expect_invalid(invalid, "production overclaim")

        runs = [validate_record(copy.deepcopy(record)) for _ in range(5)]
        require(all(run == baseline for run in runs), "non-deterministic validation")
    except (DiscoveryValidationError, json.JSONDecodeError, OSError, SyntaxError) as exc:
        print(f"SAEE_PUBLIC_DISCOVERY_VALIDATION_SMOKE: FAIL: {exc}", file=sys.stderr)
        return 1

    print("SAEE_PUBLIC_DISCOVERY_VALIDATION_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=6/6")
    print("deterministic_runs=5/5")
    for key, value in baseline.items():
        print(f"{key}={value}")
    print("external_agent_validation_completed=false")
    print("search_indexing_verified=false")
    print("certificate_renewal_dry_run_passed=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
