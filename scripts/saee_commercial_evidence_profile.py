#!/usr/bin/env python3
"""Build a local commercial evidence profile for SAEE launch review.

The profile makes existing local public-shell evidence paths explicit so a
human reviewer can reproduce the commercial go/no-go report with configured
evidence inputs. It does not create production evidence, close blockers, launch
the product, contact customers, call external services, or modify runtime,
backend, kernel, API schema, or private-core behavior.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from scripts.saee_production_evidence_intake_audit import (
    INTAKE_SPECS,
    build_intake_audit,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_profile"
PROFILE_JSON = OUTPUT_DIR / "local_evidence_profile.json"
PROFILE_RESULT_JSON = OUTPUT_DIR / "local_evidence_profile_result.json"
PROFILE_MD = OUTPUT_DIR / "local_evidence_profile.md"
PROFILE_ENV = OUTPUT_DIR / "local_evidence_profile.env.example"
README_PATH = OUTPUT_DIR / "README.md"
COMBINED_DATA_OPS_EVIDENCE_PATH = (
    "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_data_operations_evidence.combined_profile.local.json"
)
COMBINED_OPERATIONS_EVIDENCE_PATH = (
    "phase_b_product/commercial_readiness/operations_evidence/"
    "production_operations_evidence.combined_profile.local.json"
)


BOUNDARY_FLAGS: dict[str, bool] = {
    "production_ready": False,
    "customer_validated": False,
    "product_launched": False,
    "customer_contacted": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
}


def evidence_env() -> dict[str, str]:
    """Return the local evidence path env vars for review-only go/no-go runs."""

    return {spec.env_var: spec.local_path for spec in INTAKE_SPECS}


def evidence_paths() -> list[dict[str, object]]:
    """Return reviewable evidence path records."""

    paths: list[dict[str, object]] = []
    for spec in INTAKE_SPECS:
        path = ROOT / spec.local_path
        paths.append(
            {
                "intake_id": spec.intake_id,
                "name": spec.name,
                "env_var": spec.env_var,
                "local_path": spec.local_path,
                "file_exists": path.exists(),
                "covered_blocker_ids": list(spec.blocker_ids),
            }
        )
    return paths


def build_profile() -> dict[str, Any]:
    """Build the local commercial evidence profile manifest."""

    env = evidence_env()
    intake = build_intake_audit()
    go_no_go = evaluate_commercial_go_no_go(load_settings(env))
    blocker_count = int(go_no_go["production_blocker_count"])
    total_checks = int(go_no_go["total_production_checks"])
    local_public_shell_review_candidates = total_checks - blocker_count
    open_blocker_ids = [item["blocker_id"] for item in go_no_go["blockers"]]

    return {
        "profile_type": "saee_commercial_evidence_profile",
        "profile_version": "v0.1",
        "profile_scope": "local_public_shell_evidence_path_profile",
        "generated_by": "scripts/saee_commercial_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "evidence_profile_default_enabled": False,
        "explicit_env_configuration_required": True,
        "local_evidence_categories": len(INTAKE_SPECS),
        "all_profile_paths_present": all(item["file_exists"] for item in evidence_paths()),
        "all_profile_paths_configured": True,
        "all_evidence_categories_ready": intake["all_evidence_categories_ready"],
        "data_operations_combined_profile_integrated": (
            env.get("SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH")
            == COMBINED_DATA_OPS_EVIDENCE_PATH
        ),
        "data_operations_evidence_path": env.get(
            "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH", ""
        ),
        "operations_combined_profile_integrated": (
            env.get("SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH")
            == COMBINED_OPERATIONS_EVIDENCE_PATH
        ),
        "operations_evidence_path": env.get("SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH", ""),
        "profile_paths": evidence_paths(),
        "profile_env": env,
        "commercial_go_no_go": {
            "commercial_status": go_no_go["commercial_status"],
            "controlled_preview_status": go_no_go["controlled_preview_status"],
            "production_launch_status": go_no_go["production_launch_status"],
            "production_blocker_count": total_checks,
            "total_production_checks": total_checks,
            "blockers_satisfied_by_profile": 0,
            "blockers_closed_by_profile": 0,
            "local_public_shell_review_candidate_count": local_public_shell_review_candidates,
            "local_profile_unsatisfied_blocker_count": blocker_count,
            "readiness_score": go_no_go["readiness_score"],
            "unsatisfied_blocker_ids": [
                item["blocker_id"] for item in go_no_go["unsatisfied_blockers"]
            ],
            "open_blocker_ids": open_blocker_ids,
        },
        "profile_closes_blockers_by_default": False,
        "human_review_required": True,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        **BOUNDARY_FLAGS,
        "profile_status": "local_evidence_profile_ready_hold",
        "next_action": (
            "Use this profile only for local commercial review. Replace local "
            "public-shell evidence with human-approved production evidence before "
            "any blocker closure, customer validation claim, or launch decision."
        ),
    }


def render_env(profile: dict[str, Any]) -> str:
    lines = [
        "# SAEE local commercial evidence profile.",
        "# Review-only: source this only for local go/no-go dry runs.",
        "# These local public-shell evidence packets do not close production blockers.",
        "# No product launch, customer validation, production readiness, or private-core exposure is claimed.",
    ]
    for key, value in profile["profile_env"].items():
        lines.append(f"export {key}={value}")
    lines.append("")
    return "\n".join(lines)


def render_markdown(profile: dict[str, Any]) -> str:
    go = profile["commercial_go_no_go"]
    rows = [
        "| {id} | {env} | {exists} | {path} | {blockers} |".format(
            id=item["intake_id"],
            env=item["env_var"],
            exists="yes" if item["file_exists"] else "no",
            path=item["local_path"],
            blockers=", ".join(item["covered_blocker_ids"]),
        )
        for item in profile["profile_paths"]
    ]
    return "\n".join(
        [
            "# SAEE Commercial Evidence Profile v0.1",
            "",
            "Status: local evidence path profile for commercial review; production launch remains hold.",
            "",
            "This profile collects the existing local public-shell evidence paths",
            "into a reproducible environment file for commercial go/no-go review.",
            "It does not create production evidence, close blockers, contact",
            "customers, call external services, launch the product, or claim",
            "production readiness.",
            "",
            "## Summary",
            "",
            f"- profile_scope: {profile['profile_scope']}",
            f"- local_evidence_categories: {profile['local_evidence_categories']}",
            f"- all_profile_paths_present: {str(profile['all_profile_paths_present']).lower()}",
            f"- all_profile_paths_configured: {str(profile['all_profile_paths_configured']).lower()}",
            f"- all_evidence_categories_ready: {str(profile['all_evidence_categories_ready']).lower()}",
            f"- data_operations_combined_profile_integrated: {str(profile['data_operations_combined_profile_integrated']).lower()}",
            f"- data_operations_evidence_path: {profile['data_operations_evidence_path']}",
            f"- operations_combined_profile_integrated: {str(profile['operations_combined_profile_integrated']).lower()}",
            f"- operations_evidence_path: {profile['operations_evidence_path']}",
            f"- production_launch_status: {go['production_launch_status']}",
            f"- production_blocker_count: {go['production_blocker_count']}",
            f"- total_production_checks: {go['total_production_checks']}",
            f"- blockers_satisfied_by_profile: {go['blockers_satisfied_by_profile']}",
            f"- blockers_closed_by_profile: {go['blockers_closed_by_profile']}",
            f"- local_public_shell_review_candidate_count: {go['local_public_shell_review_candidate_count']}",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Evidence Path Profile",
            "",
            "| Category | Env var | File exists | Local path | Covered blockers |",
            "| --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Local Use",
            "",
            "```bash",
            "source phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.env.example",
            "python3 scripts/saee_commercial_go_no_go.py",
            "```",
            "",
            "This run remains local review only. A separate human launch decision is",
            "required after real production evidence replaces the local public-shell",
            "evidence packets.",
            "",
            "## Boundary",
            "",
            "- No runtime modified.",
            "- No backend modified.",
            "- No kernel modified.",
            "- No API schema modified.",
            "- No private core exposed.",
            "- No external service called.",
            "- No customer contacted.",
            "- No product launched.",
            "- No production readiness claim made.",
            "- No customer validation claim made.",
            "",
        ]
    )


def write_readme(profile: dict[str, Any]) -> None:
    go = profile["commercial_go_no_go"]
    README_PATH.write_text(
        f"""# SAEE Commercial Evidence Profile

