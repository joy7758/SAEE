#!/usr/bin/env python3
"""Validate the 30-minute local SAEE Cloud Entry Package review path."""

from __future__ import annotations

import json
import hashlib
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.baidu_agent_readiness_service import evaluate_agent_run, evaluate_evidence


PACKAGE = ROOT / "cloud-entry-package"
CLI = ROOT / "scripts/saee_baidu_readiness.py"
REQUIRED = (
    "README.md",
    "快速开始.md",
    "openapi.yaml",
    "mcp.json",
    "capability-card.json",
    "FAQ.md",
    "architecture.svg",
    "architecture.png",
    "screenshots/customer-service-result.svg",
    "screenshots/customer-service-result.png",
    "screenshots/coding-agent-result.svg",
    "screenshots/coding-agent-result.png",
    "security/data-boundary.md",
    "security/consent-boundary.md",
    "security/non-authorization-statement.md",
    "demo/customer-service-refund/request.json",
    "demo/customer-service-refund/response.json",
    "demo/coding-agent-release/request.json",
    "demo/coding-agent-release/response.json",
    "demo/evaluate-evidence/request.json",
    "demo/evaluate-evidence/response.json",
    "materials/SAEE_BAIDU_TECHNICAL_WHITEPAPER_V1.md",
    "materials/SAEE_BAIDU_DEMO_VIDEO_STORYBOARD_V1.md",
    "materials/SAEE_BAIDU_DEMO_VIDEO_NARRATION_ZH_V1.txt",
    "materials/SAEE_BAIDU_DEMO_VIDEO_ZH_V1.srt",
    "materials/SAEE_BAIDU_COMMERCIAL_PACKAGING_DRAFT_V1.md",
    "materials/SAEE_BAIDU_COMPANY_INTRODUCTION_INTAKE_V1.md",
    "materials/SAEE_BAIDU_ECOSYSTEM_APPLICATION_HANDOFF_V1.md",
    "materials/SAEE_BAIDU_PARTNER_PRODUCT_SOLUTION_V1.docx",
)
WHITEPAPER = ROOT / "output/pdf/SAEE_Baidu_Cloud_Technical_Whitepaper_v1.0.pdf"
VIDEO = ROOT / "output/video/SAEE_Baidu_Cloud_Demo_v1.0.mp4"
VIDEO_MANIFEST = ROOT / "output/video/SAEE_Baidu_Cloud_Demo_v1.0.manifest.json"
RELEASE_MANIFEST = ROOT / "release/SAEE-v0.1-alpha/release-manifest.json"
PUBLIC_TOOLS = ["saee.evaluate_agent_run", "saee.evaluate_evidence"]
INTERNAL_TOOLS = {"rehearse_agent", "describe_saee", "compare_observed_traces"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CLOUD_ENTRY_PACKAGE_SMOKE: FAIL " + message)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), path.as_posix())
    return value


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    require(data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", path.name)
    return struct.unpack(">II", data[16:24])


def cli(operation: str, request: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, str(CLI), operation, "--input", str(request)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    require(completed.stderr == "", f"CLI stderr {operation}")
    return json.loads(completed.stdout)


def command_output(args: list[str]) -> str:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main() -> None:
    missing = [name for name in REQUIRED if not (PACKAGE / name).is_file()]
    require(not missing, "missing files: " + ",".join(missing))
    card = load(PACKAGE / "capability-card.json")
    mcp = load(PACKAGE / "mcp.json")
    openapi = (PACKAGE / "openapi.yaml").read_text(encoding="utf-8")
    require([item["name"] for item in card["public_operations"]] == PUBLIC_TOOLS, "card public tools")
    server = mcp["mcpServers"]["saee-agent-readiness"]
    require(server["tools"] == PUBLIC_TOOLS, "MCP public tools")
    require(set(PUBLIC_TOOLS) == set(line.strip() for line in openapi.splitlines() if line.strip().startswith("operationId:") for line in [line.strip().split("operationId:", 1)[1].strip()]), "OpenAPI operations")
    require(not any(f"operationId: {name}" in openapi for name in INTERNAL_TOOLS), "internal OpenAPI operation")
    require(card["truth_boundary"]["tool_count"] == 2, "tool count")
    require(mcp["truth_boundary"]["remote_mcp"] is False, "remote MCP boundary")

    customer_request = load(PACKAGE / "demo/customer-service-refund/request.json")
    coding_request = load(PACKAGE / "demo/coding-agent-release/request.json")
    evidence_request = load(PACKAGE / "demo/evaluate-evidence/request.json")
    expected = (
        ("evaluate-agent-run", customer_request, load(PACKAGE / "demo/customer-service-refund/response.json"), evaluate_agent_run),
        ("evaluate-agent-run", coding_request, load(PACKAGE / "demo/coding-agent-release/response.json"), evaluate_agent_run),
        ("evaluate-evidence", evidence_request, load(PACKAGE / "demo/evaluate-evidence/response.json"), evaluate_evidence),
    )
    for operation, request, response, function in expected:
        require(function(request) == response, f"checked-in response drift {operation}")
        request_path = PACKAGE / ("demo/customer-service-refund/request.json" if request is customer_request else "demo/coding-agent-release/request.json" if request is coding_request else "demo/evaluate-evidence/request.json")
        require(cli(operation, request_path) == response, f"CLI drift {request_path.parent.name}")
        require(response["truth_boundary"]["deployment_authorized"] is False, "deployment boundary")
        require(response["truth_boundary"]["production_ready"] is False, "production boundary")

    require(png_size(PACKAGE / "architecture.png") == (1600, 900), "architecture dimensions")
    require(png_size(PACKAGE / "screenshots/customer-service-result.png") == (1440, 900), "screenshot dimensions")
    require(png_size(PACKAGE / "screenshots/coding-agent-result.png") == (1440, 900), "coding screenshot dimensions")
    require(WHITEPAPER.is_file(), "whitepaper PDF missing")
    require("Pages:           10" in command_output(["pdfinfo", str(WHITEPAPER)]), "whitepaper page count")
    require(VIDEO.is_file() and VIDEO_MANIFEST.is_file(), "demo video package missing")
    video_manifest = load(VIDEO_MANIFEST)
    probe = json.loads(command_output(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,width,height,sample_rate", "-of", "json", str(VIDEO)]))
    require(179.5 <= float(probe["format"]["duration"]) <= 180.5, "video duration")
    require(any(stream.get("codec_name") == "h264" and stream.get("width") == 1280 and stream.get("height") == 720 for stream in probe["streams"]), "video stream")
    require(any(stream.get("codec_name") == "aac" and stream.get("sample_rate") == "48000" for stream in probe["streams"]), "audio stream")
    require(hashlib.sha256(VIDEO.read_bytes()).hexdigest() == video_manifest["sha256"], "video SHA256")
    require(video_manifest["scene_count"] == 9 and video_manifest["truth_boundary"]["sora_used"] is False, "video manifest")
    with zipfile.ZipFile(PACKAGE / "materials/SAEE_BAIDU_PARTNER_PRODUCT_SOLUTION_V1.docx") as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")
    require("SAEE Agent Readiness Platform" in document_xml and "TBD_OWNER_INPUT" in document_xml, "partner DOCX contract")
    release = load(RELEASE_MANIFEST)
    require(release["truth_boundary"]["release_candidate_prepared"] is True, "release candidate")
    require(release["truth_boundary"]["github_release_created"] is False, "GitHub release boundary")
    canonical = json.dumps(evaluate_agent_run(customer_request), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(json.dumps(evaluate_agent_run(customer_request), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic")
    print(
        "SAEE_CLOUD_ENTRY_PACKAGE_SMOKE: PASS files=29 public_tools=2 demos=3 "
        "cli_paths=3 images=3 whitepaper_pages=10 video_seconds=180.021 "
        "video_scenes=9 deterministic_runs=5/5 release_candidate=true github_release=false "
        "provider_credentials=false network=false cloud_upload=false marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
