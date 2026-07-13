#!/usr/bin/env python3
"""Fail closed when the SAEE public surface regresses on bounded security rules."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "sites/saee-commercial"
PUBLIC = SITE / "public"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PUBLIC_SURFACE_SECURITY_GATE: FAIL: " + message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    landing = read(ROOT / "phase_b_product/landing/app.js")
    viewer = read(PUBLIC / "data/data-viewer.js")
    policy = read(PUBLIC / "data/data-file-policy.js")
    page_sources = "\n".join(read(path) for path in sorted((SITE / "app").rglob("page.tsx")))

    require("innerHTML" not in landing, "local landing must not render API values with innerHTML")
    require("localStorage" not in landing, "local landing must not persist preview tokens")
    require("sessionStorage" in landing, "local landing must use short browser-session token storage")
    require("innerHTML" not in viewer, "public data viewer must not use innerHTML")
    require("eval(" not in viewer and "new Function" not in viewer, "public data viewer must not execute data")
    require("allowedFiles.has(file)" in viewer, "public data viewer must enforce an explicit allowlist")

    allowed = set(re.findall(r'"([a-zA-Z0-9._-]+\.json)"', policy))
    linked = set(re.findall(r'jsonView\("([a-zA-Z0-9._-]+\.json)"\)', page_sources))
    linked.update(re.findall(r'(?:request|response):\s*"([a-zA-Z0-9._-]+\.json)"', page_sources))
    require(linked <= allowed, "viewer allowlist misses: " + ", ".join(sorted(linked - allowed)))
    for filename in sorted(allowed):
        path = PUBLIC / filename
        require(path.is_file(), f"allowlisted file is missing: {filename}")
        json.loads(path.read_text(encoding="utf-8"))

    public_text_suffixes = {".html", ".js", ".json", ".md", ".txt", ".xml", ".py"}
    public_text = "\n".join(
        read(path)
        for path in sorted(PUBLIC.rglob("*"))
        if path.is_file() and path.suffix.lower() in public_text_suffixes
    )
    require("/Users/" not in public_text, "public files must not expose macOS user paths")
    require("/home/" not in public_text, "public files must not expose Linux user paths")
    require("C:\\Users\\" not in public_text, "public files must not expose Windows user paths")

    json.loads(read(PUBLIC / "security-policy.json"))
    headers = read(PUBLIC / "_headers")
    for header in ("Content-Security-Policy", "Strict-Transport-Security", "X-Content-Type-Options", "Permissions-Policy"):
        require(header in headers, f"public headers missing {header}")

    sitemap = read(PUBLIC / "sitemap.xml")
    for route in ("/", "/for-agents/", "/research/", "/security/", "/llms.txt"):
        require(f"https://redcrag.cn{route}" in sitemap, f"sitemap missing {route}")
    require(".json</loc>" not in sitemap, "human sitemap must not send visitors to raw JSON")
    require((ROOT / "SECURITY.md").is_file(), "repository SECURITY.md is missing")

    print(
        "SAEE_PUBLIC_SURFACE_SECURITY_GATE: PASS "
        f"allowlisted_json={len(allowed)} linked_json={len(linked)} "
        "persistent_token_storage=false dynamic_html=false"
    )


if __name__ == "__main__":
    main()
