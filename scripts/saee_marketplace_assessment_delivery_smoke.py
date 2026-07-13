#!/usr/bin/env python3
"""End-to-end and fail-closed checks for the Marketplace delivery bridge."""

from __future__ import annotations

import ast
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.marketplace_assessment_delivery import (
    BUNDLE_SCHEMA,
    INTAKE_SCHEMA,
    RECEIPT_SCHEMA,
    MarketplaceDeliveryError,
    finalize_delivery,
    generate_assessment_bundle,
    load_json,
    prepare_delivery,
    render_assessment_report,
)


EXAMPLE = ROOT / "agent-interface/commercial/examples/saee-marketplace-assessment-intake.v0.1.json"
SERVICE = ROOT / "saee_backend/services/marketplace_assessment_delivery.py"
CLI = ROOT / "scripts/saee_marketplace_assessment_delivery.py"
DOC = ROOT / "docs/commercial/SAEE_ALIBABA_MARKETPLACE_DELIVERY_BRIDGE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_ALIBABA_MARKETPLACE_DELIVERY_BRIDGE_RECOMMENDATION_GATE.md"


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SystemExit("SAEE_MARKETPLACE_ASSESSMENT_DELIVERY_SMOKE: FAIL " + detail)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen", "run", "Popen"}:
            found.add(node.func.attr)
    return found


def expect_invalid(value: dict[str, Any], code: str) -> None:
    try:
        generate_assessment_bundle(value)
    except MarketplaceDeliveryError as exc:
        require(exc.code == code, f"expected {code}, got {exc.code}")
        return
    raise SystemExit("SAEE_MARKETPLACE_ASSESSMENT_DELIVERY_SMOKE: FAIL invalid intake accepted")


