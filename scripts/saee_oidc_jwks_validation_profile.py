#!/usr/bin/env python3
"""Build hash-bound agent evidence for the offline OIDC/JWKS narrow slice."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "agent_recommendation/oidc_jwks_verifier/run_001/independent_agent_validation.local.json"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/oidc_jwks_verifier_evidence"
JSON_PATH = OUTPUT_DIR / "oidc_jwks_verifier_evidence.local.json"
MD_PATH = OUTPUT_DIR / "oidc_jwks_verifier_evidence.md"
SOURCES = (
    "saee_backend/services/oidc_jwks_verifier.py",
    "saee_backend/services/authorization_context.py",
    "scripts/saee_oidc_jwks_verifier_smoke.py",
    "scripts/saee_oidc_rbac_handler_boundary_smoke.py",
    "scripts/saee_agent_blocker_priority_index.py",
    "phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.json",
    "docs/strategy/SAEE_PROVIDER_NEUTRAL_OIDC_JWKS_EVOLUTION_PROPOSAL.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script: str) -> str:
    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"local validation command failed: {script}")
    return result.stdout.strip()


def main() -> None:
    validation: dict[str, Any] = json.loads(VALIDATION.read_text(encoding="utf-8"))
    if validation.get("verdict") != "recommend" or validation.get("blocker_count") != 0:
        raise RuntimeError("independent recommendation gate is not recommend/0")
    verifier_output = run("scripts/saee_oidc_jwks_verifier_smoke.py")
    handler_output = run("scripts/saee_oidc_rbac_handler_boundary_smoke.py")
    priority_output = run("scripts/saee_agent_blocker_priority_index.py")
    required = {
        "SAEE_OIDC_JWKS_VERIFIER_SMOKE: PASS": verifier_output,
        "negative_cases=43": verifier_output,
        "network_calls=0": verifier_output,
        "token_or_key_leakage=0": verifier_output,
        "SAEE_OIDC_RBAC_HANDLER_BOUNDARY_SMOKE: PASS": handler_output,
        "rejected_before_handler=6": handler_output,
        "SAEE_AGENT_BLOCKER_PRIORITY_INDEX: PASS": priority_output,
        "first_priority_blocker_id=production_identity_provider": priority_output,
    }
    missing = [token for token, output in required.items() if token not in output]
    if missing:
        raise RuntimeError("missing local evidence token")
    payload = {
        "oidc_jwks_verifier_evidence_v0_1": True,
        "generated_at": date.today().isoformat(),
        "generated_by": "scripts/saee_oidc_jwks_validation_profile.py",
        "evidence_scope": "provider_neutral_offline_signed_fixture_only",
        "agent_validation_primary": True,
        "human_validation_used": False,
        "independent_agent_validation": str(VALIDATION.relative_to(ROOT)),
        "independent_adversarial_review_completed": True,
        "independent_adversarial_review_verdict": "recommend",
        "independent_adversarial_blocker_count": 0,
        "source_sha256": {path: sha256(ROOT / path) for path in SOURCES},
        "valid_signed_fixtures": 2,
        "negative_cases_passed": 43,
        "deterministic_runs_passed": 10,
        "handler_boundary_negative_cases_passed": 6,
        "network_calls": 0,
        "token_or_key_leakage": 0,
        "provider_neutral_oidc_verifier_core_available": True,
        "local_signed_jwks_validation_completed": True,
        "local_oidc_rbac_binding_reviewed": True,
        "production_blockers_closed": 0,
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
        "next_action": "Select and review a real China-market identity provider in a separate external evidence gate; do not reuse local fixture proof as production evidence.",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    hashes = "\n".join(f"- `{path}`: `{digest}`" for path, digest in payload["source_sha256"].items())
    MD_PATH.write_text(
        f"""# SAEE 离线 OIDC/JWKS 智能体验证证据

结论：`recommend`，独立智能体阻塞 `0` 项。证据范围仅为 provider-neutral、本地离线、签名合成夹具。

- 有效签名与轮换密钥：2 项
- 对抗负例：43 项
- 确定性复跑：10 次
- handler 前终止负例：6 项
- 网络调用：0
- token/密钥泄漏：0
- 关闭生产阻塞：0

允许晋级的本地窄字段：`provider_neutral_oidc_verifier_core_available=true`、`local_signed_jwks_validation_completed=true`、`local_oidc_rbac_binding_reviewed=true`。

真实 IdP、外部 JWKS、生产 token、生产 OIDC/RBAC、客户验证、生产就绪和产品上线仍全部为 `false`。

## 源码哈希

{hashes}
""",
        encoding="utf-8",
    )
    print("SAEE_OIDC_JWKS_VALIDATION_PROFILE: PASS")
    print(f"json={JSON_PATH.relative_to(ROOT)}")
    print("independent_adversarial_review_verdict=recommend")
    print("production_blockers_closed=0")


if __name__ == "__main__":
    main()
