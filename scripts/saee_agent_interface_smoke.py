#!/usr/bin/env python3
"""Validate the compact agent-first SAEE discovery and invocation surface."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)
from jsonschema import Draft202012Validator, RefResolver


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "agent-interface/agent-manifest.json"
MANIFEST_SCHEMA = ROOT / "agent-interface/schemas/saee-agent-manifest.schema.json"
TOOL_CONTRACT = ROOT / "agent-interface/tool-contract.json"
REQUEST = ROOT / "agent-interface/examples/evaluation-request.json"
EXAMPLE_RECEIPT = ROOT / "agent-interface/examples/evaluation-receipt.json"
RECEIPT_SCHEMA = ROOT / "agent-interface/schemas/evaluation-receipt.schema.json"
ERROR_SCHEMA = ROOT / "agent-interface/schemas/agent-error.schema.json"
PUBLIC_SCHEMA = ROOT / "schemas/saee_mvp_api.schema.json"
BACKEND_SCHEMA = ROOT / "saee_backend/schemas/saee_mvp_api.schema.json"
CLI = ROOT / "scripts/saee_agent_cli.py"
LANDING_JS = ROOT / "phase_b_product/landing/app.js"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_AGENT_INTERFACE_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def validate_with_root(instance: object, root_schema: dict, definition: str) -> None:
    resolver = RefResolver.from_schema(root_schema)
    validator = Draft202012Validator({"$ref": f"#/$defs/{definition}"}, resolver=resolver)
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    require(not errors, f"{definition} schema errors: {[error.message for error in errors]}")


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def main() -> None:
    manifest = read_json(MANIFEST)
    manifest_schema = read_json(MANIFEST_SCHEMA)
    Draft202012Validator(manifest_schema).validate(manifest)
    require(MANIFEST.stat().st_size < 10_000, "manifest must stay below 10 KB")
    require(len(MANIFEST.read_text(encoding="utf-8").splitlines()) < 200, "manifest must stay below 200 lines")
    require(manifest["current_status"]["default_evaluation_mode"] == "synthetic_descriptor_simulation", "default mode mismatch")
    require(manifest["current_status"]["observed_agent_trace_evaluation_available"] is True, "observed trace adapter must be discoverable")
    require(manifest["current_status"]["observed_trace_adapter_validation_status"] == "recommend_3_of_3_agents_blockers_0", "observed trace validation status")
    require(manifest["current_status"]["mcp_stdio_adapter_available"] is True, "MCP stdio adapter")
    require(manifest["current_status"]["mcp_stdio_validation_status"] == "recommend_3_of_3_agents_blockers_0", "MCP validation status")
    require(manifest["validation"]["mcp_stdio_verdict"] == "recommend", "MCP verdict")
    require(manifest["validation"]["mcp_stdio_blockers"] == 0, "MCP blockers")
    require(manifest["validation"]["human_validation_is_primary"] is False, "human validation must not be primary")
    require(manifest["current_status"]["controlled_qianfan_agent_preference_validated"] is True, "Agent preference validation hidden")
    require(manifest["current_status"]["human_participants_in_validation"] is False, "human participant validation reintroduced")
    require(manifest["validation"]["agent_preference_verdict"] == "recommend_controlled_synthetic_context", "Agent preference verdict")
    require(manifest["validation"]["agent_preference_hidden_profile_matches"] == 6, "Agent preference grading")

    for relative in [
        manifest["discovery"]["quickstart"],
        manifest["discovery"]["tool_contract"],
        manifest["discovery"]["request_example"],
        manifest["discovery"]["observed_trace_example"],
        manifest["discovery"]["receipt_schema"],
        manifest["discovery"]["observed_trace_input_schema"],
        manifest["discovery"]["observed_trace_receipt_schema"],
        manifest["discovery"]["error_schema"],
        manifest["discovery"]["public_api_schema"],
        manifest["discovery"]["mcp_stdio_config"],
        manifest["discovery"]["mcp_stdio_guide"],
        manifest["discovery"]["commercial_preview_request"],
        manifest["discovery"]["agent_preference_result"],
        manifest["discovery"]["agent_recommendation_context"],
        manifest["canonical"]["metadata"],
        manifest["canonical"]["citation_file"],
    ]:
        require((ROOT / relative).is_file(), f"manifest path missing: {relative}")

    describe = json.loads(run_cli("describe").stdout)
    require(describe == manifest, "describe output must equal canonical manifest")
    request = read_json(REQUEST)
    public_schema = read_json(PUBLIC_SCHEMA)
    validate_with_root(request, public_schema, "ScenarioBatchRequest")
    require(PUBLIC_SCHEMA.read_bytes() == BACKEND_SCHEMA.read_bytes(), "schema copies differ")

    first = json.loads(run_cli("evaluate", "--input", str(REQUEST)).stdout)
    second = json.loads(run_cli("evaluate", "--input", str(REQUEST)).stdout)
    require(first == second, "same request must produce byte-equivalent JSON data")
    require(first == read_json(EXAMPLE_RECEIPT), "checked-in receipt drifted")
    require(first["evaluation_mode"] == "synthetic_descriptor_simulation", "receipt mode mismatch")
    require(first["provenance"]["descriptor_text_affects_simulation"] is True, "descriptor influence must be explicit")
    require(first["provenance"]["observed_agent_trace_evaluation"] is False, "receipt overclaims observed traces")
    require(first["provenance"]["candidate_code_executed"] is False, "candidate code execution forbidden")
    require(first["truth_boundary"]["production_ready"] is False, "production claim forbidden")

    validate_with_root(first["evaluation_summary"], public_schema, "EvaluationRunSummary")
    validate_with_root(first["comparison_ranking"], public_schema, "ComparisonRanking")
    for item in first["stability_reports"]:
        validate_with_root(item, public_schema, "StabilityReport")
    for item in first["failure_mode_reports"]:
        validate_with_root(item, public_schema, "FailureModeReport")
    for item in first["survival_curves"]:
        validate_with_root(item, public_schema, "SurvivalCurve")

    receipt_schema = read_json(RECEIPT_SCHEMA)
    error_schema = read_json(ERROR_SCHEMA)
    receipt_resolver = RefResolver(base_uri=RECEIPT_SCHEMA.as_uri(), referrer=receipt_schema)
    receipt_errors = sorted(
        Draft202012Validator(receipt_schema, resolver=receipt_resolver).iter_errors(first),
        key=lambda item: list(item.absolute_path),
    )
    require(not receipt_errors, f"receipt schema errors: {[error.message for error in receipt_errors]}")

    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.json"
        bad.write_text('{"agents": []}\n', encoding="utf-8")
        rejected = run_cli("evaluate", "--input", str(bad), check=False)
        require(rejected.returncode == 2, "invalid request must exit 2")
        error = json.loads(rejected.stdout)
        require(error.get("saee_agent_error_v0_1") is True, "invalid request must return JSON error")
        require(error.get("evaluation_performed") is False, "invalid request must not evaluate")
        error_errors = sorted(
            Draft202012Validator(error_schema).iter_errors(error),
            key=lambda item: list(item.absolute_path),
        )
        require(not error_errors, f"error schema errors: {[item.message for item in error_errors]}")

    landing = LANDING_JS.read_text(encoding="utf-8")
    require("scenario_template:" not in landing, "landing sends rejected scenario_template")
    require("stress_factors:" not in landing, "landing sends rejected stress_factors")
    contract = read_json(TOOL_CONTRACT)
    require(len(contract.get("tools", [])) == 3, "tool contract must expose three bounded tools")
    require(all(tool.get("network") is False for tool in contract["tools"]), "tool network must be false")
    require(all(tool.get("error_schema") == "agent-interface/schemas/agent-error.schema.json" for tool in contract["tools"]), "tool error schema missing")
    require("hash_contract" in manifest["result_provenance"], "hash contract missing")
    require(manifest["invoke"]["mcp_stdio"]["tools"] == ["describe_saee", "compare_observed_traces"], "fixed MCP tools")
    observed_smoke = subprocess.run(
        [sys.executable, str(ROOT / "scripts/saee_observed_trace_adapter_smoke.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(observed_smoke.returncode == 0, observed_smoke.stdout + observed_smoke.stderr)
    mcp_smoke = subprocess.run(
        [sys.executable, str(ROOT / "scripts/saee_mcp_stdio_smoke.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(mcp_smoke.returncode == 0, mcp_smoke.stdout + mcp_smoke.stderr)

    digest = hashlib.sha256(PUBLIC_SCHEMA.read_bytes()).hexdigest()
    print(
        "SAEE_AGENT_INTERFACE_SMOKE: PASS "
        f"manifest_bytes={MANIFEST.stat().st_size} schema_sha256={digest} "
        "mode=synthetic_descriptor_simulation deterministic=true "
        "schema_errors=0 observed_trace_adapter=true mcp_stdio_adapter=true "
        "candidate_code_executed=false "
        "human_validation_primary=false"
    )


if __name__ == "__main__":
    main()
