#!/usr/bin/env python3
"""Offline adversarial smoke for SAEE GitHub Product Consolidation v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.product_consolidation_validator import (  # noqa: E402
    DOCS, MAP_PATH, README_PATH, validate_product_consolidation, validate_product_consolidation_repository,
)


SERVICE = ROOT / "saee_backend/services/product_consolidation_validator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    valid = validate_product_consolidation_repository()
    assert valid["valid"] is True, valid
    assert all(valid[key] is True for key in ("product_identity", "module_mapping", "README_complete", "language_policy", "boundary_statements"))
    assert all(valid[key] is False for key in ("canonical_identity_changed", "historical_repository_notice_written", "repository_renamed", "history_rewritten", "public_release", "external_announcement", "production_ready"))

    base = load(MAP_PATH)
    readme = README_PATH.read_text(encoding="utf-8")
    docs = {key: path.read_text(encoding="utf-8") for key, path in DOCS.items()}
    invalid: list[tuple[dict, str, dict[str, str]]] = []
    for field, value in (("theory_name", "Smart Agent Execution & Evidence"), ("engineering_core", "Agent Audit Engine"), ("primary_language", "en")):
        item = copy.deepcopy(base); item["canonical_identity"][field] = value; invalid.append((item, readme, copy.deepcopy(docs)))
    for key in ("canonical_identity_changed", "historical_repository_deleted", "historical_repository_notice_written", "repository_renamed", "history_rewritten", "public_release", "external_announcement", "production_ready"):
        item = copy.deepcopy(base); item["truth_boundary"][key] = True; invalid.append((item, readme, copy.deepcopy(docs)))
    item = copy.deepcopy(base); item["modules"][0]["module_id"] = item["modules"][1]["module_id"]; invalid.append((item, readme, copy.deepcopy(docs)))
    item = copy.deepcopy(base); item["modules"][0]["source"] = "/Users/example/private/repository"; invalid.append((item, readme, copy.deepcopy(docs)))
    item = copy.deepcopy(base); next(row for row in item["modules"] if row["module_id"] == "audit_evidence")["core"] = True; invalid.append((item, readme, copy.deepcopy(docs)))
    invalid.append((copy.deepcopy(base), readme.replace("为什么需要 SAEE", "section removed"), copy.deepcopy(docs)))
    invalid.append((copy.deepcopy(base), readme.replace("# SAEE 数字生物圈进化引擎", "# SAEE"), copy.deepcopy(docs)))
    invalid.append((copy.deepcopy(base), readme + "\n# SAEE Smart Agent Execution & Evidence\n", copy.deepcopy(docs)))
    changed = copy.deepcopy(docs); changed["asset_map"] = changed["asset_map"].replace("historical_repository_notice_written=false", "historical_repository_notice_written=true"); invalid.append((copy.deepcopy(base), readme, changed))
    assert len(invalid) >= 15
    assert all(validate_product_consolidation(item, readme=text, documents=documents)["valid"] is False for item, text, documents in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_product_consolidation_repository(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module: imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib"} & imports)

    print("SAEE_PRODUCT_CONSOLIDATION_SMOKE: PASS")
    print("product_identity=true")
    print(f"module_mapping={len(base['modules'])}/11")
    print("README_complete=true")
    print("language_policy=zh-CN_primary_en_secondary")
    print("boundary_statements=true")
    print(f"invalid_cases={len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("canonical_identity_changed=false")
    print("historical_repository_notice_written=false")
    print("repository_renamed=false")
    print("history_rewritten=false")
    print("public_release=false")
    print("external_announcement=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