def main() -> None:
    for path in (INTAKE_SCHEMA, BUNDLE_SCHEMA, RECEIPT_SCHEMA):
        Draft202012Validator.check_schema(load_json(path))
    for path in (SERVICE, CLI, Path(__file__)):
        require(not imported_roots(path).intersection({"socket", "subprocess", "urllib", "requests", "httpx"}), f"external import: {path.name}")
        require(not forbidden_calls(path), f"dynamic execution: {path.name}")
    require(DOC.is_file() and GATE.is_file(), "agent-readable documentation missing")
    require("answer: recommend" in GATE.read_text(encoding="utf-8"), "recommendation gate not closed")
    require(GATE.read_text(encoding="utf-8").count("status: fixed") == 4, "recommendation blockers not fixed")

    intake = load_json(EXAMPLE)
    serial = []
    for _ in range(5):
        serial.append(json.dumps(generate_assessment_bundle(copy.deepcopy(intake)), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    require(len(set(serial)) == 1, "bundle is not deterministic")
    bundle = json.loads(serial[0])
    require(bundle["operation"] == "saee.evaluate_agent_run", "operation delegation")
    require(bundle["assessment_result"]["recommendation"] == "REPLAN", "bounded recommendation")
    require(bundle["assessment_result"]["score"] == 50, "coverage semantics")
    require(bundle["truth_boundary"]["normalized_customer_metadata_used"] is True, "normalized metadata truth")
    require(bundle["truth_boundary"]["raw_customer_data_used"] is False, "raw data boundary")
    report = render_assessment_report(bundle)
    require("必需证据覆盖率：`50%`" in report and "不是安全认证" in report, "customer report content")

    invalid_cases = 0
    mutation = copy.deepcopy(intake)
    mutation["readiness_request"]["customer_data_included"] = True
    expect_invalid(mutation, "MARKETPLACE_READINESS_REQUEST_INVALID")
    invalid_cases += 1
    mutation = copy.deepcopy(intake)
    mutation["material_attestation"]["personal_data_excluded"] = False
    expect_invalid(mutation, "MARKETPLACE_INTAKE_SCHEMA_INVALID")
    invalid_cases += 1
    mutation = copy.deepcopy(intake)
    mutation["material_attestation"]["executable_content_excluded"] = False
    expect_invalid(mutation, "MARKETPLACE_INTAKE_SCHEMA_INVALID")
    invalid_cases += 1
    mutation = copy.deepcopy(intake)
    mutation["readiness_request"]["trace"]["events"][0]["summary"] = "See https://example.invalid/raw"
    expect_invalid(mutation, "MARKETPLACE_CONTENT_SCREEN_REJECTED")
    invalid_cases += 1
    mutation = copy.deepcopy(intake)
    mutation["readiness_request"]["task"] = "Contact demo@example.invalid"
    expect_invalid(mutation, "MARKETPLACE_CONTENT_SCREEN_REJECTED")
    invalid_cases += 1
    mutation = copy.deepcopy(intake)
    mutation["readiness_request"]["evidence"][0]["source_ref"] = "../raw/customer.json"
    expect_invalid(mutation, "MARKETPLACE_EVIDENCE_REF_REJECTED")
    invalid_cases += 1
    mutation = copy.deepcopy(intake)
    mutation["unexpected"] = True
    expect_invalid(mutation, "MARKETPLACE_INTAKE_SCHEMA_INVALID")
    invalid_cases += 1

    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        intake_root = temp_root / "intake"
        intake_root.mkdir()
        source = intake_root / "request.json"
        shutil.copyfile(EXAMPLE, source)
        output = temp_root / "output"
        prepared = prepare_delivery(source, output)
        require(prepared["stage"] == "prepared_for_human_review", "prepared stage")
        require(source.exists(), "prepare deleted source")
        require((output / "assessment-bundle.json").is_file(), "bundle missing")
        require((output / "assessment-report.zh-CN.md").is_file(), "report missing")
        final = finalize_delivery(
            output / "delivery-receipt.prepared.json",
            source,
            intake_root,
            "owner-boundary-reviewer",
        )
        require(not source.exists(), "finalize did not delete source")
        require(final["stage"] == "reviewed_ready_for_marketplace_delivery", "final stage")
        require(final["human_boundary_review"]["completed"] is True, "human review receipt")
        require(final["local_source_deletion"]["completed"] is True, "deletion receipt")
        require(final["marketplace_delivery"]["ready"] is True, "delivery readiness")
        require(final["marketplace_delivery"]["completed"] is False, "delivery truth promoted")
        require(final["truth_boundary"]["customer_validated"] is False, "customer validation promoted")

    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        intake_root = temp_root / "intake"
        intake_root.mkdir()
        source = intake_root / "request.json"
        shutil.copyfile(EXAMPLE, source)
        symlink = intake_root / "request-link.json"
        symlink.symlink_to(source)
        try:
            prepare_delivery(symlink, temp_root / "symlink-output")
        except MarketplaceDeliveryError as exc:
            require(exc.code == "MARKETPLACE_SOURCE_FILE_INVALID", "symlink rejection")
            invalid_cases += 1
        else:
            raise SystemExit("SAEE_MARKETPLACE_ASSESSMENT_DELIVERY_SMOKE: FAIL symlink accepted")

    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        intake_root = temp_root / "intake"
        intake_root.mkdir()
        source = temp_root / "outside.json"
        shutil.copyfile(EXAMPLE, source)
        output = temp_root / "output"
        prepare_delivery(source, output)
        try:
            finalize_delivery(output / "delivery-receipt.prepared.json", source, intake_root, "owner-reviewer")
        except MarketplaceDeliveryError as exc:
            require(exc.code == "MARKETPLACE_SOURCE_OUTSIDE_INTAKE_ROOT", "outside-root rejection")
            invalid_cases += 1
        else:
            raise SystemExit("SAEE_MARKETPLACE_ASSESSMENT_DELIVERY_SMOKE: FAIL outside-root source accepted")

    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        intake_root = temp_root / "intake"
        intake_root.mkdir()
        source = intake_root / "request.json"
        shutil.copyfile(EXAMPLE, source)
        output = temp_root / "output"
        prepare_delivery(source, output)
        with (output / "assessment-report.zh-CN.md").open("a", encoding="utf-8") as handle:
            handle.write("drift\n")
        try:
            finalize_delivery(output / "delivery-receipt.prepared.json", source, intake_root, "owner-reviewer")
        except MarketplaceDeliveryError as exc:
            require(exc.code == "MARKETPLACE_REPORT_DIGEST_DRIFT", "report drift rejection")
            invalid_cases += 1
        else:
            raise SystemExit("SAEE_MARKETPLACE_ASSESSMENT_DELIVERY_SMOKE: FAIL report drift accepted")

    print("SAEE_MARKETPLACE_ASSESSMENT_DELIVERY_SMOKE: PASS")
    print("valid_prepare_finalize=1/1")
    print(f"invalid_cases={invalid_cases}/{invalid_cases}")
    print("deterministic_runs=5/5")
    print("delegated_operation=saee.evaluate_agent_run")
    print("human_boundary_review=true")
    print("local_source_deleted=true")
    print("marketplace_delivery_completed=false")
    print("customer_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
