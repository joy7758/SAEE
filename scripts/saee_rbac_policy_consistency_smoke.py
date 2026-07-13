#!/usr/bin/env python3
"""Check that the local preview RBAC route matrix is internally consistent.

This validates a review template only. It does not validate identity tokens,
contact an identity provider, enforce production RBAC, or claim production
authentication readiness.
"""

from __future__ import annotations

import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rbac_policy import RbacPolicyError, evaluate_rbac_route
from scripts.generate_rbac_policy_template import (
    ROLE_DEFINITIONS,
    ROUTE_PERMISSIONS,
    TEMPLATE_PATH,
    generate_template,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_RBAC_POLICY_CONSISTENCY_SMOKE: FAIL " + message)


def expect_policy_error(policy: dict, route: str, role: str, message: str) -> None:
    with tempfile.TemporaryDirectory(prefix="saee-rbac-negative-") as directory:
        path = Path(directory) / "policy.json"
        path.write_text(json.dumps(policy), encoding="utf-8")
        try:
            evaluate_rbac_route(str(path), route, role)
        except RbacPolicyError:
            return
    raise SystemExit("SAEE_RBAC_POLICY_CONSISTENCY_SMOKE: FAIL " + message)


def main() -> None:
    generate_template()
    policy = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    roles = set(ROLE_DEFINITIONS)
    route_scopes = {item["route"]: item for item in policy["route_scopes"]}

    require(set(route_scopes) == set(ROUTE_PERMISSIONS), "route scope set drift")
    require("*" not in roles, "wildcard role is forbidden")

    for route, (permission, allowed_roles) in ROUTE_PERMISSIONS.items():
        item = route_scopes[route]
        require(item["required_permission"] == permission, f"permission drift for {route}")
        policy_roles = set(item["allowed_roles"])
        require(policy_roles == set(allowed_roles), f"allowed role drift for {route}")
        require(policy_roles <= roles, f"unknown role in {route}")
        require(permission in policy["required_permissions"], f"unknown permission for {route}")
        for role in allowed_roles:
            decision = evaluate_rbac_route(str(TEMPLATE_PATH), route, role)
            require(decision.allowed, f"listed role denied for {route}: {role}")
            require(decision.required_permission == permission, f"decision permission drift for {route}")
        denied = "__unknown_role__"
        decision = evaluate_rbac_route(str(TEMPLATE_PATH), route, denied)
        require(not decision.allowed, f"unknown role allowed for {route}")

    try:
        evaluate_rbac_route(str(TEMPLATE_PATH), "GET /not-a-route", "viewer")
    except RbacPolicyError:
        pass
    else:
        raise SystemExit("SAEE_RBAC_POLICY_CONSISTENCY_SMOKE: FAIL unknown route accepted")

    missing_permission = deepcopy(policy)
    operator = next(item for item in missing_permission["roles"] if item["role"] == "evaluator_operator")
    operator["permissions"].remove("experiment:run")
    expect_policy_error(
        missing_permission,
        "POST /experiment/run",
        "evaluator_operator",
        "route-listed role without required permission accepted",
    )

    unknown_allowed_role = deepcopy(policy)
    unknown_allowed_role["route_scopes"][0]["allowed_roles"].append("unknown_role")
    expect_policy_error(
        unknown_allowed_role,
        unknown_allowed_role["route_scopes"][0]["route"],
        "owner",
        "unknown allowed role accepted",
    )

    duplicate_role = deepcopy(policy)
    duplicate_role["roles"].append(deepcopy(duplicate_role["roles"][0]))
    expect_policy_error(duplicate_role, "GET /experiment", "viewer", "duplicate role accepted")

    duplicate_route = deepcopy(policy)
    duplicate_route["route_scopes"].append(deepcopy(duplicate_route["route_scopes"][0]))
    expect_policy_error(duplicate_route, "GET /experiment", "viewer", "duplicate route accepted")

    positive_production_claim = deepcopy(policy)
    positive_production_claim["production_auth_ready"] = True
    expect_policy_error(
        positive_production_claim,
        "GET /experiment",
        "viewer",
        "positive production claim accepted",
    )

    print(
        "SAEE_RBAC_POLICY_CONSISTENCY_SMOKE: PASS "
        f"routes={len(route_scopes)} roles={len(roles)} "
        "unknown_role_denied=true unknown_route_denied=true "
        "role_permission_consistency=true duplicate_role_route_denied=true "
        "production_auth_ready=false"
    )


if __name__ == "__main__":
    main()
