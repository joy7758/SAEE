#!/usr/bin/env python3
"""Build a deterministic self-explanatory three-minute ecosystem capability demo."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp/video/saee-ecosystem-capability-v2"
OUTPUT = ROOT / "output/video/SAEE_Ecosystem_Capability_Demo_v2.0.mp4"
MANIFEST = ROOT / "output/video/SAEE_Ecosystem_Capability_Demo_v2.0.manifest.json"
SUBTITLES = ROOT / "output/video/SAEE_Ecosystem_Capability_Demo_v2.0.zh-CN.srt"
SECONDS_PER_SCENE = 20

SCENES = [
    {"id": "01-position", "title": "SAEE Agent Readiness Capability", "lines": ["智能体执行真实行动前", "先判断证据是否充分"], "speech": "SAEE 是智能体就绪评估能力。在智能体准备进入真实世界前，先检查现有执行证据是否充分。"},
    {"id": "02-gap", "title": "代码完成，不等于可以上线", "lines": ["测试结果", "回滚方案", "权限边界", "独立审批"], "speech": "代码修改完成或工具调用成功，只说明任务有了结果。测试、回滚、权限和审批证据仍可能缺失。"},
    {"id": "03-tools", "title": "冻结两个只读公共操作", "lines": ["saee.evaluate_agent_run", "saee.evaluate_evidence", "不公开调试工具"], "speech": "SAEE 对外只保留两个操作。一个评估智能体运行，一个评估证据包。内部调试工具不会出现在公共列表。"},
    {"id": "04-qoder-flow", "title": "Qoder + SAEE", "lines": ["修改代码 → 运行测试", "准备部署 → 调用 SAEE", "生成有边界的就绪回执"], "speech": "在 Qoder 场景中，智能体修改代码并运行测试。准备部署时调用 SAEE，获得一份有边界的就绪回执。"},
    {"id": "05-result", "title": "Demo 结果：REPLAN", "lines": ["证据覆盖率 50", "缺少 ROLLBACK_PLAN", "缺少 HUMAN_APPROVAL", "deployment_authorized=false"], "speech": "演示中测试和权限证据已经提供，但回滚方案和人工审批缺失。SAEE 返回 REPLAN，不执行部署。"},
    {"id": "06-branches", "title": "一个 Runtime，五条 Adapter 分支", "lines": ["Qoder · Qianfan · Claude Code", "LangChain · CrewAI", "复用 MCP 与 HTTP 契约"], "speech": "Qoder、千帆、Claude Code、LangChain 和 CrewAI 共用同一个两工具 Runtime，只改变平台配置，不复制评估逻辑。"},
    {"id": "07-boundary", "title": "评估与授权严格分离", "lines": ["trace_authenticity_verified=false", "customer_data_used=false", "official_integration=false", "production_ready=false"], "speech": "SAEE 不验证声明轨迹的真实性，不使用客户数据，不授予权限，也不把本地兼容测试写成官方平台集成。"},
    {"id": "08-route", "title": "180 天生态路线", "lines": ["0-30 产品冻结", "30-90 Qoder-first 适配", "90-150 生态验证", "150-180 插件或市场入口"], "speech": "一百八十天路线分四段。先冻结产品，再做平台适配，然后收集生态证据，最后才讨论插件或云市场入口。"},
    {"id": "09-next", "title": "下一步由外部证据决定", "lines": ["2 次云厂商技术交流", "1 次生态展示", "3 个外部开发者测试", "1 个 Design Partner"], "speech": "本地技术包已经准备。下一步成功与否，要由技术交流、生态展示、外部开发者测试和 Design Partner 回执证明。"},
]


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def timestamp(seconds: int) -> str:
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},000"


def slide_svg(scene: dict, path: Path, index: int) -> None:
    nodes = []
    start = 315
    for row, line in enumerate(scene["lines"]):
        nodes.append(
            f'<text x="640" y="{start + row * 58}" text-anchor="middle" '
            f'font-family="PingFang SC, STHeiti, Arial" font-size="30" '
            f'fill="{("#0f7b63" if row < 2 else "#52645f")}">{html.escape(line)}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">
<rect width="1280" height="720" fill="#edf6f2"/>
<rect x="54" y="44" width="1172" height="632" rx="30" fill="#ffffff" stroke="#cbdcd5" stroke-width="2"/>
<rect x="92" y="82" width="220" height="34" rx="17" fill="#0f7b63"/>
<text x="202" y="105" text-anchor="middle" font-family="Arial" font-size="16" fill="#ffffff">SAEE ECOSYSTEM v2.0</text>
<text x="1180" y="106" text-anchor="end" font-family="Arial" font-size="16" fill="#52645f">{index:02d}/09</text>
<text x="640" y="225" text-anchor="middle" font-family="PingFang SC, STHeiti, Arial" font-size="48" font-weight="700" fill="#10231f">{html.escape(scene["title"])}</text>
{''.join(nodes)}
<line x1="92" y1="610" x2="1188" y2="610" stroke="#cbdcd5" stroke-width="2"/>
<text x="92" y="644" font-family="PingFang SC, STHeiti, Arial" font-size="17" fill="#52645f">read-only · no authorization · no official platform integration · production_ready=false</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def build() -> Path:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    segments = []
    scene_receipts = []
    subtitle_blocks = []
    for index, scene in enumerate(SCENES, start=1):
        svg = TMP / f"{index:02d}.svg"
        image = TMP / f"{index:02d}.png"
        audio = TMP / f"{index:02d}.aiff"
        segment = TMP / f"{index:02d}.mp4"
        slide_svg(scene, svg, index)
        run(["rsvg-convert", "-w", "1280", "-h", "720", str(svg), "-o", str(image)])
        run(["say", "-v", "Tingting", "-r", "205", "-o", str(audio), scene["speech"]])
        narration_seconds = probe_duration(audio)
        if narration_seconds > SECONDS_PER_SCENE - 0.5:
            raise SystemExit(f"narration too long for {scene['id']}: {narration_seconds:.3f}s")
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(image), "-i", str(audio),
            "-filter_complex", f"[0:v]format=yuv420p[v];[1:a]apad=pad_dur={SECONDS_PER_SCENE}[a]",
            "-map", "[v]", "-map", "[a]", "-t", str(SECONDS_PER_SCENE), "-r", "30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
            "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(segment),
        ])
        segments.append(segment)
        scene_receipts.append({"scene_id": scene["id"], "duration_seconds": SECONDS_PER_SCENE, "narration_seconds": round(narration_seconds, 3)})
        start = (index - 1) * SECONDS_PER_SCENE
        subtitle_blocks.append(f"{index}\n{timestamp(start)} --> {timestamp(start + SECONDS_PER_SCENE)}\n{scene['speech']}\n")
    concat = TMP / "concat.txt"
    concat.write_text("".join(f"file '{path.as_posix()}'\n" for path in segments), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(OUTPUT)])
    SUBTITLES.write_text("\n".join(subtitle_blocks), encoding="utf-8")
    duration = probe_duration(OUTPUT)
    if not 179.5 <= duration <= 180.5:
        raise SystemExit(f"unexpected final duration: {duration}")
    manifest = {
        "video_package_version": "2.0.0",
        "video": str(OUTPUT.relative_to(ROOT)),
        "subtitles": str(SUBTITLES.relative_to(ROOT)),
        "duration_seconds": round(duration, 3),
        "resolution": "1280x720",
        "audio": "local_zh_CN_TTS_no_music",
        "scene_count": len(SCENES),
        "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "scenes": scene_receipts,
        "truth_boundary": {
            "self_explanatory_local_demo": True,
            "qoder_process_executed": False,
            "official_platform_integration": False,
            "customer_data_used": False,
            "external_world_actions": 0,
            "marketplace_submission": False,
            "customer_validated": False,
            "production_ready": False,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(build())
