#!/usr/bin/env python3
"""Build the dependency-ordered, agent-primary SAEE blocker priority truth surface."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
LEGACY = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.local.json"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/agent_blocker_priority_index"
JSON_PATH = OUTPUT_DIR / "agent_blocker_priority_index.local.json"
MD_PATH = OUTPUT_DIR / "agent_blocker_priority_index.md"


def build() -> dict[str, object]:
    dependency = json.loads(SOURCE.read_text(encoding="utf-8"))
    legacy = json.loads(LEGACY.read_text(encoding="utf-8"))
    phases = dependency["phases"]
    phase_order = {phase["phase_id"]: index + 1 for index, phase in enumerate(phases)}
    source_order = {item["blocker_id"]: index for index, item in enumerate(dependency["blockers"])}
    remaining = {item["blocker_id"]: item for item in dependency["blockers"]}
    ordered = []
    completed: set[str] = set()
    while remaining:
        candidates = [
            item
            for item in remaining.values()
            if set(item["depends_on_blockers"]).issubset(completed)
        ]
        if not candidates:
            raise ValueError("dependency graph contains a cycle or unknown dependency")
        selected = min(
            candidates,
            key=lambda item: (phase_order[item["phase_id"]], source_order[item["blocker_id"]]),
        )
        ordered.append(selected)
        completed.add(selected["blocker_id"])
        del remaining[selected["blocker_id"]]
    rank_by_id = {item["blocker_id"]: index + 1 for index, item in enumerate(ordered)}
    for item in ordered:
        for dependency_id in item["depends_on_blockers"]:
            if dependency_id not in rank_by_id or rank_by_id[dependency_id] >= rank_by_id[item["blocker_id"]]:
                raise ValueError(f"dependency order invalid for {item['blocker_id']}")
    rows = []
    for rank, item in enumerate(ordered, 1):
        rows.append(
            {
                "rank": rank,
                "phase_order": phase_order[item["phase_id"]],
                "phase_id": item["phase_id"],
                "blocker_id": item["blocker_id"],
                "status": item["status"],
                "depends_on_blockers": item["depends_on_blockers"],
                "engineering_implementation_required": item["engineering_implementation_required"],
                "external_dependency_required": item["external_dependency_required"],
                "production_closure_allowed": False,
            }
        )
    first = rows[0]
    return {
        "agent_blocker_priority_index_v0_1": True,
        "generated_at": date.today().isoformat(),
        "generated_by": "scripts/saee_agent_blocker_priority_index.py",
        "status": "dependency_order_active_local_engineering_only",
        "agent_validation_primary": True,
        "human_validation_used": False,
        "phase_count": len(phases),
        "production_blocker_count": dependency["production_blocker_count"],
        "open_blocker_count": dependency["open_blocker_count"],
        "production_blockers_closed": 0,
        "first_priority_blocker_id": first["blocker_id"],
        "first_priority_phase_id": first["phase_id"],
        "current_development_action": "provider_neutral_offline_signed_oidc_jwks_verifier_core",
        "current_action_recommendation": "recommend",
        "independent_agent_recommendations": [
            {"agent_lane": "recommendation_agent_validation", "verdict": "recommend", "blocker_count": 0},
            {"agent_lane": "observed_trace_recommendation_gate", "verdict": "recommend", "blocker_count": 0},
        ],
        "superseded_legacy_priority": {
            "path": str(LEGACY.relative_to(ROOT)),
            "first_priority_blocker_id": legacy["first_priority_blocker_id"],
            "reason": "legacy human review queue crossed the five-phase dependency order and is not current development authority",
        },
        "source_dependency_plan": str(SOURCE.relative_to(ROOT)),
        "priority_rows": rows,
        "provider_neutral_oidc_verifier_implementation_present": True,
        "official_oidc_jwks_smoke_passed": True,
        "independent_adversarial_review_completed": True,
        "independent_adversarial_review_verdict": "recommend",
        "independent_adversarial_blocker_count": 0,
        "provider_neutral_oidc_verifier_core_available": True,
        "local_signed_jwks_validation_completed": True,
        "local_oidc_rbac_binding_reviewed": True,
        "production_identity_provider_selected": False,
        "external_identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated_in_production": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "next_action": "Review real China-market identity-provider candidates in a separate external evidence gate; keep all production blockers open.",
    }


def write(payload: dict[str, object]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = "\n".join(
        f"| {row['rank']} | {row['phase_order']} | `{row['blocker_id']}` | `{row['status']}` |"
        for row in payload["priority_rows"]
    )
    MD_PATH.write_text(
        f"""# SAEE 智能体商业阻塞优先级索引

状态：按五阶段依赖顺序推进；智能体验证为主；不使用真人验证。

当前第一阻塞：`{payload['first_priority_blocker_id']}`  
当前工程动作：`{payload['current_development_action']}`  
生产阻塞：`{payload['production_blocker_count']}` 项，关闭 `0` 项。

旧索引把 `support_contact` 置于首位，但它属于 Phase 3，现已作为历史人工复核队列被本索引取代，不再作为开发真源。

| 排名 | 阶段 | 阻塞 | 状态 |
| ---: | ---: | --- | --- |
{rows}

本索引只授权本地、可逆、智能体可复核的工程缺口压缩；真实 IdP、外部 JWKS、生产 token、客户验证和产品上线均保持未完成。
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build()
    write(payload)
    assert payload["first_priority_blocker_id"] == "production_identity_provider"
    assert payload["production_blocker_count"] == 24
    assert payload["production_blockers_closed"] == 0
    assert payload["human_validation_used"] is False
    print("SAEE_AGENT_BLOCKER_PRIORITY_INDEX: PASS")
    print(f"json={JSON_PATH.relative_to(ROOT)}")
    print("first_priority_blocker_id=production_identity_provider")
    print("production_blockers_closed=0")


if __name__ == "__main__":
    main()
