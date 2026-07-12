#!/usr/bin/env python3
"""Audit the curated SAEE-v0.1-alpha public-source candidate without staging it."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "release/SAEE-v0.1-alpha/public-source-allowlist.txt"
REPORT = ROOT / "release/SAEE-v0.1-alpha/public-baseline-audit.json"
SECRET_PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "openai_style_secret": re.compile(rb"sk-[A-Za-z0-9_-]{32,}"),
    "github_token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
}


def git_head_exists() -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def staged_files() -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    )
    return [line for line in completed.stdout.splitlines() if line]


def main() -> None:
    paths = [line.strip() for line in ALLOWLIST.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    missing = [path for path in paths if not (ROOT / path).is_file()]
    unsafe_names = [path for path in paths if any(part.startswith(".env") or "secret" in part.lower() or "credential" in part.lower() for part in Path(path).parts)]
    findings = []
    total_bytes = 0
    for path in paths:
        candidate = ROOT / path
        if not candidate.is_file():
            continue
        data = candidate.read_bytes()
        total_bytes += len(data)
        for pattern_id, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                findings.append({"path": path, "pattern": pattern_id})
    staged = staged_files()
    result = {
        "audit_id": "saee-v0.1-alpha-public-baseline-audit",
        "status": "human_review_required" if not missing and not unsafe_names and not findings else "failed_local_safety_check",
        "candidate_file_count": len(paths),
        "candidate_bytes": total_bytes,
        "missing_files": missing,
        "unsafe_filenames": unsafe_names,
        "high_confidence_secret_findings": findings,
        "git_head_exists": git_head_exists(),
        "root_license_present": (ROOT / "LICENSE").is_file(),
        "release_assets_not_in_source_allowlist": [
            "output/pdf/SAEE_Baidu_Cloud_Technical_Whitepaper_v1.0.pdf",
            "output/video/SAEE_Baidu_Cloud_Demo_v1.0.mp4",
            "output/video/SAEE_Baidu_Cloud_Demo_v1.0.zh-CN.srt",
            "output/video/SAEE_Baidu_Cloud_Demo_v1.0.manifest.json"
        ],
        "truth_boundary": {
            "files_staged": bool(staged),
            "staged_file_count": len(staged),
            "commit_created": git_head_exists(),
            "tag_created": False,
            "github_release_created": False,
            "external_action_authorized": True,
            "external_action_authorization_scope_limited": True
        }
    }
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if missing or unsafe_names or findings:
        raise SystemExit("SAEE_PUBLIC_BASELINE_AUDIT: FAIL " + json.dumps({"missing": missing, "unsafe_names": unsafe_names, "findings": findings}))
    print(
        "SAEE_PUBLIC_BASELINE_AUDIT: PASS "
        f"candidate_files={len(paths)} candidate_bytes={total_bytes} "
        f"git_head_exists={str(result['git_head_exists']).lower()} "
        f"root_license_present={str(result['root_license_present']).lower()} "
        f"high_confidence_secret_findings=0 files_staged={str(bool(staged)).lower()}"
    )


if __name__ == "__main__":
    main()
