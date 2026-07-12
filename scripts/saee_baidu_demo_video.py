#!/usr/bin/env python3
"""Build a deterministic three-minute SAEE Baidu technical demo video."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "cloud-entry-package"
MATERIALS = PACKAGE / "materials"
TMP = ROOT / "tmp/video/saee-baidu-demo-v1"
OUTPUT = ROOT / "output/video/SAEE_Baidu_Cloud_Demo_v1.0.mp4"
MANIFEST = ROOT / "output/video/SAEE_Baidu_Cloud_Demo_v1.0.manifest.json"
SUBTITLES = ROOT / "output/video/SAEE_Baidu_Cloud_Demo_v1.0.zh-CN.srt"
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
SECONDS_PER_SCENE = 20

SCENES = [
    {"id": "01-intro", "title": "SAEE Agent Readiness Platform", "lines": ["让企业 Agent 上线前", "先通过执行证据检查"], "image": "sites/saee-commercial/public/og.png"},
    {"id": "02-risk", "title": "一次跑通，不等于可以上线", "lines": ["测试证据", "回滚方案", "权限边界", "人工审批"]},
    {"id": "03-tools", "title": "两个只读公共操作", "lines": ["saee.evaluate_agent_run", "saee.evaluate_evidence", "评估提供上下文，不授予部署权限"]},
    {"id": "04-architecture", "title": "百度版产品架构", "lines": [], "image": "cloud-entry-package/architecture.png"},
    {"id": "05-customer", "title": "智能客服退款 Agent", "lines": [], "image": "cloud-entry-package/screenshots/customer-service-result.png"},
    {"id": "06-coding", "title": "代码发布 Agent", "lines": [], "image": "cloud-entry-package/screenshots/coding-agent-result.png"},
    {"id": "07-boundary", "title": "评估与授权严格分离", "lines": ["customer_data_used=false", "external_world_actions=0", "deployment_authorized=false", "production_ready=false"]},
    {"id": "08-package", "title": "Cloud Entry Package", "lines": ["30 分钟本地技术审阅", "2 个公共工具", "3 个版本化 Demo", "OpenAPI · MCP · 架构 · FAQ · Validator"]},
    {"id": "09-next", "title": "下一步：受控生态合作验证", "lines": ["真实 Qianfan 产品 roundtrip", "人工审阅 Git Release 与生态材料", "显式授权后再联系百度或提交申请", "marketplace_submission=false"]},
]


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def narration() -> list[str]:
    text = (MATERIALS / "SAEE_BAIDU_DEMO_VIDEO_NARRATION_ZH_V1.txt").read_text(encoding="utf-8").strip()
    parts = []
    current = []
    for line in text.splitlines():
        if line and line[0:2].isdigit() and "-" in line:
            if current:
                parts.append(" ".join(current))
                current = []
        elif line.strip():
            current.append(line.strip())
    if current:
        parts.append(" ".join(current))
    if len(parts) != len(SCENES):
        raise SystemExit(f"expected {len(SCENES)} narration parts, got {len(parts)}")
    return parts


def slide_svg(scene: dict, path: Path) -> None:
    title = html.escape(scene["title"])
    lines = scene["lines"]
    line_nodes = []
    # Keep the body below the title even for the four-line boundary/next slides.
    start = 320
    for index, line in enumerate(lines):
        color = "#2f6feb" if index < 2 else "#526078"
        line_nodes.append(f'<text x="640" y="{start + index * 62}" text-anchor="middle" font-family="PingFang SC, Arial, sans-serif" font-size="32" fill="{color}">{html.escape(line)}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<rect width="1280" height="720" fill="#f7f9fc"/>
<rect x="64" y="58" width="1152" height="604" rx="30" fill="#ffffff" stroke="#d8deea" stroke-width="2"/>
<text x="110" y="118" font-family="PingFang SC, Arial, sans-serif" font-size="18" fill="#2f6feb">SAEE · 百度智能云本地技术 Demo</text>
<text x="640" y="225" text-anchor="middle" font-family="PingFang SC, Arial, sans-serif" font-size="48" font-weight="700" fill="#172033">{title}</text>
{''.join(line_nodes)}
<line x1="110" y1="590" x2="1170" y2="590" stroke="#d8deea" stroke-width="2"/>
<text x="110" y="625" font-family="PingFang SC, Arial, sans-serif" font-size="16" fill="#667085">local_review_alpha · official_qianfan_integration=false · production_ready=false</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def probe_duration(path: Path) -> float:
    completed = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True, check=True)
    return float(completed.stdout.strip())


def build() -> Path:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    narrations = narration()
    segments = []
    scene_receipts = []
    for index, (scene, speech) in enumerate(zip(SCENES, narrations), start=1):
        if scene.get("image"):
            image_path = ROOT / scene["image"]
        else:
            svg = TMP / f"{index:02d}.svg"
            image_path = TMP / f"{index:02d}.png"
            slide_svg(scene, svg)
            run(["rsvg-convert", "-w", "1280", "-h", "720", str(svg), "-o", str(image_path)])
        audio = TMP / f"{index:02d}.aiff"
        run(["say", "-v", "Tingting", "-r", "205", "-o", str(audio), speech])
        narration_seconds = probe_duration(audio)
        if narration_seconds > SECONDS_PER_SCENE - 0.5:
            raise SystemExit(f"narration too long for {scene['id']}: {narration_seconds:.2f}s")
        segment = TMP / f"{index:02d}.mp4"
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(image_path), "-i", str(audio),
            "-filter_complex", f"[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=white,format=yuv420p[v];[1:a]apad=pad_dur={SECONDS_PER_SCENE}[a]",
            "-map", "[v]", "-map", "[a]", "-t", str(SECONDS_PER_SCENE), "-r", "30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(segment),
        ])
        segments.append(segment)
        scene_receipts.append({"scene_id": scene["id"], "duration_seconds": SECONDS_PER_SCENE, "narration_seconds": round(narration_seconds, 3), "visual": str(image_path.relative_to(ROOT)) if image_path.is_relative_to(ROOT) else image_path.name})
    concat = TMP / "concat.txt"
    concat.write_text("".join(f"file '{path.as_posix()}'\n" for path in segments), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(OUTPUT)])
    shutil.copy2(MATERIALS / "SAEE_BAIDU_DEMO_VIDEO_ZH_V1.srt", SUBTITLES)
    duration = probe_duration(OUTPUT)
    if not 179.5 <= duration <= 180.5:
        raise SystemExit(f"unexpected final duration: {duration}")
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    manifest = {
        "video_package_version": "1.0.0",
        "video": str(OUTPUT.relative_to(ROOT)),
        "subtitles": str(SUBTITLES.relative_to(ROOT)),
        "duration_seconds": round(duration, 3),
        "resolution": "1280x720",
        "audio": "local_zh_CN_TTS_no_music",
        "scene_count": len(SCENES),
        "sha256": digest,
        "scenes": scene_receipts,
        "truth_boundary": {
            "local_generated_video": True,
            "sora_used": False,
            "customer_data_used": False,
            "external_world_actions": 0,
            "official_qianfan_integration": False,
            "marketplace_submission": False,
            "customer_validated": False,
            "production_ready": False,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(build())
