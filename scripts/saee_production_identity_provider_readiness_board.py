#!/usr/bin/env python3
"""Build a local production identity-provider readiness board.

This board consolidates existing production identity-provider readiness
artifacts into a single human-review surface. It does not select or contact an
identity provider, fetch JWKS, validate production tokens, enable production
auth, close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
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


AUTH_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"
PHASE1_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
FIXTURE_DIR = ROOT / "phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run"

OUTPUT_JSON = AUTH_DIR / "production_identity_provider_readiness_board.local.json"
OUTPUT_MD = AUTH_DIR / "production_identity_provider_readiness_board.md"
OUTPUT_CSV = AUTH_DIR / "production_identity_provider_readiness_board.csv"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD_RECOMMENDATION_GATE.md"
)

SOURCE_PATHS = {
    "decision_packet": AUTH_DIR / "production_identity_provider_decision_packet.local.json",
    "approval_input_validation": AUTH_DIR
    / "production_identity_provider_approval_input_validation.local.json",
    "phase1_evidence_builder": PHASE1_DIR / "phase_1_identity_tenant_evidence_builder_output.local.json",
    "auth_evidence_runner": AUTH_DIR / "auth_evidence.local.json",
    "auth_fixture_dry_run": FIXTURE_DIR / "auth_oidc_rbac_fixture_dry_run.local.json",
    "auth_evidence_path": AUTH_DIR / "production_auth_evidence_path.local.json",
}

FALSE_FLAGS = {
    "production_identity_provider_available": False,
    "production_identity_provider_selected": False,
    "production_identity_provider_approved_by_validator": False,
    "production_identity_provider_configured": False,
    "production_auth_enabled": False,
    "production_auth_ready": False,
    "production_tokens_validated_by_codex": False,
    "tokens_validated_in_production": False,
    "identity_provider_contacted_by_codex": False,
    "identity_provider_contacted": False,
    "jwks_fetched_by_codex": False,
    "jwks_fetched": False,
    "oauth_oidc_available": False,
    "rbac_available": False,
    "rbac_enforced_in_production": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "development_permission_granted": False,
    "blockers_closed_by_board": 0,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "product_launched": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD: FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD: FAIL {path} must contain an object"
        )
    return data


def commercial_identity_provider_state() -> dict[str, Any]:
    go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    blockers = go_no_go.get("blockers", [])
    idp_blocker = {}
    if isinstance(blockers, list):
        for item in blockers:
            if isinstance(item, dict) and item.get("blocker_id") == "production_identity_provider":
                idp_blocker = item
                break
    return {
        "commercial_status": go_no_go.get("commercial_status"),
        "production_launch_status": go_no_go.get("production_launch_status"),
        "production_blocker_count": go_no_go.get("production_blocker_count"),
        "production_identity_provider_blocker_satisfied": idp_blocker.get("satisfied") is True,
        "production_identity_provider_blocker_message": idp_blocker.get(
            "message",
            "Production identity provider must be available before commercial launch.",
        ),
    }


def step_state(
    step_id: str,
    title: str,
    source_key: str,
    status: str,
    complete: bool,
    next_action: str,
    local_support_only: bool = False,
) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "title": title,
        "source": source_key,
        "source_path": rel(SOURCE_PATHS[source_key]),
        "status": status,
        "complete": complete,
        "local_support_only": local_support_only,
        "next_action": next_action,
        "human_review_required": True,
    }


def board_status(steps: list[dict[str, Any]], blocker_satisfied: bool) -> str:
    if blocker_satisfied:
        return "hold_human_closure_review_required"
    for step in steps:
        if step["step_id"] == "PIDB-002" and not step["complete"]:
            return "hold_human_identity_provider_input_required"
        if step["step_id"] == "PIDB-003" and not step["complete"]:
            return "hold_phase1_identity_tenant_evidence_builder_required"
        if step["step_id"] == "PIDB-005" and not step["complete"]:
            return "hold_real_identity_provider_evidence_required"
    return "hold_go_no_go_and_closure_review_required"


def build_board() -> dict[str, Any]:
    sources = {name: read_json(path) for name, path in SOURCE_PATHS.items()}
    commercial = commercial_identity_provider_state()

    packet = sources["decision_packet"]
    approval = sources["approval_input_validation"]
    builder = sources["phase1_evidence_builder"]
    auth = sources["auth_evidence_runner"]
    fixture = sources["auth_fixture_dry_run"]
    path = sources["auth_evidence_path"]

    steps = [
        step_state(
            "PIDB-001",
            "Production identity-provider decision packet",
            "decision_packet",
            str(packet.get("status", "missing")),
            packet.get("status") == "ready_for_human_review_not_execution",
            "Human owner reviews candidate provider slots and decides whether to fill the production identity-provider input.",
        ),
        step_state(
            "PIDB-002",
            "Human-filled identity-provider approval input validation",
            "approval_input_validation",
            str(approval.get("validation_status", "missing")),
            approval.get("builder_ready") is True,
            "Fill human reviewer, selected provider, source notes, and evidence review fields; then rerun the approval input validator.",
        ),
        step_state(
            "PIDB-003",
            "Phase 1 identity/tenant evidence builder",
            "phase1_evidence_builder",
            str(builder.get("status", "missing")),
            builder.get("auth_production_ready_for_review") is True,
            "Run the Phase 1 evidence builder only after validated human-filled identity-provider input exists.",
        ),
        step_state(
            "PIDB-004",
            "Local OIDC/RBAC fixture dry run",
            "auth_fixture_dry_run",
            str(fixture.get("status", "missing")),
            fixture.get("status") == "pass",
            "Use fixture results as local review support only; they do not prove real identity-provider readiness.",
            local_support_only=True,
        ),
        step_state(
            "PIDB-005",
            "Real production auth evidence path",
            "auth_evidence_path",
            str(path.get("path_status", "missing")),
            path.get("fixture_only") is False
            and path.get("real_identity_provider_selected") is True
            and path.get("real_production_tokens_validated") is True,
            "Replace fixture-only proof with real human-approved identity-provider evidence before any go/no-go closure review.",
        ),
    ]

    completed_steps = sum(1 for step in steps if step["complete"])
    status = board_status(steps, commercial["production_identity_provider_blocker_satisfied"])

    board: dict[str, Any] = {
        "production_identity_provider_readiness_board_v0_1": True,
        "board_type": "saee_production_identity_provider_readiness_board",
        "board_scope": "local_production_identity_provider_blocker_readiness_review",
        "target_blocker_id": "production_identity_provider",
        "generated_by": "scripts/saee_production_identity_provider_readiness_board.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "commercial_status": commercial["commercial_status"],
        "production_launch_status": commercial["production_launch_status"],
        "production_blocker_count": commercial["production_blocker_count"],
        "production_identity_provider_blocker_satisfied": commercial[
            "production_identity_provider_blocker_satisfied"
        ],
        "production_identity_provider_blocker_message": commercial[
            "production_identity_provider_blocker_message"
        ],
        "readiness_step_count": len(steps),
        "completed_step_count": completed_steps,
        "incomplete_step_count": len(steps) - completed_steps,
        "local_support_step_count": sum(1 for step in steps if step["local_support_only"]),
        "real_evidence_step_count": sum(1 for step in steps if not step["local_support_only"]),
        "steps": steps,
        "source_paths": {name: rel(path) for name, path in SOURCE_PATHS.items()},
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_human_closure_approval_required": True,
        "next_human_action": (
            str(approval.get("next_action", "")).strip()
            or "Complete the human-filled production identity-provider input and rerun the approval input validator."
        ),
        "auth_evidence_local_fixture_status": fixture.get("status", "missing"),
        "auth_evidence_runner_scope": auth.get("evidence_scope", "missing"),
        "fixture_only_path_status": path.get("path_status", "missing"),
    }
    board.update(FALSE_FLAGS)
    return board


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "step_id",
                "title",
                "source",
                "status",
                "complete",
                "local_support_only",
                "human_review_required",
                "next_action",
            ],
        )
        writer.writeheader()
        for step in data["steps"]:
            writer.writerow(
                {
                    "step_id": step["step_id"],
                    "title": step["title"],
                    "source": step["source"],
                    "status": step["status"],
                    "complete": step["complete"],
                    "local_support_only": step["local_support_only"],
                    "human_review_required": step["human_review_required"],
                    "next_action": step["next_action"],
                }
            )


def bool_text(value: Any) -> str:
    return str(bool(value)).lower()


def write_markdown(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SAEE Production Identity Provider Readiness Board",
        "",
        f"Status: {data['status']}.",
        "",
        "This board summarizes the current `production_identity_provider`",
        "commercial blocker path. It is a local human-review surface only.",
        "It does not select or contact an identity provider, fetch JWKS,",
        "validate production tokens, enable production auth, close blockers,",
        "launch product, or claim production readiness.",
        "",
        "## Summary",
        "",
        f"- target_blocker_id: {data['target_blocker_id']}",
        f"- commercial_status: {data['commercial_status']}",
        f"- production_launch_status: {data['production_launch_status']}",
        f"- production_blocker_count: {data['production_blocker_count']}",
        f"- production_identity_provider_blocker_satisfied: {bool_text(data['production_identity_provider_blocker_satisfied'])}",
        f"- readiness_step_count: {data['readiness_step_count']}",
        f"- completed_step_count: {data['completed_step_count']}",
        f"- blockers_closed_by_board: {data['blockers_closed_by_board']}",
        f"- production_ready: {bool_text(data['production_ready'])}",
        f"- customer_validated: {bool_text(data['customer_validated'])}",
        f"- product_launched: {bool_text(data['product_launched'])}",
        "",
        "## Step State",
        "",
        "| Step | Title | Status | Complete | Local Support Only | Source |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for step in data["steps"]:
        lines.append(
            f"| {step['step_id']} | {step['title']} | {step['status']} | "
            f"{bool_text(step['complete'])} | {bool_text(step['local_support_only'])} | "
            f"`{step['source_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Next Human Action",
            "",
            str(data["next_human_action"]),
            "",
            "## Boundary",
            "",
            "- production_identity_provider_available: false",
            "- production_identity_provider_selected: false",
            "- production_identity_provider_configured: false",
            "- production_auth_enabled: false",
            "- production_auth_ready: false",
            "- production_tokens_validated_by_codex: false",
            "- tokens_validated_in_production: false",
            "- identity_provider_contacted_by_codex: false",
            "- identity_provider_contacted: false",
            "- jwks_fetched_by_codex: false",
            "- jwks_fetched: false",
            "- oauth_oidc_available: false",
            "- rbac_available: false",
            "- rbac_enforced_in_production: false",
            "- evidence_collection_authorized: false",
            "- execution_authorized: false",
            "- development_permission_granted: false",
            "- blockers_closed_by_board: 0",
            "- production_ready: false",
            "- customer_validated: false",
            "- customer_contacted: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "- runtime_modified: false",
            "- backend_modified: false",
            "- kernel_modified: false",
            "- api_schema_modified: false",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_top_doc() -> None:
    TOP_DOC.write_text(
        """# SAEE Production Identity Provider Readiness Board v0.1

