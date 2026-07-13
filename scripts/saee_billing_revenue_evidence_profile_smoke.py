#!/usr/bin/env python3
"""Smoke check for the SAEE combined billing/revenue evidence profile."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_billing_revenue_evidence_profile import (
    DEFAULT_COMBINED_EVIDENCE,
    DEFAULT_PROFILE_JSON,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    SOURCE_KEY_GROUPS,
    build_profile,
)
from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_billing_revenue_evidence import FORBIDDEN_TRUE_KEYS


PROFILE_SCRIPT = ROOT / "scripts/saee_billing_revenue_evidence_profile.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BILLING_REVENUE_EVIDENCE_PROFILE_SMOKE: FAIL: " + message)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_evidence(label: str, *, complete: bool, unsafe: bool = False) -> dict[str, object]:
    data: dict[str, object] = {
        "billing_revenue_evidence_type": "production_billing_revenue_evidence",
        "evidence_scope": f"fixture_{label}_billing_revenue_evidence",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_billing_revenue_evidence_profile_smoke.py",
        "source_boundary_violation_count": 0,
    }
    for group_label, keys in SOURCE_KEY_GROUPS.items():
        for key in keys:
            data[key] = complete and group_label == label
    for key in FORBIDDEN_TRUE_KEYS:
        data[key] = False
    if unsafe:
        data["production_ready"] = True
    return data


def complete_source_paths(tmp: Path, *, unsafe: bool = False) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for label in SOURCE_KEY_GROUPS:
        path = tmp / f"{label}.json"
        write_json(path, source_evidence(label, complete=True, unsafe=unsafe and label == "pricing_page"))
        paths[label] = path
    return paths


def go_no_go(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(PROFILE_SCRIPT.exists(), "profile script missing")

    default_run = subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_profile = json.loads(default_run.stdout)
    require(default_profile["profile_status"] == "hold", "default profile status hold")
    require(
        default_profile["production_billing_revenue_ready"] is False,
        "default billing/revenue not ready",
    )
    require(
        default_profile["target_blockers_satisfied_count"] == 0,
        "default target blockers satisfied count must be zero",
    )
    require(
        default_profile["profile_production_blocker_count"] == 24,
        "default profile leaves 24 blockers",
    )
    require(default_profile["blockers_closed_by_profile"] == 0, "default closes no blockers")
    require(DEFAULT_PROFILE_JSON.exists(), "default profile JSON missing")
    require(DEFAULT_COMBINED_EVIDENCE.exists(), "default combined evidence missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_profile_path = tmp / "complete_billing_profile.json"
        complete_combined_path = tmp / "complete_billing_evidence.json"
        unsafe_profile_path = tmp / "unsafe_billing_profile.json"
        unsafe_combined_path = tmp / "unsafe_billing_evidence.json"

        complete_profile = build_profile(
            complete_source_paths(tmp / "complete"),
            complete_profile_path,
            complete_combined_path,
        )
        unsafe_profile = build_profile(
            complete_source_paths(tmp / "unsafe", unsafe=True),
            unsafe_profile_path,
            unsafe_combined_path,
        )
        complete_go_no_go = go_no_go(complete_combined_path)

    require(complete_profile["profile_status"] == "pass", "complete fixture profile pass")
    require(
        complete_profile["production_billing_revenue_ready"] is True,
        "complete fixture billing/revenue ready",
    )
    require(
        complete_profile["target_blockers_satisfied_count"] == 6,
        "complete fixture satisfies six billing/revenue blockers",
    )
    require(
        complete_go_no_go["satisfied_production_checks"] == 6,
        "complete fixture satisfies six go/no-go checks",
    )
    require(
        complete_go_no_go["production_blocker_count"] == 18,
        "complete fixture leaves 18 blockers",
    )
    require(complete_go_no_go["commercial_status"] == "hold", "commercial remains hold")
    require(complete_go_no_go["production_ready"] is False, "production ready false")
    require(
        complete_profile["blockers_closed_by_profile"] == 0,
        "complete profile closes no blockers by itself",
    )
    require(unsafe_profile["profile_status"] == "stop", "unsafe profile stops")
    require(
        unsafe_profile["source_boundary_violation_count"] > 0,
        "unsafe profile records source violation",
    )
    require(
        unsafe_profile["production_billing_revenue_ready"] is False,
        "unsafe billing/revenue not ready",
    )

    subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "billing_revenue_evidence_profile_v0_1: true",
        "profile_scope: combined_billing_revenue_evidence_profile_to_go_no_go",
        "default_profile_status: hold",
        "pricing_page_evidence_complete: false",
        "payment_provider_evidence_complete: false",
        "invoice_process_evidence_complete: false",
        "tax_review_evidence_complete: false",
        "refund_policy_evidence_complete: false",
        "tenant_billing_isolation_evidence_complete: false",
        "production_billing_revenue_ready: false",
        "profile_production_blocker_count: 24",
        "blockers_closed_by_profile: 0",
        "answer: conditional",
        "recommend_for_human_go_no_go_review: true",
        "recommend_for_blocker_closure_by_profile_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_payment_enablement: false",
        "recommend_for_customer_contact: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PROFILE_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_profile.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.combined_profile.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_profile_report.md",
        "/docs/strategy/SAEE_BILLING_REVENUE_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md",
        "/scripts/saee_billing_revenue_evidence_profile.py",
        "/scripts/saee_billing_revenue_evidence_profile_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("billing_revenue_evidence_profile_v0_1", {})
    expected = {
        "status": "local_combined_billing_revenue_profile_hold",
        "profile_scope": "combined_billing_revenue_evidence_profile_to_go_no_go",
        "pricing_page_evidence_complete": False,
        "payment_provider_evidence_complete": False,
        "invoice_process_evidence_complete": False,
        "tax_review_evidence_complete": False,
        "refund_policy_evidence_complete": False,
        "tenant_billing_isolation_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "target_blockers_satisfied_count": 0,
        "profile_production_blocker_count": 24,
        "blockers_closed_by_profile": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "invoice_sent_to_customer": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_BILLING_REVENUE_EVIDENCE_PROFILE_SMOKE: PASS "
        "default_billing_ready=false default_blockers=24 "
        "complete_fixture_billing_ready=true complete_blockers=18 "
        "blockers_closed_by_profile=0"
    )


if __name__ == "__main__":
    main()
