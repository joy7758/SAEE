#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Cloud Ecosystem Strategy v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.cloud_ecosystem_strategy_validator import (  # noqa: E402
    MATRIX_PATH,
    validate_priority_matrix,
    validate_strategy_package,
)


SERVICE = ROOT / "saee_backend/services/cloud_ecosystem_strategy_validator.py"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    valid = validate_strategy_package()
    assert valid["valid"] is True, valid
    assert valid["platform_count"] >= 5
    assert valid["document_count"] >= 5
    assert valid["integration_package"] is True

    invalid: list[dict] = []
    for phrase in (
        "official support", "official integration", "cloud partner", "partnered with",
        "marketplace listed", "marketplace submission completed", "integration completed",
    ):
        bad = copy.deepcopy(matrix)
        bad["platforms"][0]["limitations"].append(phrase)
        invalid.append(bad)
    for key in (
        "cloud_integration_executed", "official_support", "partner_contact",
        "marketplace_submission", "marketplace_listed", "external_agents_connected",
        "customer_validated", "production_ready",
    ):
        bad = copy.deepcopy(matrix)
        bad["truth_boundary"][key] = True
        invalid.append(bad)
    for mutate in (
        lambda v: v.update({"platforms": v["platforms"][:4]}),
        lambda v: v["platforms"].pop(),
        lambda v: v["platforms"][0].pop("integration_surface"),
        lambda v: v["platforms"][0].update({"commercial_readiness": "PRODUCTION_READY"}),
        lambda v: v["platforms"][0].update({"ecosystem": "UNKNOWN"}),
        lambda v: v.update({"truth_boundary": {}}),
    ):
        bad = copy.deepcopy(matrix)
        mutate(bad)
        invalid.append(bad)
    assert len(invalid) >= 20
    assert all(validate_priority_matrix(case)["valid"] is False for case in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        assert json.dumps(validate_strategy_package(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib"} & imports)
    assert all(valid[key] is False for key in (
        "network_accessed", "subprocess_started", "external_execution",
        "cloud_integration_executed", "partner_contact", "marketplace_submission", "production_ready",
    ))

    print("SAEE_CLOUD_ECOSYSTEM_STRATEGY_SMOKE: PASS")
    print(f"platforms={valid['platform_count']}/5")
    print(f"documents={valid['document_count']}")
    print("package=true")
    print(f"invalid_cases={len(invalid)}")
    print("deterministic_runs=5/5")
    print("strategy_defined=true")
    print("priority_matrix=true")
    print("integration_package=true")
    print("boundary_defined=true")
    print("cloud_integration_executed=false")
    print("partner_contact=false")
    print("marketplace_submission=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