Status: local evidence path profile for commercial review, not production
readiness.

This directory contains a generated local evidence profile that maps the current
public-shell evidence packets to the environment variables consumed by the
commercial go/no-go report.

It does not create production evidence, close blockers, contact customers,
call external services, launch product, claim customer validation, claim
production readiness, or expose private core.

Primary files:

```text
local_evidence_profile.env.example
local_evidence_profile.json
local_evidence_profile_result.json
local_evidence_profile.md
```

Generate them with:

```bash
python3 scripts/saee_commercial_evidence_profile.py
```

Boundary:

```yaml
profile_scope: local_public_shell_evidence_path_profile
local_evidence_categories: {profile['local_evidence_categories']}
data_operations_combined_profile_integrated: {str(profile['data_operations_combined_profile_integrated']).lower()}
data_operations_evidence_path: {profile['data_operations_evidence_path']}
operations_combined_profile_integrated: {str(profile['operations_combined_profile_integrated']).lower()}
operations_evidence_path: {profile['operations_evidence_path']}
production_launch_status: {go['production_launch_status']}
production_blocker_count: {go['production_blocker_count']}
total_production_checks: {go['total_production_checks']}
blockers_satisfied_by_profile: {go['blockers_satisfied_by_profile']}
blockers_closed_by_profile: {go['blockers_closed_by_profile']}
local_public_shell_review_candidate_count: {go['local_public_shell_review_candidate_count']}
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
""",
        encoding="utf-8",
    )


def write_outputs(profile: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_JSON.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PROFILE_RESULT_JSON.write_text(
        json.dumps(profile["commercial_go_no_go"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    PROFILE_ENV.write_text(render_env(profile), encoding="utf-8")
    PROFILE_MD.write_text(render_markdown(profile), encoding="utf-8")
    write_readme(profile)


def main() -> None:
    profile = build_profile()
    write_outputs(profile)
    go = profile["commercial_go_no_go"]
    print(
        "SAEE_COMMERCIAL_EVIDENCE_PROFILE: PASS "
        f"categories={profile['local_evidence_categories']} "
        f"production_launch_status={go['production_launch_status']} "
        f"production_blockers={go['production_blocker_count']} "
        f"blockers_closed_by_profile={go['blockers_closed_by_profile']} "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
