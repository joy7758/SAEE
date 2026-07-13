#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Agent Readiness product packaging."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.commercial_positioning_validator import (  # noqa: E402
    PACKAGE_ROOT,
    validate_package,
    validate_product,
)


SERVICE = ROOT / "saee_backend/services/commercial_positioning_validator.py"


def main() -> int:
    value = json.loads((PACKAGE_ROOT / "product.json").read_text(encoding="utf-8"))
    valid = validate_package()
    assert valid["valid"] is True, valid
    assert all(valid[key] is True for key in (
        "product_definition", "assessment_package", "report_template", "demo_flow", "limitations",
    ))

    invalid: list[dict] = []
    for phrase in ("certification", "guaranteed safety", "production approval", "best agent ranking", "customer success"):
        bad = copy.deepcopy(value)
        bad["name"] = phrase
        invalid.append(bad)
    for key in (
        "production_service", "public_service", "commercial_delivery_completed",
        "customer_validated", "market_validation", "revenue_confirmed", "deployment_authorized",
    ):
        bad = copy.deepcopy(value)
        bad["truth_boundary"][key] = True
        invalid.append(bad)
    for mutate in (
        lambda v: v.update({"product_id": "other"}),
        lambda v: v.update({"language": "en-US"}),
        lambda v: v.update({"allowed_recommendations": ["APPROVED"]}),
        lambda v: v.update({"canonical_service_ref": "missing.py"}),
        lambda v: v.update({"demo_ref": "https://example.invalid/demo"}),
        lambda v: v.update({"truth_boundary": {}}),
    ):
        bad = copy.deepcopy(value)
        mutate(bad)
        invalid.append(bad)
    assert len(invalid) >= 15
    assert all(validate_product(case)["valid"] is False for case in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        assert json.dumps(validate_package(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"} & imports)
    assert all(valid[key] is False for key in (
        "network_accessed", "subprocess_started", "external_execution",
        "commercial_delivery_completed", "production_service",
    ))

    print("SAEE_AGENT_READINESS_PRODUCTIZATION_SMOKE: PASS")
    print("product_definition=true")
    print("assessment_package=true")
    print("report_template=true")
    print("demo_flow=true")
    print("limitations=true")
    print(f"invalid_cases={len(invalid)}")
    print("deterministic_runs=5/5")
    print("canonical_commercial_assessment_service_reused=true")
    print("new_runtime_created=false")
    print("commercial_delivery_completed=false")
    print("customer_validated=false")
    print("market_validation=false")
    print("production_service=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

