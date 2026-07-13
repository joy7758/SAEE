#!/usr/bin/env python3
"""Offline deterministic validation for the SAEE certificate renewal status."""

from __future__ import annotations

import ast
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "agent-interface/operations/saee-certificate-renewal-status.v0.1.json"
OPERATION_PATH = ROOT / "docs/operations/SAEE_CERTIFICATE_RENEWAL_OPERATION.md"
PLAN_PATH = ROOT / "docs/operations/SAEE_CERTIFICATE_RENEWAL_PLAN.md"
REPORT_PATH = ROOT / "SAEE_HTTPS_RENEWAL_RELIABILITY_FIX_REPORT.md"

EXPECTED_TRUTH = {
    "renewal_reliability_fixed": True,
    "certificate_renewal_dry_run_passed": True,
    "security_certification_provided": False,
    "production_ready": False,
    "commercial_service": False,
    "agent_callable_runtime": False,
    "tool_capability_gate_released": False,
    "ready_for_tool_capability_gate_review": True,
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SECRET_VALUE_PATTERNS = (
    re.compile(r"bce-v3/[A-Za-z0-9/+_=.-]{12,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9/+_.=-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


class RenewalSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise RenewalSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def validate_status(status: dict[str, Any]) -> dict[str, int]:
    require(status.get("saee_certificate_renewal_status_v0_1") is True, "status marker missing")
    require(status.get("status_version") == "0.1", "status version invalid")
    require(status.get("domain") == "redcrag.cn", "domain invalid")
    require(status.get("canonical_url") == "https://redcrag.cn/", "canonical URL invalid")

    certificate = status.get("current_certificate", {})
    require(certificate.get("valid") is True, "current certificate validity missing")
    require(certificate.get("subject") == "CN=redcrag.cn", "certificate subject invalid")
    require(certificate.get("issuer") == "Let's Encrypt YE2", "certificate issuer invalid")
    require(certificate.get("not_after") == "2026-10-09T11:55:43Z", "certificate expiry missing")
    require(certificate.get("replaced_by_this_task") is False, "active certificate replaced")

    renewal = status.get("renewal_configuration", {})
    require(renewal.get("challenge_type") == "webroot_http_01", "challenge method changed")
    require(renewal.get("renewal_config_declared_path") == "/etc/letsencrypt/renewal/redcrag.cn.conf", "renewal config declaration missing")
    require(renewal.get("webroot_declared_path") == "/var/www/letsencrypt", "webroot declaration missing")
    require(renewal.get("timer_enabled") is True and renewal.get("timer_active") is True, "renewal timer invalid")
    require(renewal.get("nginx_reload_hook_configured") is True, "reload hook missing")
    for field in ("nginx_config_changed_by_this_task", "certbot_config_changed_by_this_task", "renewal_mode_switched"):
        require(renewal.get(field) is False, f"configuration unexpectedly changed: {field}")

    dry_run = status.get("dry_run", {})
    require(dry_run.get("command") == "certbot renew --dry-run --no-random-sleep-on-renew", "dry-run command missing")
    require(dry_run.get("passed") is True, "dry-run success missing")
    require(dry_run.get("current_failure") is None, "current failure must be empty")
    require(dry_run.get("previous_failure_type") == "unauthorized", "historical failure type missing")
    require(dry_run.get("previous_failure_reason") == "secondary_validation_received_baidu_domainwall_http_403", "historical failure reason missing")
    require(dry_run.get("success_evidence") == "all_simulated_renewals_succeeded", "dry-run success evidence missing")
    require(dry_run.get("server_route_locally_validated") is True, "local route validation missing")
    require(dry_run.get("baidu_cloud_icp_access_confirmed_by_task") is False, "Baidu access status overstated")

    solution = status.get("chosen_solution", {})
    require(solution.get("solution_id") == "RETAIN_HTTP_01_AFTER_SUCCESSFUL_STAGING_RETRY", "chosen solution invalid")
    require(solution.get("solution_implemented") is True, "solution implementation missing")
    require(solution.get("configuration_change_required") is False, "unexpected configuration change required")
    require(solution.get("requires_dns_credential") is False, "chosen solution requires unexpected credential")
    require(solution.get("acceptance_criteria_met") is True, "acceptance criteria not met")

    fallback = status.get("dns_01_fallback", {})
    require(fallback.get("evaluated") is True, "DNS-01 not evaluated")
    for field in ("configured", "credential_available", "credential_stored"):
        require(fallback.get(field) is False, f"DNS-01 boundary invalid: {field}")
    require(fallback.get("dedicated_minimum_permission_credential_required") is True, "minimum permission rule missing")
    require(fallback.get("unrelated_api_key_reuse_allowed") is False, "unrelated credential reuse allowed")

    hashes = status.get("configuration_hashes", {})
    require(set(hashes) == {"nginx_conf_sha256", "renewal_conf_sha256", "reload_hook_sha256"}, "configuration hash set invalid")
    require(all(SHA256_RE.fullmatch(value or "") for value in hashes.values()), "configuration hash invalid")

    truth = status.get("truth_boundary", {})
    require(truth == EXPECTED_TRUTH, "truth boundary invalid")

    serialized = json.dumps(status, ensure_ascii=False)
    require(not any(pattern.search(serialized) for pattern in SECRET_VALUE_PATTERNS), "credential or key material exposed")
    return {
        "certificate_metadata_present": 1,
        "renewal_config_declared": 1,
        "dry_run_status_recorded": 1,
        "credential_values_exposed": 0,
        "private_keys_exposed": 0,
    }


def expect_invalid(status: dict[str, Any], label: str) -> None:
    try:
        validate_status(status)
    except RenewalSmokeError:
        return
    raise RenewalSmokeError(f"invalid status accepted: {label}")


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
        for path in (STATUS_PATH, OPERATION_PATH, PLAN_PATH, REPORT_PATH):
            require(path.is_file(), f"required file missing: {path}")
        validate_script_boundary()

        texts = [path.read_text(encoding="utf-8") for path in (OPERATION_PATH, PLAN_PATH, REPORT_PATH)]
        combined = "\n".join(texts)
        require("RETAIN_HTTP_01_AFTER_SUCCESSFUL_STAGING_RETRY" in combined, "chosen solution not documented")
        require("certificate_renewal_dry_run_passed=true" in combined, "dry-run truth missing")
        require("private_key_output_allowed=false" in combined, "private-key output boundary missing")
        require(not any(pattern.search(combined) for pattern in SECRET_VALUE_PATTERNS), "credential or private-key value exposed in documents")

        status = read_json(STATUS_PATH)
        baseline = validate_status(status)

        invalid = copy.deepcopy(status)
        invalid["dry_run"]["passed"] = False
        expect_invalid(invalid, "dry-run success removed")
        invalid = copy.deepcopy(status)
        invalid["dns_01_fallback"]["credential_stored"] = True
        expect_invalid(invalid, "credential stored")
        invalid = copy.deepcopy(status)
        invalid["configuration_hashes"].pop("renewal_conf_sha256")
        expect_invalid(invalid, "renewal hash missing")
        invalid = copy.deepcopy(status)
        invalid["chosen_solution"]["solution_implemented"] = False
        expect_invalid(invalid, "solution implementation missing")

        runs = [validate_status(copy.deepcopy(status)) for _ in range(5)]
        require(all(run == baseline for run in runs), "non-deterministic validation")
    except (RenewalSmokeError, json.JSONDecodeError, OSError, SyntaxError) as exc:
        print(f"SAEE_CERTIFICATE_RENEWAL_SMOKE: FAIL: {exc}", file=sys.stderr)
        return 1

    print("SAEE_CERTIFICATE_RENEWAL_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=4/4")
    print("deterministic_runs=5/5")
    for key, value in baseline.items():
        print(f"{key}={value}")
    print("certificate_renewal_dry_run_passed=true")
    print("renewal_reliability_fixed=true")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