Status: local board available.

This board consolidates the current `production_identity_provider` commercial
blocker surface into one local human-review artifact. It reads existing local
decision, validation, fixture, and evidence-path outputs only.

It does not select or contact an identity provider, fetch JWKS, validate
production tokens, enable production authentication, enforce production RBAC,
close blockers, launch product, contact customers, or claim production
readiness.

## Outputs

- board JSON: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.local.json`
- board report: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.md`
- board CSV: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.csv`

## Command

```bash
python3 scripts/saee_production_identity_provider_readiness_board.py
```

## Boundary

- production_identity_provider_available: false
- production_identity_provider_selected: false
- production_identity_provider_configured: false
- production_auth_enabled: false
- production_auth_ready: false
- production_tokens_validated_by_codex: false
- tokens_validated_in_production: false
- identity_provider_contacted_by_codex: false
- identity_provider_contacted: false
- jwks_fetched_by_codex: false
- jwks_fetched: false
- oauth_oidc_available: false
- rbac_available: false
- rbac_enforced_in_production: false
- evidence_collection_authorized: false
- execution_authorized: false
- development_permission_granted: false
- blockers_closed_by_board: 0
- production_ready: false
- customer_validated: false
- customer_contacted: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE.write_text(
        """# SAEE Production Identity Provider Readiness Board Recommendation Gate

answer: recommend

recommend_for_local_human_review: true
recommend_for_production: false

## Need

The `production_identity_provider` blocker is the first open production launch
blocker. A human reviewer needs one concise board that separates local fixture
support from real identity-provider evidence.

## Recommendation

Recommend this board as a local human-review and agent-readable coordination
surface. It should not be treated as identity-provider selection, production
auth enablement, evidence collection approval, blocker closure, or production
readiness.

## Boundary

- production_identity_provider_available: false
- production_identity_provider_selected: false
- production_auth_enabled: false
- production_auth_ready: false
- production_tokens_validated_by_codex: false
- tokens_validated_in_production: false
- identity_provider_contacted_by_codex: false
- identity_provider_contacted: false
- jwks_fetched_by_codex: false
- jwks_fetched: false
- oauth_oidc_available: false
- rbac_available: false
- rbac_enforced_in_production: false
- evidence_collection_authorized: false
- execution_authorized: false
- development_permission_granted: false
- blockers_closed_by_board: 0
- production_ready: false
- customer_validated: false
- customer_contacted: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
""",
        encoding="utf-8",
    )


def main() -> None:
    board = build_board()
    write_json(OUTPUT_JSON, board)
    write_markdown(OUTPUT_MD, board)
    write_csv(OUTPUT_CSV, board)
    write_top_doc()
    write_gate()
    print(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_READINESS_BOARD: PASS "
        f"status={board['status']} "
        f"completed_step_count={board['completed_step_count']} "
        "blockers_closed_by_board=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
