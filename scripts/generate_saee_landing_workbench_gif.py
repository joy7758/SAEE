#!/usr/bin/env python3
"""Generate the Chinese SAEE landing workbench animation.

This creates a local visual asset only. It does not call external services,
modify the backend/runtime/kernel/API schema, or expose private core logic.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/landing/assets/saee-interface-operation-demo.gif"

W, H = 1280, 760
FRAME_COUNT = 34

INK = "#101513"
TEXT = "#1f241f"
MUTED = "#626861"
LINE = "#deddd5"
SURFACE = "#ffffff"
SOFT = "#fbfaf6"
PRIMARY = "#147a64"
PRIMARY_DARK = "#0f5f50"
PRIMARY_SOFT = "#e8f3ef"
SLATE = "#697068"
SLATE_LIGHT = "#d5d8d2"
RISK = "#9b6a20"
RISK_SOFT = "#fff7e8"


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
    ]
    for path in candidates:
        if not Path(path).exists():
            continue
        for index in ([1, 0, 2, 3] if weight == "bold" else [0, 1, 2, 3]):
            try:
                return ImageFont.truetype(path, size=size, index=index)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


F = {
    "brand": font(26, "bold"),
    "title": font(21, "bold"),
    "sub": font(13),
    "tiny": font(11),
    "body": font(14),
    "body_bold": font(14, "bold"),
    "metric": font(26, "bold"),
    "score": font(34, "bold"),
    "button": font(16, "bold"),
}


def ease(x: float) -> float:
    return 1 - (1 - x) * (1 - x)


def clamp(x: float, lo: float = 0, hi: float = 1) -> float:
    return max(lo, min(hi, x))


def round_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def line_chart(draw: ImageDraw.ImageDraw, box, color, progress: float, phase: float, width: int = 3):
    x0, y0, x1, y1 = box
    pts = []
    steps = 34
    for i in range(steps):
        t = i / (steps - 1)
        trend = 0.72 - 0.2 * t + 0.04 * math.sin(t * 7 + phase)
        y = y0 + (1 - trend) * (y1 - y0)
        x = x0 + t * (x1 - x0)
        pts.append((x, y))
    visible = max(2, int(len(pts) * progress))
    draw.line(pts[:visible], fill=color, width=width, joint="curve")


def survival_chart(draw: ImageDraw.ImageDraw, box, progress: float):
    x0, y0, x1, y1 = box
    grid = "#e9ebe6"
    draw.rectangle(box, fill=SURFACE, outline=LINE)
    for i in range(1, 4):
        y = y0 + i * (y1 - y0) / 4
        draw.line([(x0, y), (x1, y)], fill=grid, width=1)
    for i in range(1, 5):
        x = x0 + i * (x1 - x0) / 5
        draw.line([(x, y0), (x, y1)], fill=grid, width=1)
    colors = [PRIMARY, "#6f9f8f", SLATE, SLATE_LIGHT, RISK]
    rates = [0.52, 0.64, 0.82, 1.15, 1.55]
    for idx, (color, rate) in enumerate(zip(colors, rates)):
        pts = []
        for i in range(70):
            t = i / 69
            val = math.exp(-rate * t) + 0.015 * math.sin(t * 28 + idx)
            val = clamp(val, 0.02, 1)
            pts.append((x0 + t * (x1 - x0), y0 + (1 - val) * (y1 - y0)))
        visible = max(3, int(len(pts) * progress))
        draw.line(pts[:visible], fill=color, width=3)


def draw_logo(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, fill=PRIMARY):
    round_rect(draw, (x, y, x + size, y + size), 10, fill=PRIMARY_SOFT, outline="#c9ddd6")
    cx, cy = x + size / 2, y + size / 2
    r = size * 0.29
    pts = []
    for i in range(6):
        a = math.pi / 6 + i * math.pi / 3
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.line(pts + [pts[0]], fill=fill, width=3)
    draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=fill)


def draw_header(draw: ImageDraw.ImageDraw, p: float):
    round_rect(draw, (0, 0, W, 70), 0, fill=SURFACE)
    draw.line((0, 70, W, 70), fill=LINE, width=1)
    draw_logo(draw, 26, 16, 38)
    draw.text((74, 14), "SAEE 工作台", font=F["brand"], fill=TEXT)
    draw.text((75, 43), "多方案长期稳定性评测", font=F["sub"], fill=MUTED)
    round_rect(draw, (285, 12, 570, 58), 8, fill=SURFACE, outline="#deddd5")
    draw.text((306, 18), "场景", font=F["tiny"], fill=MUTED)
    draw.text((306, 35), "上线前 AI 方案选择", font=F["body_bold"], fill=TEXT)
    draw.text((548, 29), "⌄", font=F["body_bold"], fill=SLATE)
    run_fill = INK if p < 0.72 else PRIMARY
    round_rect(draw, (592, 12, 720, 58), 8, fill=run_fill)
    draw.text((625, 24), "▶ 开始评测", font=F["button"], fill=SURFACE)
    round_rect(draw, (815, 12, 1086, 58), 8, fill=SURFACE, outline="#deddd5")
    draw.text((846, 26), "搜索方案、曲线、风险...", font=F["body"], fill="#8a8f86")
    draw.text((1135, 25), "提醒", font=F["body"], fill="#565b54")
    round_rect(draw, (1190, 14, 1238, 56), 21, fill="#f1f2ee")
    draw.text((1204, 25), "SA", font=F["body_bold"], fill="#30342f")


def draw_sidebar(draw: ImageDraw.ImageDraw, p: float):
    x, y, w, h = 20, 88, 240, 585
    round_rect(draw, (x, y, x + w, y + h), 10, fill=SURFACE, outline=LINE)
    draw.text((x + 18, y + 18), "候选方案", font=F["title"], fill=TEXT)
    draw.text((x + 18, y + 48), "同一任务，公平比较", font=F["sub"], fill=MUTED)
    agents = [
        ("方案 A", "客服助手 v2.3", "波动中", 0.62, RISK),
        ("方案 B", "流程助手 Pro", "更稳定", 0.82, PRIMARY),
        ("方案 C", "检索助手 1.7", "需观察", 0.71, SLATE),
        ("方案 D", "自动回复模型", "易失误", 0.46, "#9aa19a"),
        ("方案 E", "保守规则版", "稳定但慢", 0.58, "#4d5751"),
    ]
    for i, (name, desc, status, score, color) in enumerate(agents):
        top = y + 82 + i * 92
        selected = name == "方案 B" and p > 0.58
        outline = PRIMARY if selected else LINE
        fill = PRIMARY_SOFT if selected else SURFACE
        round_rect(draw, (x + 14, top, x + w - 14, top + 76), 9, fill=fill, outline=outline, width=2 if selected else 1)
        draw_logo(draw, x + 27, top + 18, 38, fill=color)
        draw.text((x + 76, top + 14), name, font=F["body_bold"], fill=TEXT)
        draw.text((x + 76, top + 37), desc, font=F["tiny"], fill=MUTED)
        draw.ellipse((x + 76, top + 58, x + 84, top + 66), fill=color)
        draw.text((x + 90, top + 54), status, font=F["tiny"], fill=color)
        draw.text((x + w - 64, top + 16), f"{score:.2f}", font=F["body_bold"], fill=TEXT)
        line_chart(draw, (x + w - 92, top + 46, x + w - 26, top + 64), color, clamp(p * 1.2), i)


def draw_main(draw: ImageDraw.ImageDraw, p: float):
    x, y, w, h = 282, 88, 620, 585
    round_rect(draw, (x, y, x + w, y + h), 10, fill=SURFACE, outline=LINE)
    draw.text((x + 18, y + 18), "稳定性对比", font=F["title"], fill=TEXT)
    draw.text((x + 18, y + 48), "看长期表现，不只看第一次成功", font=F["sub"], fill=MUTED)
    cards = [
        ("方案 B", "更稳", "0.82", PRIMARY),
        ("方案 C", "可继续", "0.71", SLATE),
        ("方案 A", "波动中", "0.62", RISK),
    ]
    for i, (name, label, score, color) in enumerate(cards):
        cx = x + 18 + i * 194
        cy = y + 82
        card_fill = PRIMARY_SOFT if i == 0 else SOFT if i == 1 else RISK_SOFT
        round_rect(draw, (cx, cy, cx + 176, cy + 108), 9, fill=card_fill, outline=color)
        draw.text((cx + 14, cy + 13), label, font=F["body_bold"], fill=color)
        draw.text((cx + 14, cy + 38), name, font=F["sub"], fill="#565b54")
        draw.text((cx + 14, cy + 62), score, font=F["metric"], fill=TEXT)
        line_chart(draw, (cx + 82, cy + 62, cx + 158, cy + 92), color, clamp((p - 0.08) * 1.3), i + 1, 2)
    stats_y = y + 208
    stats = [("评测轮次", "120"), ("候选方案", "5"), ("当前步数", f"{int(1240 * p):,}"), ("数据点", f"{round(2.4 * p, 1)}万")]
    round_rect(draw, (x + 18, stats_y, x + w - 18, stats_y + 64), 9, fill=SURFACE, outline=LINE)
    for i, (k, v) in enumerate(stats):
        sx = x + 42 + i * 142
        draw.text((sx, stats_y + 12), k, font=F["tiny"], fill=MUTED)
        draw.text((sx, stats_y + 31), v, font=F["body_bold"], fill=PRIMARY)
    chart_y = y + 300
    draw.text((x + 18, chart_y - 28), "生存曲线", font=F["body_bold"], fill=TEXT)
    survival_chart(draw, (x + 18, chart_y, x + w - 18, chart_y + 190), clamp((p - 0.18) * 1.3))
    bar_y = chart_y + 218
    draw.text((x + 18, bar_y - 22), "收敛 / 发散观察", font=F["body_bold"], fill=TEXT)
    for i in range(86):
        t = i / 85
        if t > p:
            col = "#f2f3f5"
        else:
            col = [PRIMARY, "#b8d2c8", RISK, "#d7dad4"][int((math.sin(i * 1.7) + 1) * 1.8) % 4]
        bx = x + 18 + i * 6.7
        draw.rounded_rectangle((bx, bar_y, bx + 3, bar_y + 34), 1, fill=col)


def draw_right(draw: ImageDraw.ImageDraw, p: float):
    x, y, w, h = 922, 88, 338, 585
    round_rect(draw, (x, y, x + w, y + h), 10, fill=SURFACE, outline=LINE)
    draw.text((x + 18, y + 18), "推荐结果", font=F["title"], fill=TEXT)
    rows = [("1", "方案 B", "0.82", "建议继续试", PRIMARY), ("2", "方案 C", "0.71", "可备选", SLATE), ("3", "方案 A", "0.62", "先别上", RISK)]
    for i, (rank, name, score, label, color) in enumerate(rows):
        top = y + 62 + i * 48
        fill = PRIMARY_SOFT if i == 0 and p > 0.6 else SURFACE
        outline = PRIMARY if i == 0 and p > 0.6 else "#e7e8ed"
        round_rect(draw, (x + 16, top, x + w - 16, top + 40), 7, fill=fill, outline=outline)
        draw.ellipse((x + 26, top + 10, x + 46, top + 30), fill=color)
        draw.text((x + 32, top + 12), rank, font=F["tiny"], fill=SURFACE)
        draw.text((x + 58, top + 10), name, font=F["body_bold"], fill=TEXT)
        draw.text((x + 172, top + 10), score, font=F["body_bold"], fill=TEXT)
        draw.text((x + 232, top + 10), label, font=F["tiny"], fill=color)
    rec_y = y + 230
    outline = PRIMARY if p > 0.58 else LINE
    round_rect(draw, (x + 16, rec_y, x + w - 16, rec_y + 210), 10, fill=SURFACE, outline=outline, width=2 if p > 0.58 else 1)
    draw.text((x + 34, rec_y + 18), "部署建议", font=F["body_bold"], fill=TEXT)
    draw_logo(draw, x + 34, rec_y + 56, 52, PRIMARY)
    draw.text((x + 102, rec_y + 58), "方案 B", font=F["title"], fill=TEXT)
    draw.text((x + 102, rec_y + 86), "更稳，可以继续试", font=F["body"], fill=MUTED)
    draw.text((x + 238, rec_y + 56), "0.82", font=F["score"], fill=PRIMARY)
    reasons = ["多轮后变化更小", "突然失败风险更低", "适合进入下一轮评审"]
    for i, text in enumerate(reasons):
        yy = rec_y + 128 + i * 24
        draw.ellipse((x + 36, yy + 3, x + 48, yy + 15), fill=PRIMARY_SOFT)
        draw.text((x + 39, yy), "✓", font=F["tiny"], fill=PRIMARY)
        draw.text((x + 56, yy - 1), text, font=F["sub"], fill="#565b54")
    round_rect(draw, (x + 16, y + h - 80, x + w - 16, y + h - 36), 8, fill=INK if p <= 0.65 else PRIMARY)
    draw.text((x + 100, y + h - 67), "查看完整报告", font=F["button"], fill=SURFACE)


def draw_status_toast(draw: ImageDraw.ImageDraw, p: float):
    if p < 0.08:
        return
    x, y = 948, 238
    alpha = clamp((p - 0.08) * 3)
    fill = tuple(int(44 * alpha + 255 * (1 - alpha)) for _ in range(3))
    round_rect(draw, (x, y, x + 260, y + 120), 12, fill=fill)
    draw.text((x + 24, y + 22), "正在做什么", font=F["title"], fill="#ffffff")
    steps = ["放入方案", "多轮试跑", "生成建议"]
    for i, step in enumerate(steps):
        sx = x + 34 + i * 78
        active = p > 0.24 + i * 0.22
        col = "#ffffff" if active else "#9aa49e"
        draw.ellipse((sx, y + 72, sx + 18, y + 90), fill=col)
        if i < 2:
            draw.line((sx + 24, y + 81, sx + 58, y + 81), fill="#9aa49e", width=4)
        draw.text((sx - 8, y + 94), step, font=F["tiny"], fill="#ffffff")


def make_frame(idx: int) -> Image.Image:
    p = ease(idx / (FRAME_COUNT - 1))
    im = Image.new("RGB", (W, H), "#f7f6f2")
    bg = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(bg)
    for y in range(H):
        r = int(251 - y * 0.004)
        g = int(250 - y * 0.005)
        b = int(246 - y * 0.006)
        draw.line((0, y, W, y), fill=(r, g, b))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((720, 40, 1380, 700), fill=(210, 226, 218, 44))
    gd.ellipse((590, 160, 1240, 720), fill=(232, 229, 220, 26))
    bg = Image.alpha_composite(bg.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(34))).convert("RGB")
    draw = ImageDraw.Draw(bg)
    draw_header(draw, p)
    draw_sidebar(draw, p)
    draw_main(draw, p)
    draw_right(draw, p)
    draw_status_toast(draw, p)
    return bg


def main() -> None:
    frames = [make_frame(i) for i in range(FRAME_COUNT)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=115,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"SAEE_LANDING_WORKBENCH_GIF: PASS path={OUT.relative_to(ROOT)} frames={FRAME_COUNT} size={W}x{H}")


if __name__ == "__main__":
    main()
