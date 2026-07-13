#!/usr/bin/env python3
"""Smoke test for SAEE public claim lint."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_public_claim_lint.py"
REPORT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/public_claim_lint/public_claim_lint.local.json"
)
REPORT_MD = (
    ROOT / "phase_b_product/commercial_readiness/public_claim_lint/public_claim_lint.md"
)
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PUBLIC_CLAIM_LINT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PUBLIC_CLAIM_LINT_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_PUBLIC_CLAIM_LINT_SMOKE: FAIL: {message}")


def run_default_lint() -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        fail(result.stderr or result.stdout or "default lint failed")
    if not REPORT_JSON.exists():
        fail("public claim lint JSON report missing")
    if not REPORT_MD.exists():
        fail("public claim lint Markdown report missing")
    return json.loads(REPORT_JSON.read_text(encoding="utf-8"))


def require_default_report(report: dict[str, object]) -> None:
    expected_false_flags = [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "external_validation_claim",
        "customer_contacted",
        "public_sdk_released",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
    ]
    if report.get("public_claim_lint_v0_1") is not True:
        fail("public_claim_lint_v0_1 must be true")
    if report.get("status") != "pass":
        fail("default public claim lint status must be pass")
    if report.get("violation_count") != 0:
        fail("default public claim lint must have zero violations")
    if report.get("files_scanned", 0) < 10:
        fail("default public claim lint must scan public and agent-readable surfaces")
    if report.get("blockers_closed_by_lint") != 0:
        fail("public claim lint must close zero blockers")
    for flag in expected_false_flags:
        if report.get(flag) is not False:
            fail(f"{flag} must remain false")


def require_fixture_detection() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        fixture = tmp / "bad_claim.md"
        fixture.write_text(
            '"production_ready": true\nSAEE is production ready for enterprise use.\n',
            encoding="utf-8",
        )
        output_json = tmp / "fixture_report.json"
        output_md = tmp / "fixture_report.md"
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--scan-file",
                str(fixture),
                "--output-json",
                str(output_json),
                "--output-md",
                str(output_md),
            ],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            fail("fixture with forbidden public claims must fail lint")
        fixture_report = json.loads(output_json.read_text(encoding="utf-8"))
        if fixture_report.get("status") != "fail":
            fail("fixture report status must be fail")
        if fixture_report.get("violation_count", 0) < 2:
            fail("fixture report must detect boolean and natural-language claims")


def require_docs() -> None:
    for path in [TOP_DOC, GATE, REPORT_MD]:
        if not path.exists():
            fail(f"missing public claim lint doc: {path}")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    report = REPORT_MD.read_text(encoding="utf-8")
    required_pairs = [
        (top_doc, "public_claim_lint_v0_1: true"),
        (top_doc, "blockers_closed_by_lint: 0"),
        (top_doc, "It does not make SAEE"),
        (gate, "answer: recommend"),
        (gate, "recommend_for_public_claim_boundary_guard: true"),
        (gate, "recommend_for_product_launch: false"),
        (report, "No forbidden public commercial claims were found"),
    ]
    for text, token in required_pairs:
        if token not in text:
            fail(f"missing documentation token: {token}")


def main() -> None:
    report = run_default_lint()
    require_default_report(report)
    require_fixture_detection()
    require_docs()
    print("SAEE_PUBLIC_CLAIM_LINT_SMOKE: PASS")


if __name__ == "__main__":
    main()
