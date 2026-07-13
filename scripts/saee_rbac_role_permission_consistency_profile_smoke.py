#!/usr/bin/env python3
"""Smoke check for the agent-readable RBAC consistency profile."""

from __future__ import annotations

from saee_rbac_role_permission_consistency_profile import build_profile


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_RBAC_ROLE_PERMISSION_CONSISTENCY_PROFILE_SMOKE: FAIL " + message)


def main() -> None:
    data = build_profile()
    require(data["role_count"] == 5, "role count")
    require(data["route_count"] == 19, "route count")
    require(data["negative_cases_passed"] == data["negative_cases_total"] == 5, "negative cases")
    require(data["role_permission_consistency_enforced"] is True, "consistency")
    require(data["external_calls_made"] is False, "external calls")
    require(data["production_auth_ready"] is False, "production auth")
    require(data["blockers_closed"] == 0, "blockers")
    print("SAEE_RBAC_ROLE_PERMISSION_CONSISTENCY_PROFILE_SMOKE: PASS roles=5 routes=19 negative_cases=5/5 external_calls=false production_auth_ready=false blockers_closed=0")


if __name__ == "__main__":
    main()
