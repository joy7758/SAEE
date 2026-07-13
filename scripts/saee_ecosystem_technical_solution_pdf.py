#!/usr/bin/env python3
"""Build the ten-page platform-neutral SAEE ecosystem technical solution PDF."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/SAEE_Agent_Readiness_Capability_Technical_Solution_v2.0.pdf"
MANIFEST = ROOT / "output/pdf/SAEE_Agent_Readiness_Capability_Technical_Solution_v2.0.manifest.json"
FONT_PATH = Path("/System/Library/Fonts/STHeiti Medium.ttc")
PAGE_SIZE = landscape(A4)
WIDTH, HEIGHT = PAGE_SIZE

INK = colors.HexColor("#10231f")
MUTED = colors.HexColor("#52645f")
GREEN = colors.HexColor("#0f7b63")
LIGHT = colors.HexColor("#edf6f2")
LINE = colors.HexColor("#cbdcd5")
AMBER = colors.HexColor("#c78315")
RED = colors.HexColor("#ad3c3c")


PAGES = [
    {
        "title": "Agent 执行能力已经成熟，行动证据仍然缺位",
        "kicker": "01 / AGENT RISK PROBLEM",
        "lead": "代码完成、工具调用成功或任务结束，都不自动等于可以进入真实世界。",
        "bullets": ["测试证据是否充分", "是否存在可执行的回滚方案", "权限边界是否明确", "高影响动作是否经过独立授权"],
        "boundary": "SAEE 评估证据覆盖，不执行部署。",
    },
    {
        "title": "现有工具之间，缺少一层可调用的就绪判断",
        "kicker": "02 / SOLUTION GAP",
        "lead": "Observability、Policy、Authorization 与 Sandbox 各有职责；SAEE 不替代它们。",
        "bullets": ["Observability：说明发生了什么", "Policy：表达规则", "Authorization：决定谁可以做什么", "SAEE：说明当前证据还缺什么"],
        "boundary": "评估结果是决策上下文，不是授权结论。",
    },
    {
        "title": "SAEE Agent Readiness Capability",
        "kicker": "03 / POSITIONING",
        "lead": "所有 Agent 平台在高影响行动前都可调用的一层只读就绪评估能力。",
        "bullets": ["不争夺 Agent 平台", "不做 Audit SDK 或治理工具", "不新增协议或 Runtime", "复用 Digital Biosphere Evolution Engine 的证据与选择子系统"],
        "boundary": "中文冻结名：SAEE 智能体就绪评估能力。",
    },
    {
        "title": "一个 Runtime，多个平台 Adapter",
        "kicker": "04 / ARCHITECTURE",
        "lead": "平台分支只负责发现与调用；评估逻辑保持单一真源。",
        "flow": ["Agent Platform", "MCP / HTTP Adapter", "Two-tool SAEE Runtime", "Readiness Receipt", "Authorized Decision"],
        "boundary": "未知代码、外部仓库、权限扩张和外部执行均不进入链路。",
    },
    {
        "title": "冻结两个公共操作",
        "kicker": "05 / STABLE OPERATIONS",
        "lead": "工具描述、schema、示例和结果边界同时面向编码、检索与引用智能体。",
        "cards": [
            ("saee.evaluate_agent_run", "输入声明的 Agent Trace 与执行证据，输出 readiness、risk 与 missing_evidence。"),
            ("saee.evaluate_evidence", "输入证据包与必需类型，输出 coverage、reason codes 与 missing_evidence。"),
        ],
        "boundary": "describe_saee、compare_observed_traces、rehearse_agent 均不公开。",
    },
    {
        "title": "Qoder Demo：代码完成，不等于可以上线",
        "kicker": "06 / QODER DEMO",
        "lead": "本地 Qoder 格式配置发现 SAEE；兼容客户端调用 coding-release 场景。",
        "flow": ["Code changed", "Tests passed", "Call SAEE", "Rollback + approval missing", "REPLAN"],
        "boundary": "score=50 是证据覆盖率；Qoder 进程尚未实际运行。",
    },
    {
        "title": "五条 Adapter 分支，共用同一能力契约",
        "kicker": "07 / PLATFORM BRANCHES",
        "lead": "Qoder first，但不把配置模板夸大为平台互操作或官方集成。",
        "bullets": ["Qoder：项目级 .mcp.json + 本地协议兼容测试", "Qianfan：两工具适配 + 受控真实 provider 合成回执", "Claude Code：项目级 MCP 模板", "LangChain / CrewAI：官方 MCP 配置模板，Runtime 未测"],
        "boundary": "平台名称只表示组合目标，不表示认可、合作或上架。",
    },
    {
        "title": "Truth boundaries 是产品契约的一部分",
        "kicker": "08 / SAFETY AND TRUTH",
        "lead": "每个结果都保留可机器检查的非授权与非生产边界。",
        "bullets": ["customer_data_used=false", "trace_authenticity_verified=false", "deployment_authorized=false", "official_platform_integration=false", "production_ready=false"],
        "boundary": "The organism may observe the world, but it may not execute the world.",
    },
    {
        "title": "180 天：从本地契约走向受控生态证据",
        "kicker": "09 / EXECUTION ROUTE",
        "lead": "每一阶段以可验证 exit evidence 结束，不按时间自动升级。",
        "timeline": [("0-30", "产品与接口冻结"), ("30-90", "Qoder-first 平台适配"), ("90-150", "生态技术验证"), ("150-180", "插件或云市场入口")],
        "boundary": "伙伴申请不等于技术交流；技术交流不等于伙伴关系。",
    },
    {
        "title": "成功标准：外部证据，而不是更多架构",
        "kicker": "10 / KPI AND NEXT DECISIONS",
        "lead": "技术包已本地就绪；生态与商业 KPI 必须由独立外部回执证明。",
        "bullets": ["技术：MCP、Qoder Adapter、Qianfan Adapter、OpenAPI", "生态：2 次技术交流、1 次生态展示、3 个外部开发者测试", "商业：1 个 Design Partner、1 个联合方案草案", "停止：新协议、新 Runtime、新治理模块、更多架构论文"],
        "boundary": "当前仍为 conditional；Marketplace 与 production 均为 false。",
    },
]


def draw_header(pdf: canvas.Canvas, page_no: int, page: dict) -> None:
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(GREEN)
    pdf.roundRect(44, HEIGHT - 68, 172, 25, 12, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("SAEEZH", 9)
    pdf.drawString(56, HEIGHT - 59, page["kicker"])
    pdf.setFillColor(MUTED)
    pdf.drawRightString(WIDTH - 44, HEIGHT - 58, f"SAEE ECOSYSTEM CAPABILITY · v2.0 · {page_no:02d}/10")
    pdf.setStrokeColor(LINE)
    pdf.line(44, 45, WIDTH - 44, 45)
    pdf.setFillColor(MUTED)
    pdf.setFont("SAEEZH", 8)
    pdf.drawString(44, 29, "local capability package · no authorization · no official platform integration")


def draw_title(pdf: canvas.Canvas, page: dict) -> float:
    pdf.setFillColor(INK)
    pdf.setFont("SAEEZH", 24)
    pdf.drawString(48, HEIGHT - 118, page["title"])
    pdf.setFillColor(MUTED)
    pdf.setFont("SAEEZH", 12)
    pdf.drawString(50, HEIGHT - 150, page["lead"])
    return HEIGHT - 190


def draw_bullets(pdf: canvas.Canvas, bullets: list[str], y: float) -> None:
    for index, text in enumerate(bullets, start=1):
        box_y = y - (index - 1) * 58
        pdf.setFillColor(LIGHT)
        pdf.roundRect(58, box_y - 34, WIDTH - 116, 44, 10, fill=1, stroke=0)
        pdf.setFillColor(GREEN)
        pdf.circle(78, box_y - 12, 11, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont("SAEEZH", 8)
        pdf.drawCentredString(78, box_y - 15, str(index))
        pdf.setFillColor(INK)
        pdf.setFont("SAEEZH", 12)
        pdf.drawString(100, box_y - 17, text)


def draw_flow(pdf: canvas.Canvas, flow: list[str], y: float) -> None:
    box_width = 124
    gap = 23
    start = (WIDTH - (len(flow) * box_width + (len(flow) - 1) * gap)) / 2
    for index, label in enumerate(flow):
        x = start + index * (box_width + gap)
        pdf.setFillColor(GREEN if index in (0, len(flow) - 1) else LIGHT)
        pdf.roundRect(x, y - 48, box_width, 72, 12, fill=1, stroke=0)
        pdf.setFillColor(colors.white if index in (0, len(flow) - 1) else INK)
        pdf.setFont("SAEEZH", 9)
        words = label.split(" ")
        if len(words) > 2:
            pdf.drawCentredString(x + box_width / 2, y - 5, " ".join(words[:2]))
            pdf.drawCentredString(x + box_width / 2, y - 20, " ".join(words[2:]))
        else:
            pdf.drawCentredString(x + box_width / 2, y - 13, label)
        if index < len(flow) - 1:
            pdf.setFillColor(AMBER)
            pdf.setFont("Helvetica-Bold", 17)
            pdf.drawCentredString(x + box_width + gap / 2, y - 15, ">")


def draw_cards(pdf: canvas.Canvas, cards: list[tuple[str, str]], y: float) -> None:
    card_width = (WIDTH - 132) / 2
    for index, (title, body) in enumerate(cards):
        x = 50 + index * (card_width + 32)
        pdf.setFillColor(LIGHT)
        pdf.roundRect(x, y - 130, card_width, 150, 14, fill=1, stroke=0)
        pdf.setFillColor(GREEN)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x + 20, y - 12, title)
        pdf.setFillColor(INK)
        pdf.setFont("SAEEZH", 11)
        parts = wrap_text(body, card_width - 40, "SAEEZH", 11)
        for row, part in enumerate(parts):
            pdf.drawString(x + 20, y - 48 - row * 22, part)


def wrap_text(text: str, max_width: float, font_name: str, font_size: float) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_.:-]+|\s+|.", text)
    lines: list[str] = []
    current = ""
    for token in tokens:
        candidate = current + token
        if current and pdfmetrics.stringWidth(candidate, font_name, font_size) > max_width:
            lines.append(current.rstrip())
            current = token.lstrip()
        else:
            current = candidate
    if current.strip():
        lines.append(current.rstrip())
    return lines


def draw_timeline(pdf: canvas.Canvas, timeline: list[tuple[str, str]], y: float) -> None:
    pdf.setStrokeColor(GREEN)
    pdf.setLineWidth(4)
    pdf.line(90, y, WIDTH - 90, y)
    step = (WIDTH - 180) / (len(timeline) - 1)
    for index, (window, label) in enumerate(timeline):
        x = 90 + index * step
        pdf.setFillColor(GREEN)
        pdf.circle(x, y, 10, fill=1, stroke=0)
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(x, y + 30, window)
        pdf.setFont("SAEEZH", 10)
        pdf.drawCentredString(x, y - 35, label)


def draw_boundary(pdf: canvas.Canvas, text: str) -> None:
    pdf.setFillColor(colors.HexColor("#fff4e3"))
    pdf.roundRect(58, 72, WIDTH - 116, 46, 10, fill=1, stroke=0)
    pdf.setFillColor(AMBER if "false" not in text else RED)
    pdf.setFont("SAEEZH", 10)
    pdf.drawCentredString(WIDTH / 2, 90, text)


def build() -> Path:
    if not FONT_PATH.is_file():
        raise SystemExit(f"missing font: {FONT_PATH}")
    pdfmetrics.registerFont(TTFont("SAEEZH", str(FONT_PATH)))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=PAGE_SIZE, pageCompression=1)
    pdf.setTitle("SAEE Agent Readiness Capability Technical Solution v2.0")
    pdf.setAuthor("山西游骑兵电子商务有限公司")
    for page_no, page in enumerate(PAGES, start=1):
        draw_header(pdf, page_no, page)
        y = draw_title(pdf, page)
        if "flow" in page:
            draw_flow(pdf, page["flow"], y - 35)
        elif "cards" in page:
            draw_cards(pdf, page["cards"], y)
        elif "timeline" in page:
            draw_timeline(pdf, page["timeline"], y - 70)
        else:
            draw_bullets(pdf, page["bullets"], y)
        draw_boundary(pdf, page["boundary"])
        pdf.showPage()
    pdf.save()
    page_count = len(PdfReader(str(OUTPUT)).pages)
    if page_count != 10:
        raise SystemExit(f"expected 10 pages, got {page_count}")
    manifest = {
        "artifact": str(OUTPUT.relative_to(ROOT)),
        "source": "docs/ecosystem/SAEE_AGENT_READINESS_CAPABILITY_TECHNICAL_SOLUTION_V2.md",
        "page_count": page_count,
        "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "truth_boundary": {
            "local_generated": True,
            "official_platform_solution": False,
            "joint_solution_confirmed": False,
            "marketplace_listed": False,
            "production_ready": False,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(build())
