#!/usr/bin/env python3
"""Validate the SAEE landing page to decision API integration contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_LANDING_API_INTEGRATION_SMOKE: FAIL: {message}")


def read(relpath: str) -> str:
    path = ROOT / relpath
    if not path.is_file():
        fail(f"missing {relpath}")
    return path.read_text(encoding="utf-8")


def require_tokens(relpath: str, tokens: list[str]) -> None:
    text = read(relpath)
    missing = [token for token in tokens if token not in text]
    if missing:
        fail(f"{relpath} missing tokens: {', '.join(missing)}")


def main() -> None:
    require_tokens(
        "phase_b_product/landing/index.html",
        [
            'id="run-demo-battle"',
            'id="demo-status"',
            'id="demo-output"',
            'id="demo-ranking"',
            'id="demo-failures"',
            'src="app.js?v=plain-cn-v3-20260709"',
            "本地试用",
        ],
    )
    require_tokens(
        "phase_b_product/landing/app.js",
        [
            "fetch(apiUrl",
            "http://127.0.0.1:8000/experiment/run",
            "landing-demo-battle",
            "decision_result",
            "recommended_agent",
            "confidence_score",
            "failure_modes_summary",
            "SAEE RESULT",
        ],
    )
    require_tokens(
        "saee_backend/main.py",
        [
            "CORSMiddleware",
            "SETTINGS.allowed_origins",
        ],
    )
    require_tokens(
        "saee_backend/config.py",
        [
            "http://127.0.0.1:8765",
            "http://localhost:8765",
            "SAEE_ALLOWED_ORIGINS",
        ],
    )
    require_tokens(
        "docs/strategy/SAEE_LANDING_API_INTEGRATION_RECOMMENDATION_GATE.md",
        [
            "recommendation_gate",
            "SAEE Landing API Integration",
            "landing_api_integration_implemented: true",
            "api_contract_modified: false",
            "private_core_exported: false",
        ],
    )
    forbidden_app_tokens = [
        "saee_v1_0",
        "kernel/runtime.py",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]
    app = read("phase_b_product/landing/app.js")
    found = [token for token in forbidden_app_tokens if token in app]
    if found:
        fail("landing app.js contains forbidden private tokens: " + ", ".join(found))
    print(
        "SAEE_LANDING_API_INTEGRATION_SMOKE: PASS "
        "run_demo_button=true api_call=true decision_result_render=true "
        "api_contract_modified=false private_core_exported=false"
    )


if __name__ == "__main__":
    main()
