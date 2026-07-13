#!/usr/bin/env python3
"""Render the Alibaba Cloud Marketplace SAEE service user guide PDF."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md"
OUTPUT = ROOT / "output/pdf/SAEE_Alibaba_Cloud_Marketplace_Agent_Readiness_Service_User_Guide_v0.1.pdf"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_MEDIUM = "/System/Library/Fonts/STHeiti Medium.ttc"


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(20 * mm, 16 * mm, 190 * mm, 16 * mm)
    canvas.setFont("SAEELight", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(20 * mm, 10 * mm, "SAEE - 阿里云云市场服务使用指南 v0.1")
    canvas.drawRightString(190 * mm, 10 * mm, f"第 {document.page} 页")
    canvas.restoreState()


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "Cover",
            parent=base["Title"],
            fontName="SAEEMedium",
            fontSize=27,
            leading=39,
            textColor=colors.HexColor("#102A43"),
            alignment=TA_CENTER,
            spaceAfter=12 * mm,
        ),
        "cover_sub": ParagraphStyle(
            "CoverSub",
            parent=base["Normal"],
            fontName="SAEELight",
            fontSize=15,
            leading=23,
            textColor=colors.HexColor("#2563EB"),
            alignment=TA_CENTER,
            spaceAfter=11 * mm,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading1"],
            fontName="SAEEMedium",
            fontSize=20,
            leading=29,
            textColor=colors.HexColor("#102A43"),
            spaceAfter=7 * mm,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading2"],
            fontName="SAEEMedium",
            fontSize=13,
            leading=20,
            textColor=colors.HexColor("#2563EB"),
            spaceBefore=3 * mm,
            spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="SAEELight",
            fontSize=10.3,
            leading=18,
            textColor=colors.HexColor("#334E68"),
            alignment=TA_LEFT,
            spaceAfter=3 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="SAEELight",
            fontSize=9.8,
            leading=16.5,
            leftIndent=7 * mm,
            firstLineIndent=-4 * mm,
            textColor=colors.HexColor("#334E68"),
            spaceAfter=1.8 * mm,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["BodyText"],
            fontName="SAEELight",
            fontSize=10,
            leading=18,
            textColor=colors.HexColor("#526D82"),
            alignment=TA_CENTER,
            spaceAfter=2.5 * mm,
        ),
    }


def clean(text: str) -> str:
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    escaped = re.sub(r"`([^`]+)`", r"<font name='SAEEMedium'>\1</font>", escaped)
    return escaped


def render() -> Path:
    pdfmetrics.registerFont(TTFont("SAEELight", FONT_LIGHT, subfontIndex=0))
    pdfmetrics.registerFont(TTFont("SAEEMedium", FONT_MEDIUM, subfontIndex=0))
    pages = SOURCE.read_text(encoding="utf-8").split("<!-- PAGE_BREAK -->")
    if len(pages) != 4:
        raise SystemExit(f"expected 4 pages, got {len(pages)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=21 * mm,
        rightMargin=21 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title="SAEE AI 智能体上线前可靠性评估服务 - 用户使用指南 v0.1",
        author="山西游骑兵电子商务有限公司",
    )
    style = build_styles()
    story = []

    for page_index, page in enumerate(pages):
        lines = page.strip().splitlines()
        if page_index == 0:
            story.extend(
                [
                    Spacer(1, 29 * mm),
                    Paragraph(clean(lines[0].removeprefix("# ")), style["cover"]),
                    Paragraph(clean(lines[2].removeprefix("## ")), style["cover_sub"]),
                    Spacer(1, 7 * mm),
                ]
            )
            for line in lines[3:]:
                if line.startswith("- "):
                    story.append(Paragraph("• " + clean(line[2:]), style["meta"]))
        else:
            buffer: list[str] = []

            def flush() -> None:
                if buffer:
                    story.append(Paragraph(clean(" ".join(buffer)), style["body"]))
                    buffer.clear()

            for raw in lines:
                line = raw.strip()
                if not line:
                    flush()
                elif line.startswith("## "):
                    flush()
                    story.append(Paragraph(clean(line[3:]), style["h2"]))
                elif line.startswith("### "):
                    flush()
                    story.append(Paragraph(clean(line[4:]), style["h3"]))
                elif line.startswith("- "):
                    flush()
                    story.append(Paragraph("• " + clean(line[2:]), style["bullet"]))
                elif re.match(r"^\d+\. ", line):
                    flush()
                    story.append(Paragraph(clean(line), style["bullet"]))
                else:
                    buffer.append(line)
            flush()

        if page_index < len(pages) - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUTPUT


if __name__ == "__main__":
    print(render())
