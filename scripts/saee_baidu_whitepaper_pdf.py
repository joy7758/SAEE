#!/usr/bin/env python3
"""Render the ten-page SAEE Baidu technical whitepaper from Markdown."""

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
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cloud-entry-package/materials/SAEE_BAIDU_TECHNICAL_WHITEPAPER_V1.md"
OUTPUT = ROOT / "output/pdf/SAEE_Baidu_Cloud_Technical_Whitepaper_v1.0.pdf"
PACKAGE = ROOT / "cloud-entry-package"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_MEDIUM = "/System/Library/Fonts/STHeiti Medium.ttc"


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D8DEE8"))
    canvas.line(22 * mm, 16 * mm, 188 * mm, 16 * mm)
    canvas.setFont("SAEELight", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(22 * mm, 10 * mm, "SAEE Agent Readiness Platform - local review alpha")
    canvas.drawRightString(188 * mm, 10 * mm, f"{document.page}")
    canvas.restoreState()


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("Cover", parent=base["Title"], fontName="SAEEMedium", fontSize=30, leading=40, textColor=colors.HexColor("#172033"), alignment=TA_CENTER, spaceAfter=14 * mm),
        "cover_sub": ParagraphStyle("CoverSub", parent=base["Normal"], fontName="SAEELight", fontSize=16, leading=25, textColor=colors.HexColor("#2F6FEB"), alignment=TA_CENTER, spaceAfter=12 * mm),
        "h2": ParagraphStyle("H2", parent=base["Heading1"], fontName="SAEEMedium", fontSize=22, leading=30, textColor=colors.HexColor("#172033"), spaceAfter=9 * mm),
        "h3": ParagraphStyle("H3", parent=base["Heading2"], fontName="SAEEMedium", fontSize=14, leading=21, textColor=colors.HexColor("#2F6FEB"), spaceBefore=4 * mm, spaceAfter=3 * mm),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="SAEELight", fontSize=10.3, leading=18, textColor=colors.HexColor("#344054"), alignment=TA_LEFT, spaceAfter=4 * mm),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName="SAEELight", fontSize=9.7, leading=16, leftIndent=6 * mm, firstLineIndent=-3 * mm, bulletIndent=2 * mm, textColor=colors.HexColor("#344054"), spaceAfter=2 * mm),
        "meta": ParagraphStyle("Meta", parent=base["BodyText"], fontName="SAEELight", fontSize=9.5, leading=17, textColor=colors.HexColor("#667085"), alignment=TA_CENTER, spaceAfter=2 * mm),
    }


def clean(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"<font name='SAEEMedium'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def render() -> Path:
    pdfmetrics.registerFont(TTFont("SAEELight", FONT_LIGHT, subfontIndex=0))
    pdfmetrics.registerFont(TTFont("SAEEMedium", FONT_MEDIUM, subfontIndex=0))
    pages = SOURCE.read_text(encoding="utf-8").split("<!-- PAGE_BREAK -->")
    if len(pages) != 10:
        raise SystemExit(f"expected 10 pages, got {len(pages)}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=22 * mm, bottomMargin=22 * mm, title="SAEE Baidu Cloud Technical Whitepaper v1.0", author="SAEE")
    style = styles()
    story = []
    for page_index, page in enumerate(pages):
        lines = page.strip().splitlines()
        if page_index == 0:
            story.extend([Spacer(1, 28 * mm), Paragraph(clean(lines[0].removeprefix("# ")), style["cover"]), Paragraph(clean(lines[2].removeprefix("## ")), style["cover_sub"]), Spacer(1, 8 * mm)])
            for line in lines[3:]:
                line = line.strip()
                if line.startswith("- "):
                    story.append(Paragraph("• " + clean(line[2:]), style["meta"]))
                elif line:
                    story.append(Paragraph(clean(line), style["meta"]))
        else:
            paragraph_buffer: list[str] = []

            def flush() -> None:
                if paragraph_buffer:
                    story.append(Paragraph(clean(" ".join(paragraph_buffer)), style["body"]))
                    paragraph_buffer.clear()

            for raw in lines:
                line = raw.strip()
                if not line:
                    flush()
                elif line.startswith("## "):
                    flush(); story.append(Paragraph(clean(line[3:]), style["h2"]))
                elif line.startswith("### "):
                    flush(); story.append(Paragraph(clean(line[4:]), style["h3"]))
                elif line.startswith("- "):
                    flush(); story.append(Paragraph("• " + clean(line[2:]), style["bullet"]))
                elif re.match(r"^\d+\. ", line):
                    flush(); story.append(Paragraph(clean(line), style["bullet"]))
                elif line.startswith("[[IMAGE:") and line.endswith("]]" ):
                    flush()
                    relative = line[8:-2]
                    image_path = PACKAGE / relative
                    image = Image(str(image_path))
                    max_width, max_height = 162 * mm, 98 * mm
                    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
                    image.drawWidth = image.imageWidth * scale
                    image.drawHeight = image.imageHeight * scale
                    story.extend([image, Spacer(1, 5 * mm)])
                else:
                    paragraph_buffer.append(line)
            flush()
        if page_index < len(pages) - 1:
            story.append(PageBreak())
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUTPUT


if __name__ == "__main__":
    print(render())
