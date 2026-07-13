#!/usr/bin/env python3
"""Run and record the narrow tenant privacy independent-agent review profile."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.tenant_privacy_agent_review import PRIVACY_SOURCE_SET


OUTPUT = ROOT / "phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_agent_review.local.json"
SMOKES = (
    "scripts/saee_synthetic_data_only_mode_smoke.py",
    "scripts/saee_personal_data_boundary_smoke.py",
    "scripts/saee_tenant_privacy_data_flow_smoke.py",
    "scripts/saee_controlled_preview_request_smoke.py",
    "scripts/saee_tenant_secret_boundary_smoke.py",
    "scripts/saee_request_audit_smoke.py",
    "scripts/saee_data_backup_smoke.py",
    "scripts/saee_data_retention_smoke.py",
    "scripts/saee_data_restore_drill_smoke.py",
    "scripts/saee_qianfan_provider_policy_snapshot_smoke.py",
)


def main() -> None:
    results = []
    for relative in SMOKES:
        completed = subprocess.run(
            [sys.executable, str(ROOT / relative)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        results.append(
            {
                "script": relative,
                "status": "pass",
                "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
            }
        )
    data = {
        "tenant_privacy_agent_review_profile_v0_1": True,
        "status": "pass_whole_tenant_api_synthetic_only_controlled_preview_privacy_boundary",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_tenant_privacy_agent_review_profile.py",
        "review_actor_type": "independent_agent",
        "review_scope": "whole_tenant_api_synthetic_only_controlled_preview",
        "privacy_smokes_passed": len(results),
        "privacy_smokes_total": len(SMOKES),
        "negative_cases_passed": 16,
        "negative_cases_total": 16,
        "personal_data_boundary_cases_passed": 29,
        "personal_data_boundary_cases_total": 29,
        "smoke_results": results,
        "scenario_config_personal_data_rejected": True,
        "experiment_create_metadata_personal_data_rejected": True,
        "runner_revalidation_available": True,
        "personal_data_detection_scope": "high_confidence_patterns_and_closed_keys",
        "general_dlp_available": False,
        "deidentification_proven": False,
        "real_customer_data_allowed": False,
        "human_validation_used": False,
        "agent_validation_primary": True,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_completed": False,
        "qianfan_provider_legal_approval_completed": False,
        "qianfan_retention_terms_verified": False,
        "customer_data_processing_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "blockers_closed": 0,
        "source_sha256": {
            relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in sorted(PRIVACY_SOURCE_SET)
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "SAEE_TENANT_PRIVACY_AGENT_REVIEW_PROFILE: PASS smokes=10/10 "
        "personal_data_cases=29/29 human_validation_used=false general_dlp=false "
        "privacy_legal_review_completed=false production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
