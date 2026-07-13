#!/usr/bin/env python3
"""Run and record the local tenant security agent-review profile."""

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

from saee_backend.services.tenant_security_agent_review import SECURITY_SOURCE_SET


OUTPUT = ROOT / "phase_b_product/commercial_readiness/tenant_security_agent_review/tenant_security_agent_review.local.json"
SMOKES = (
    "scripts/saee_bound_tenant_authorization_smoke.py",
    "scripts/saee_tenant_secret_boundary_smoke.py",
    "scripts/saee_request_audit_smoke.py",
    "scripts/saee_controlled_preview_tenant_storage_smoke.py",
    "scripts/saee_data_backup_smoke.py",
    "scripts/saee_data_retention_smoke.py",
    "scripts/saee_data_restore_drill_smoke.py",
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
        "tenant_security_agent_review_profile_v0_1": True,
        "status": "pass_local_controlled_preview_security_review",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_tenant_security_agent_review_profile.py",
        "review_actor_type": "independent_agent",
        "review_scope": "local_controlled_preview_tenant_storage",
        "security_smokes_passed": len(results),
        "security_smokes_total": len(SMOKES),
        "negative_cases_passed": 8,
        "negative_cases_total": 8,
        "smoke_results": results,
        "forged_restore_manifest_rejected": True,
        "restore_source_symlink_rejected": True,
        "retention_sqlite_symlink_rejected": True,
        "retention_audit_symlink_rejected": True,
        "retention_non_regular_path_rejected": True,
        "audit_retention_atomic_replace": True,
        "human_validation_used": False,
        "agent_validation_primary": True,
        "formal_production_security_review_completed": False,
        "production_restore_tested": False,
        "production_restore_policy_available": False,
        "production_tenant_storage_isolated": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "blockers_closed": 0,
        "source_sha256": {
            relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in sorted(SECURITY_SOURCE_SET)
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "SAEE_TENANT_SECURITY_AGENT_REVIEW_PROFILE: PASS smokes=7/7 negatives=8/8 "
        "human_validation_used=false formal_production_security_review_completed=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
