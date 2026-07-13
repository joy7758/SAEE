#!/usr/bin/env python3
"""Offline adversarial smoke for SAEE First Ecosystem Demo v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.ecosystem_demo_validator import (  # noqa: E402
    DEMO_ROOT,
    REQUIRED_DOCUMENTS,
    validate_demo_data,
    validate_demo_package,
)


SERVICE = ROOT / "saee_backend/services/ecosystem_demo_validator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    scenario = load(DEMO_ROOT / "scenario/coding-agent-preflight.json")
    result = load(DEMO_ROOT / "result-example.json")
    documents = {name: (DEMO_ROOT / name).read_text(encoding="utf-8") for name in REQUIRED_DOCUMENTS}
    valid = validate_demo_package()
    assert valid["valid"] is True and valid["demo_package"] is True
    assert all(valid[key] is True for key in ("scenario_exists", "flow_exists", "result_example", "limitations"))
    assert valid["scenario_count"] >= 1 and valid["document_count"] >= 5
    assert result["recommendation"] == "REPLAN"
    assert set(result["findings"]) == {"missing_test_evidence", "insufficient_recovery_plan"}

    invalid = []
    for key in ("scenario_id", "scenario_type", "required_capabilities", "expected_recommendation", "expected_findings", "synthetic"):
        s = copy.deepcopy(scenario); s.pop(key); invalid.append((s, copy.deepcopy(result), copy.deepcopy(documents)))
    for key in ("customer_data", "external_agent", "external_execution", "deployment_authorized", "production_ready"):
        s = copy.deepcopy(scenario); s[key] = True; invalid.append((s, copy.deepcopy(result), copy.deepcopy(documents)))
    for key in ("external_agent", "external_execution", "customer_validated", "marketplace_listed", "production_ready"):
        r = copy.deepcopy(result); r["truth_boundary"][key] = True; invalid.append((copy.deepcopy(scenario), r, copy.deepcopy(documents)))
    for key in ("production_claim", "adoption_claim", "certification_claim", "security_guarantee_claim"):
        r = copy.deepcopy(result); r[key] = True; invalid.append((copy.deepcopy(scenario), r, copy.deepcopy(documents)))
    for value in ("APPROVED", "CERTIFIED", "SAFE", "DEPLOYED"):
        r = copy.deepcopy(result); r["recommendation"] = value; invalid.append((copy.deepcopy(scenario), r, copy.deepcopy(documents)))
    d = copy.deepcopy(documents); d.pop("limitations.md"); invalid.append((copy.deepcopy(scenario), copy.deepcopy(result), d))
    d = copy.deepcopy(documents); d["README.md"] = "SAEE is production ready."; invalid.append((copy.deepcopy(scenario), copy.deepcopy(result), d))
    assert len(invalid) >= 15
    assert all(validate_demo_data(s, r, d)["valid"] is False for s, r, d in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_demo_package(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"} & imports)
    assert all(valid[key] is False for key in ("external_agent", "external_execution", "customer_validated", "marketplace_listed", "production_ready"))

    print("SAEE_ECOSYSTEM_DEMO_SMOKE: PASS")
    print("demo_package=true")
    print(f"scenarios={valid['scenario_count']}")
    print(f"documents={valid['document_count']}")
    print(f"invalid_cases={len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("recommendation=REPLAN")
    print("local_demo_only=true")
    print("external_agent=false")
    print("external_execution=false")
    print("customer_validated=false")
    print("marketplace_listed=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
